import requests
from bs4 import BeautifulSoup
import json

# ✅ 크롤링할 URL 리스트
URLS = [
    "https://gongamcompany.imweb.me/gongam-imgdb/?bmode=view&idx=164899277&back_url=&t=board&page=1"
]

# ✅ User-Agent 헤더
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    )
}

# ✅ 값 파싱 함수
def parse_value(key, value):
    value = value.strip()
    if value == "Y":
        return True
    if value == "N":
        return False
    if key == "types":
        return [v.strip() for v in value.split(",") if v.strip()]
    return value

# ✅ 테이블 데이터 추출 함수
def extract_table_data(table, is_detail_card=False):
    data = {}
    prefix = None
    table_id = table.get("id", "")
    if table_id == "detail-service":
        prefix = "price_table"
    elif table_id == "detail-facilities":
        prefix = "facilities"

    for tr in table.find_all("tr"):
        tds = tr.find_all(["td", "th"])
        if len(tds) < 2:
            if not is_detail_card:
                continue

        # ✅ <td><td> 구조 대응
        th = tds[0] if len(tds) > 1 else None
        td = tds[1] if len(tds) > 1 else None

        key = (td.get("id") if td else None)
        if not key and prefix:
            label = (th or td).get_text(strip=True)
            key = f"{prefix}.{label}"
        if not key:
            continue

        value = td.get_text(strip=True) if td else ""

        # ✅ facilities는 리스트 형태로 가공
        if "." in key:
            part1, part2 = key.split(".", 1)
            if part1 == "facilities":
                if "facilities" not in data:
                    data["facilities"] = []
                data["facilities"].append({
                    "name": part2,
                    "active": parse_value(part2, value)
                })
            else:
                if part1 not in data:
                    data[part1] = {}
                data[part1][part2] = parse_value(part2, value)
        else:
            data[key] = parse_value(key, value)
    return data

# ✅ 이미지 src + alt 추출 함수
def extract_images(td_tag, title_prefix):
    images = []
    for i, img in enumerate(td_tag.find_all("img"), 1):
        src = img.get("data-src") or img.get("src")
        alt = f"{title_prefix} 장지 이미지{i}"
        if src:
            images.append({"src": src, "alt": alt})
    return images

# ✅ 전체 처리 결과
final_result = {}

for i, url in enumerate(URLS, start=1):
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    detail_data = {}
    title = ""

    for table in soup.select("div.board_txt_area table"):
        table_id = table.get("id", "")
        is_detail_card = (table_id == "detail-card")
        extracted = extract_table_data(table, is_detail_card)
        if table_id == "detail-head":
            title = extracted.get("summary", {}).get("title", "")
        detail_data.update(extracted)

        if table_id == "detail-images":
            for tr in table.find_all("tr"):
                td = tr.find("td")
                if not td:
                    continue
                td_id = td.get("id")
                if td_id == "thumbnail":
                    images = extract_images(td, title)
                    detail_data["thumbnail"] = images[0]["src"] if images else ""
                elif td_id == "detail_images":
                    images = extract_images(td, title)
                    detail_data["detail_images"] = images

    # ✅ location 누락 방지
    if "location" not in detail_data:
        detail_data["location"] = {"lat": "", "lng": ""}
    else:
        detail_data["location"].setdefault("lat", "")
        detail_data["location"].setdefault("lng", "")

    final_result[f"{i:03}"] = detail_data

# ✅ JSON 파일로 저장
with open("gongam_detail_db_result.json", "w", encoding="utf-8") as f:
    json.dump(final_result, f, ensure_ascii=False, indent=2)

print("✅ gongam_detail_db_result.json 파일 생성 완료")
