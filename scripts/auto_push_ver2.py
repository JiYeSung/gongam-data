import os
import base64
import json
import requests
import shutil

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "JiYeSung"
REPO_NAME = "gongam-data"
BRANCH = "main"

RESULT_FILE = "gongam_detail_db_result.json"  # 크롤링 결과
MAIN_FILE = "gongam_detail_db.json"           # 서비스용 파일
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{MAIN_FILE}"


def load_json_file(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def update_main_data(result_data, main_data):
    updated = False
    existing_keys = list(main_data.keys())

    def next_index():
        return f"{max([int(k) for k in existing_keys] + [0]) + 1:03}"

    for _, new_item in result_data.items():
        matched_key = None

        for key, existing_item in main_data.items():
            if (
                existing_item.get("name") == new_item.get("name") and
                existing_item.get("summary", {}).get("title") == new_item.get("summary", {}).get("title")
            ):
                matched_key = key
                if existing_item != new_item:
                    main_data[key] = new_item
                    updated = True
                break

        if not matched_key:
            new_key = next_index()
            main_data[new_key] = new_item
            existing_keys.append(int(new_key))
            updated = True

    return main_data, updated


def run_git_api_push():
    if not GITHUB_TOKEN:
        print("❌ GITHUB_TOKEN 환경변수가 설정되지 않았습니다.")
        return

    # 1️⃣ JSON 파일 비교 및 병합
    result_data = load_json_file(RESULT_FILE)
    main_data = load_json_file(MAIN_FILE)

    updated_data, is_updated = update_main_data(result_data, main_data)

    if not is_updated:
        print("✅ 변경된 내용이 없어 GitHub 푸시를 생략합니다.")
        return

    # 2️⃣ 파일 저장
    with open(MAIN_FILE, "w", encoding="utf-8") as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=2)

    # 3️⃣ GitHub API를 통한 푸시
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    print("🔍 기존 GitHub 파일 SHA 조회 중...")
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

    # 파일 인코딩
    with open(MAIN_FILE, "rb") as f:
        content_bytes = f.read()
    encoded_content = base64.b64encode(content_bytes).decode("utf-8")

    payload = {
        "message": "Auto update gongam_detail_db.json",
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
