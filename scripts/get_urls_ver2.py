import requests
from bs4 import BeautifulSoup
import json
import time
import re

BASE_URL = "https://gongamcompany.imweb.me"
LIST_PAGE = BASE_URL + "/gongam-imgdb"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def get_pagination_links():
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

def extract_title_parts(title_text):
    match = re.match(r"(.+?)\s*\((.+?)\)", title_text)
    if match:
        alt_prefix = match.group(1).strip()
        name = match.group(2).strip()
    else:
        alt_prefix = title_text.strip()
        name = title_text.strip()
    return alt_prefix, name

def collect_from_page(url, count_filter_set):
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

        if count_filter_set is not None and count not in count_filter_set:
            continue

        href = title_el.get("href", "")
        title = title_el.text.strip()
        alt_prefix, name = extract_title_parts(title)
        full_url = BASE_URL + href

        result.append({
            "url": full_url,
            "alt_prefix": alt_prefix,
            "name": name,
            "count": count
        })

    return result

def collect_all(count_filter_set=None):
    page_urls = get_pagination_links()
    print(f"🔍 총 {len(page_urls)} 페이지 수집 예정...")

    all_results = []
    for idx, page_url in enumerate(page_urls):
        print(f"📄 {idx + 1}/{len(page_urls)} 페이지 수집 중: {page_url}")
        data = collect_from_page(page_url, count_filter_set)
        all_results.extend(data)
        time.sleep(0.5)

    return all_results

# def get_count_filter_input():
    # user_input = input("🎯 수집할 count 값을 입력하세요 (예: 10-50 / 5 10 23 / [엔터=전체]): ").strip()

    # if not user_input:
    #     return None  # 전체 수집

    # if "-" in user_input:
    #     try:
    #         min_count, max_count = map(int, user_input.split("-"))
    #         return set(range(min_count, max_count + 1))
    #     except:
    #         print("❌ 범위 입력 오류! 예: 10-30")
    #         exit(1)
    # else:
    #     try:
    #         return set(map(int, user_input.split()))
    #     except:
    #         print("❌ 숫자 입력 오류! 예: 5 10 23")
    #         exit(1)
def get_count_filter_input():
    # ✅ 사용자 입력 없이 전체 수집
    return None

if __name__ == "__main__":
    count_filter_set = get_count_filter_input()

    results = collect_all(count_filter_set=count_filter_set)
    with open("urls_by_pagination.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 수집 완료: {len(results)}개 → urls_by_pagination.json 저장됨")
