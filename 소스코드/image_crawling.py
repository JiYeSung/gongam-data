import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# ✅ User-Agent 헤더 (크롤링 차단 우회용)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    )
}

# ✅ 이미지 저장 기본 폴더
BASE_SAVE_DIR = "../../장지 이미지2/downloaded_images"
os.makedirs(BASE_SAVE_DIR, exist_ok=True)

# ✅ 이미지 크롤링 함수 (폴더명 커스터마이징 가능)
def download_images_from_url(url, custom_folder_name=None):
    parsed = urlparse(url)
    domain_folder = custom_folder_name if custom_folder_name else parsed.netloc
    save_path = os.path.join(BASE_SAVE_DIR, domain_folder)
    os.makedirs(save_path, exist_ok=True)

    try:
        response = requests.get(url, timeout=10, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        base_name = parsed.path.strip('/').replace('/', '_') or "index"
        img_urls = set()

        for tag in soup.find_all("img", src=True):
            img_urls.add(urljoin(url, tag['src']))

        for tag in soup.find_all(style=re.compile("background-image")):
            style = tag.get("style", "")
            match = re.search(r"background-image\s*:\s*url\((.*?)\)", style)
            if match:
                img_urls.add(urljoin(url, match.group(1).strip('"\' ')))

        for tag in soup.find_all(attrs={"data-bg": True}):
            match = re.search(r"url\((.*?)\)", tag['data-bg'])
            if match:
                img_urls.add(urljoin(url, match.group(1).strip('"\' ')))

        for tag in soup.find_all(attrs={"data-src": True}):
            img_urls.add(urljoin(url, tag['data-src']))

        for idx, img_url in enumerate(img_urls):
            try:
                img_data = requests.get(img_url, timeout=10, headers=HEADERS).content
                img_ext = os.path.splitext(urlparse(img_url).path)[-1][:5]
                img_name = f"{base_name}_img{idx+1}{img_ext if img_ext else '.jpg'}"
                with open(os.path.join(save_path, img_name), "wb") as f:
                    f.write(img_data)
            except Exception as e:
                print(f"⚠️ 다운로드 실패: {img_url} → {e}")

        print(f"✅ {url} → 저장 완료: {save_path}")

    except Exception as e:
        print(f"❌ {url} → 크롤링 실패: {e}")

# ✅ 대상 URL 및 폴더명 목록
url_list = [
    # ("URL", "폴더이름"),
    ("https://pajupark.com/%EC%B6%94%EB%AA%A8%EA%B3%B5%EC%9B%90%EC%86%8C%EA%B0%9C", "파주추모공원"),
]

# ✅ 실행
for url, folder_name in url_list:
    if url.strip():
        download_images_from_url(url, folder_name)
