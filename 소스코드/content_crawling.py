import requests
from bs4 import BeautifulSoup

# ✅ 실제 테스트할 게시글 URL로 교체하세요
URL = "https://gongamcompany.imweb.me/gongam-imgdb/?bmode=view&idx=164891943&back_url=&t=board&page="

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def extract_table_cells(url):
    res = requests.get(url, headers=headers)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")

    # ✅ 개별 셀 추출
    data = {
        "name_1": soup.find(id="cell-row1-col1").text.strip(),
        "area_1": soup.find(id="cell-row1-col2").text.strip(),
        "name_2": soup.find(id="cell-row2-col1").text.strip(),
        "area_2": soup.find(id="cell-row2-col2").text.strip(),
    }

    return data

if __name__ == "__main__":
    table_data = extract_table_cells(URL)
    for key, value in table_data.items():
        print(f"{key}: {value}")
