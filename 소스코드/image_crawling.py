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
BASE_SAVE_DIR = "downloaded_images"
os.makedirs(BASE_SAVE_DIR, exist_ok=True)

# ✅ 이미지 크롤링 함수
def download_images_from_url(url):
    parsed = urlparse(url)
    domain_folder = parsed.netloc
    save_path = os.path.join(BASE_SAVE_DIR, domain_folder)
    os.makedirs(save_path, exist_ok=True)

    try:
        response = requests.get(url, timeout=10, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        base_name = parsed.path.strip('/').replace('/', '_') or "index"
        img_urls = set()

        # ✅ 1. <img src="...">
        for tag in soup.find_all("img", src=True):
            img_urls.add(urljoin(url, tag['src']))

        # ✅ 2. style="background-image: url(...)"
        for tag in soup.find_all(style=re.compile("background-image")):
            style = tag.get("style", "")
            match = re.search(r"background-image\s*:\s*url\((.*?)\)", style)
            if match:
                img_urls.add(urljoin(url, match.group(1).strip('"\' ')))

        # ✅ 3. [data-bg="url(...)"]
        for tag in soup.find_all(attrs={"data-bg": True}):
            match = re.search(r"url\((.*?)\)", tag['data-bg'])
            if match:
                img_urls.add(urljoin(url, match.group(1).strip('"\' ')))

        # ✅ 4. [data-src="..."]
        for tag in soup.find_all(attrs={"data-src": True}):
            img_urls.add(urljoin(url, tag['data-src']))

        # ✅ 이미지 저장
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

# ✅ 대상 URL 목록
url_list = [
    "http://thecrest.co.kr/?m=art_project",
    "http://thecrest.co.kr/?m=nobility",
    "http://www.hi1009.com/renew/sub02/sub_0201.php",
    "http://www.hi1009.com/renew/sub02/sub_0202.php",
    "http://www.hi1009.com/renew/sub02/sub_0203.php",
    "http://www.hi1009.com/renew/sub02/sub_0204.php",
    "http://www.xn--6w2b15kutaz6o56r.com/intro/sisul.asp",
    "http://www.xn--6w2b15kutaz6o56r.com/intro/sisul1.asp",
    "http://www.xn--6w2b15kutaz6o56r.com/intro/other_sisul.asp",
    "http://www.xn--6w2b15kutaz6o56r.com/album/pds_list.asp?BGNO=2008",
]

# ✅ 실행
for url in url_list:
    download_images_from_url(url)
