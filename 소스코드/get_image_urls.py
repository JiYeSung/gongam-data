import requests
from bs4 import BeautifulSoup
import json
import time
import sys

BASE_URL = "https://gongamcompany.imweb.me"
LIST_PAGE = BASE_URL + "/gongam-imgdb"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def get_pagination_links():
    """첫 게시판 페이지에서 pagination으로부터 모든 page 링크 추출"""
    res = requests.get(LIST_PAGE, headers=HEADERS)
    if res.status_code != 200:
        print("❌ 첫 페이지 요청 실패")
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    links = set()

    for a in soup.select("ul.pagination a[href]"):
        href = a.get("href")
        if href and "page=" in href and "javascript:;" not in href:
            full_url = BASE_URL + href
            links.add(full_url)

    return sorted(list(links))

def collect_from_page(url, min_count, max_count):
    """개별 페이지에서 조건에 맞는 게시글 수집"""
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    posts = soup.select("ul.li_body.holder")

    result = []

    for post in posts:
        count_el = post.select_one("li.count")
        title_el = post.select_one("a.list_text_title")

        if not count_el or not title_el:
            continue

        try:
            count = int(count_el.text.strip())
        except ValueError:
            continue

        if not (min_count <= count <= max_count):
            continue

        href = title_el.get("href", "")
        title = title_el.text.strip()
        full_url = BASE_URL + href
        result.append({
            "url": full_url,
            "alt_prefix": title,
            "count": count
        })

    return result

def collect_all(min_count=1, max_count=999):
    page_urls = get_pagination_links()
    print(f"🔍 총 {len(page_urls)} 페이지 수집 예정...")

    all_results = []
    for idx, page_url in enumerate(page_urls):
        print(f"📄 {idx + 1}/{len(page_urls)} 페이지 수집 중: {page_url}")
        data = collect_from_page(page_url, min_count, max_count)
        all_results.extend(data)
        time.sleep(0.5)

    return all_results

if __name__ == "__main__":
    min_count = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    max_count = int(sys.argv[2]) if len(sys.argv) > 2 else 999

    results = collect_all(min_count=min_count, max_count=max_count)
    with open("urls_by_pagination.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 수집 완료: {len(results)}개 → urls_by_pagination.json 저장됨")
