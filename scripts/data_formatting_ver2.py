import requests
from bs4 import BeautifulSoup
import json

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
    table_id = table.get("id", "")

    # ✅ 대상 테이블별 prefix
    table_prefixes = {
        "detail-service": "price_table",
        "detail-facilities": "facilities",
        "detail-basic": "info"
    }
    prefix = table_prefixes.get(table_id)

    for tr in table.find_all("tr"):
        tds = tr.find_all(["td", "th"])
        if len(tds) < 2:
            if not is_detail_card:
                continue

        th_or_td = tds[0] if len(tds) > 1 else None
        value_td = tds[1] if len(tds) > 1 else None

        key = value_td.get("id") if value_td else None

        if not key and prefix and th_or_td:
            label = th_or_td.get_text(strip=True)
            if label:
                key = f"{prefix}.{label}"

        if not key or not value_td:
            continue

        value = value_td.get_text(strip=True)

        # ✅ 처리 분기
        if "." in key:
            part1, part2 = key.split(".", 1)

            if part1 == "facilities":
                if "facilities" not in data:
                    data["facilities"] = []
                data["facilities"].append({
                    "name": part2,
                    "active": parse_value(part2, value)
                })

            elif part1 == "price_table":
                if "price_table" not in data:
                    data["price_table"] = []
                data["price_table"].append({
                    "name": part2,
                    "price": parse_value(part2, value)
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

# ✅ 메인 실행 함수
def main():
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        )
    }

    with open("./urls_by_pagination.json", "r", encoding="utf-8") as f:
        url_items = json.load(f)

    url_items.sort(key=lambda x: int(x.get("count", 0)))
    final_result = {}

    for idx, item in enumerate(url_items, start=1):
        url = item["url"]
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            res.raise_for_status()
        except Exception as e:
            print(f"❌ URL 요청 실패: {url} → {e}")
            continue

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

                        thumbnail_url = detail_data.get("thumbnail")
                        if thumbnail_url and not any(img["src"] == thumbnail_url for img in images):
                            images.insert(0, {"src": thumbnail_url, "alt": f"{title} 장지 이미지0"})
                        if not thumbnail_url and images:
                            detail_data["thumbnail"] = images[0]["src"]

                        detail_data["detail_images"] = images

        if "location" not in detail_data:
            detail_data["location"] = {"lat": "", "lng": ""}
        else:
            detail_data["location"].setdefault("lat", "")
            detail_data["location"].setdefault("lng", "")

        required_fields = ["summary", "location", "thumbnail", "detail_images", "info"]
        for field in required_fields:
            if field not in detail_data:
                print(f"⚠️ [누락] {idx:03}번 항목 - '{field}' 필드 없음 → {url}")

        final_result[f"{idx:03}"] = detail_data

    with open("gongam_detail_db_result.json", "w", encoding="utf-8") as f:
        json.dump(final_result, f, ensure_ascii=False, indent=2)

    print("✅ gongam_detail_db_result.json 파일 생성 완료")

if __name__ == "__main__":
    main()
