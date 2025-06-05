import os
import base64
import json
import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "JiYeSung"
REPO_NAME = "gongam-data"
BRANCH = "main"

RESULT_FILE = "gongam_detail_db_result.json"
MAIN_FILE = "gongam_detail_db.json"

def load_json_file(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def update_main_data(result_data, main_data):
    updated = False
    existing_keys = list(main_data.keys())
    changed_keys = []
    added_keys = []

    def next_index():
        return f"{max([int(k) for k in existing_keys] + [0]) + 1:03}"

    for _, new_item in result_data.items():
        matched_key = None
        for key, existing_item in main_data.items():
            same_name = existing_item.get("name") == new_item.get("name")
            same_title = existing_item.get("summary", {}).get("title") == new_item.get("summary", {}).get("title")

            if same_name and same_title:
                matched_key = key

                # ✅ detailpage_url이 누락되었을 경우 추가
                if "detailpage_url" not in existing_item:
                    existing_item["detailpage_url"] = f"/detail/?id={key}"
                    main_data[key] = existing_item
                    updated = True

                # ✅ 내용이 바뀌었을 경우 전체 업데이트
                if existing_item != new_item:
                    new_item["detailpage_url"] = f"/detail/?id={key}"
                    main_data[key] = new_item
                    changed_keys.append((key, new_item["name"], new_item["summary"]["title"]))
                    updated = True
                break

        if not matched_key:
            new_key = next_index()
            new_item["detailpage_url"] = f"/detail/?id={new_key}"
            main_data[new_key] = new_item
            added_keys.append((new_key, new_item["name"], new_item["summary"]["title"]))
            existing_keys.append(int(new_key))
            updated = True

    deleted_keys = []
    result_name_title_set = set(
        (v.get("name"), v.get("summary", {}).get("title")) for v in result_data.values()
    )

    for key, item in list(main_data.items()):
        pair = (item.get("name"), item.get("summary", {}).get("title"))
        if pair not in result_name_title_set:
            deleted_keys.append((key, item.get("name"), item.get("summary", {}).get("title")))
            del main_data[key]
            updated = True

    return main_data, updated, changed_keys, added_keys, deleted_keys

def push_file_to_github(file_path, commit_message, github_file_path, log):
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    github_api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{github_file_path}"
    log(f"🔍 {github_file_path} GitHub SHA 조회 중...")
    response = requests.get(github_api_url, headers=headers, params={"ref": BRANCH})

    if response.status_code == 200:
        sha = response.json()["sha"]
        log("🔄 기존 파일 업데이트 방식으로 진행합니다.")
    elif response.status_code == 404:
        sha = None
        log("🆕 새 파일로 생성합니다.")
    else:
        log(f"❌ SHA 조회 실패: {response.status_code} → {response.text}")
        return False

    with open(file_path, "rb") as f:
        encoded_content = base64.b64encode(f.read()).decode("utf-8")

    payload = {
        "message": commit_message,
        "content": encoded_content,
        "branch": BRANCH
    }
    if sha:
        payload["sha"] = sha

    log(f"📤 {github_file_path} GitHub에 푸시 중...")
    put_response = requests.put(github_api_url, headers=headers, data=json.dumps(payload))
    if put_response.status_code in [200, 201]:
        log("✅ GitHub API를 통한 푸시 성공!")
        return True
    else:
        log(f"❌ GitHub API 푸시 실패: {put_response.status_code} → {put_response.text}")
        return False

def run_git_api_push():
    log_messages = []

    def log(msg):
        print(msg)
        log_messages.append(str(msg))

    if not GITHUB_TOKEN:
        log("❌ GITHUB_TOKEN 환경변수가 설정되지 않았습니다.")
        return "토큰 없음"

    # ✅ JSON 파일 로드
    result_data = load_json_file(RESULT_FILE)
    main_data = load_json_file(MAIN_FILE)

    # ✅ DB 병합 및 비교
    updated_data, is_updated, changed_keys, added_keys, deleted_keys = update_main_data(result_data, main_data)

    # ✅ 항상 result 파일 저장 & 푸시
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)

    log("📤 gongam_detail_db_result.json GitHub에 푸시 시작")
    push_file_to_github(RESULT_FILE, "Auto push result file", RESULT_FILE, log)

    # ✅ 변경된 경우에만 main 파일 저장 & 푸시
    if is_updated:
        for k, name, title in changed_keys:
            log("♻️ 변경된 항목:\n" + json.dumps({"key": k, "name": name, "title": title}, ensure_ascii=False, indent=2))
        for k, name, title in added_keys:
            log("🆕 추가된 항목:\n" + json.dumps({"key": k, "name": name, "title": title}, ensure_ascii=False, indent=2))
        for k, name, title in deleted_keys:
            log("🗑️ 삭제된 항목:\n" + json.dumps({"key": k, "name": name, "title": title}, ensure_ascii=False, indent=2))

        with open(MAIN_FILE, "w", encoding="utf-8") as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=2)

        log("📤 gongam_detail_db.json GitHub에 푸시 시작")
        push_file_to_github(MAIN_FILE, "Auto update gongam_detail_db.json", MAIN_FILE, log)
    else:
        log("✅ 변경된 내용이 없어 gongam_detail_db.json 푸시 생략")

    return "\n".join(log_messages)
