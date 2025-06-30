import requests
from bs4 import BeautifulSoup
import random
import time

# ✅ 다양한 User-Agent 리스트
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
]

titles = []

for i in range(1, 43):  # 001부터 042까지
    url = f"https://gongamcompany.imweb.me/{str(i).zfill(3)}"
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": "https://www.google.com",  # 또는 https://gongamcompany.imweb.me/
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    try:
        time.sleep(random.uniform(1, 2))  # 너무 빠른 요청 방지
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string.strip() if soup.title else "No Title"
        titles.append(title)
    except Exception as e:
        titles.append(f"{url} → Error: {str(e)}")

# txt 파일로 저장
with open("gongam_titles.txt", "w", encoding="utf-8") as f:
    for line in titles:
        f.write(line + "\n")
