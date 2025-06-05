import os
import base64
import json
import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "JiYeSung"
REPO_NAME = "gongam-data"
BRANCH = "main"
FILE_PATH = "gongam_detail_db_result.json"
LOCAL_FILE_PATH = FILE_PATH  # 로컬에서도 동일한 이름으로 저장됨

GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"

def run_git_api_push():
    if not GITHUB_TOKEN:
        print("❌ GITHUB_TOKEN 환경변수가 설정되지 않았습니다.")
        return

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # 현재 파일의 SHA 가져오기 (있으면 업데이트, 없으면 생성)
    print("🔍 기존 파일 SHA 조회 중...")
    response = requests.get(GITHUB_API_URL, headers=headers, params={"ref": BRANCH})

    if response.status_code == 200:
        sha = response.json()["sha"]
        print("🔄 기존 파일 업데이트 방식으로 진행합니다.")
    elif response.status_code == 404:
        sha = None
        print("🆕 새 파일로 생성합니다.")
    else:
        print(f"❌ SHA 조회 실패: {response.status_code} → {response.text}")
        return

    # 파일 읽기 및 base64 인코딩
    with open(LOCAL_FILE_PATH, "rb") as f:
        content_bytes = f.read()
    encoded_content = base64.b64encode(content_bytes).decode("utf-8")

    # API 요청 페이로드
    payload = {
        "message": "Auto update thumbnails and detail_images",
        "content": encoded_content,
        "branch": BRANCH
    }
    if sha:
        payload["sha"] = sha

    print("📤 GitHub에 파일 푸시 중...")
    response = requests.put(GITHUB_API_URL, headers=headers, data=json.dumps(payload))

    if response.status_code in [200, 201]:
        print("✅ GitHub API를 통한 자동 푸시 성공!")
    else:
        print(f"❌ GitHub API 푸시 실패: {response.status_code} → {response.text}")
