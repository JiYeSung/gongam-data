import requests
from bs4 import BeautifulSoup
import json
import os

def extract_image_data(url, alt_prefix):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        container = soup.select_one('.board_txt_area')

        if not container:
            print(f"❌ [SKIP] '.board_txt_area' not found in: {url}")
            return None

        images = container.find_all('img')
        src_list = [img.get('src') or img.get('data-src') for img in images if img.get('src') or img.get('data-src')]

        if not src_list:
            return None

        thumbnail = src_list[0]
        detail_images = [
            {"src": src, "alt": f"{alt_prefix} 장지 이미지 {idx + 1}"}
            for idx, src in enumerate(src_list)
        ]

        return {
            "thumbnail": thumbnail,
            "detail_images": detail_images
        }

    except Exception as e:
        print(f"❌ [ERROR] {url} 에서 오류 발생: {e}")
        return None

def main():
    # ✅ 자동 수집된 URL 목록 로딩
    urls_file = "urls_by_pagination.json"  # 경로 조정 가능
    with open(urls_file, "r", encoding="utf-8") as f:
        urls = json.load(f)

    # ✅ 저장 경로 설정
    output_dir = "../images_update_data"
    os.makedirs(output_dir, exist_ok=True)

    # ✅ 각 URL에서 이미지 추출 후 JSON 저장
    for item in urls:
        print(f"\n🌐 처리 중: {item['url']}")
        result = extract_image_data(item['url'], item['alt_prefix'])
        if result:
            filename = os.path.join(output_dir, f"{item['alt_prefix']}.json")
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"✅ 저장 완료: {filename}")
        else:
            print("⚠️  이미지 데이터 없음. 저장되지 않음.")

if __name__ == "__main__":
    main()
