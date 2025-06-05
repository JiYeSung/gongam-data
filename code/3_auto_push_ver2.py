import json
import os
import base64
import httpx

DB_FILE_PATH = "./gongam_detail_db.json"
COMMIT_MESSAGE = "자동 업데이트 커밋"

# ✅ GitHub 푸시 함수
def push_to_github(file_path: str, commit_message: str):
    owner = "JiYeSung"
    repo = "gongam-data"
    branch = "main"
    github_token = os.getenv("GITHUB_TOKEN")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    content_b64 = base64.b64encode(content.encode()).decode()

    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{os.path.basename(file_path)}"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json"
    }

    # 기존 파일의 SHA 필요
    r_get = httpx.get(api_url, headers=headers)
    sha = r_get.json().get("sha") if r_get.status_code == 200 else None

    payload = {
        "message": commit_message,
        "content": content_b64,
        "branch": branch
    }
    if sha:
        payload["sha"] = sha

    r_put = httpx.put(api_url, json=payload, headers=headers)

    if r_put.status_code in (200, 201):
        print("✅ GitHub 푸시 성공")
    else:
        print(f"❌ GitHub 푸시 실패: {r_put.status_code} / {r_put.text}")

# ✅ 실제 DB 저장 후 푸시
def main():
    # 예시: 로컬에서 어떤 처리 후 DB 저장
    with open(DB_FILE_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)

    print(f"💾 '{DB_FILE_PATH}' 저장 완료")
    
    # GitHub로 푸시
    push_to_github(DB_FILE_PATH, COMMIT_MESSAGE)

if __name__ == "__main__":
    main()
