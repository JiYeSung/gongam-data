import os
import json
import base64
import requests

# 🔐 토큰: 상위 폴더 github_token.txt에서 로드
TOKEN_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "../github_token.txt"))
try:
    with open(TOKEN_PATH, "r", encoding="utf-8") as f:
        GITHUB_TOKEN = f.read().strip()
except Exception as e:
    print(f"❌ 토큰 파일 로드 실패: {e}")
    GITHUB_TOKEN = None
print("📁 예상 경로:", TOKEN_PATH)
# ✅ 설정
REPO_OWNER = "JiYeSung"
REPO_NAME = "gongam-data"
BRANCH = "main"

RESULT_FILE = "gongam_detail_db_result.json"
MAIN_FILE = "gongam_detail_db.json"

def log(msg):
    print(msg)

def load_json_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log(f"❗ 파일 로드 실패 ({path}): {e}")
        return {}

def save_json_file(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def push_to_github(file_path, repo_path):
    if not GITHUB_TOKEN:
        log("❗ GITHUB_TOKEN이 설정되지 않았습니다.")
        return

    with open(file_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{repo_path}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json",
    }

    # 기존 SHA 조회
    res = requests.get(url, headers=headers)
    sha = res.json().get("sha") if res.status_code == 200 else None

    # 푸시 요청
    data = {
        "message": f"Auto update {repo_path}",
        "content": content,
        "branch": BRANCH,
    }
    if sha:
        data["sha"] = sha

    res = requests.put(url, headers=headers, json=data)
    if res.status_code in [200, 201]:
        log(f"✅ {repo_path} 푸시 완료")
    else:
        log(f"❌ {repo_path} 푸시 실패: {res.text}")

def should_push(new_data, old_data):
    for key in new_data:
        new_title = new_data[key].get("summary", {}).get("title", "")
        old_title = old_data.get(key, {}).get("summary", {}).get("title", "")
        if new_title != old_title:
            log(f"🔄 변경 감지: key={key}, old='{old_title}' → new='{new_title}'")
            return True
    return True

def main():
    result_data = load_json_file(RESULT_FILE)
    main_data = load_json_file(MAIN_FILE)

    # ✅ exposure_detailpage_url 추가
    for key in result_data:
        result_data[key]["exposure_detailpage_url"] = f"/{key}"

    if should_push(result_data, main_data):
        save_json_file(result_data, MAIN_FILE)
        push_to_github(MAIN_FILE, MAIN_FILE)
    else:
        log("✅ 변경된 title 없음 → 푸시 생략")

if __name__ == "__main__":
    main()
