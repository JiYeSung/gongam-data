import os
import json
import base64
import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "JiYeSung"
REPO_NAME = "gongam-data"
BRANCH = "main"

RESULT_FILE = "gongam_detail_db_result.json"
MAIN_FILE = "gongam_detail_db.json"

def log(message):
    print(message)

def load_json_file(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json_file(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def normalize_for_comparison(data):
    ignore_keys = {"url", "detailpage_url"}
    def recurse(d):
        if isinstance(d, dict):
            return {k: recurse(v) for k, v in d.items() if k not in ignore_keys}
        elif isinstance(d, list):
            return [recurse(i) for i in d]
        else:
            return d
    return recurse(data)

def update_main_data(result_data, main_data):
    updated = False
    changed_keys = []
    added_keys = []
    deleted_keys = []
    processed_keys = set()

    reverse_lookup = {
        (v.get("name"), v.get("summary", {}).get("title")): k
        for k, v in main_data.items()
    }

    for new_key, new_item in result_data.items():
        new_name = new_item.get("name")
        new_title = new_item.get("summary", {}).get("title")
        lookup_key = reverse_lookup.get((new_name, new_title))

        if lookup_key:
            if lookup_key in processed_keys:
                continue
            existing_item = main_data[lookup_key]
            if normalize_for_comparison(existing_item) != normalize_for_comparison(new_item):
                # 변경된 항목
                main_item = dict(new_item)
                main_item["detailpage_url"] = f"/detail/?id={lookup_key}"
                main_data[lookup_key] = main_item
                changed_keys.append((lookup_key, main_item["name"], main_item["summary"]["title"]))
                updated = True
            processed_keys.add(lookup_key)
        else:
            # 추가된 항목
            main_data[new_key] = dict(new_item)
            main_data[new_key]["detailpage_url"] = f"/detail/?id={new_key}"
            added_keys.append((new_key, new_item["name"], new_item["summary"]["title"]))
            updated = True

    # 삭제된 항목 탐지
    for key in list(main_data.keys()):
        if key not in result_data:
            deleted_keys.append((key, main_data[key].get("name"), main_data[key].get("summary", {}).get("title")))
            del main_data[key]
            updated = True

    return updated, changed_keys, added_keys, deleted_keys

def push_to_github(file_path, repo_path):
    with open(file_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{repo_path}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json",
    }

    res = requests.get(url, headers=headers)
    sha = res.json().get("sha") if res.status_code == 200 else None

    message = f"Auto update {repo_path}"
    data = {
        "message": message,
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

def main():
    result_data = load_json_file(RESULT_FILE)
    main_data = load_json_file(MAIN_FILE)

    updated, changed_keys, added_keys, deleted_keys = update_main_data(result_data, main_data)

    if updated:
        save_json_file(main_data, MAIN_FILE)
        push_to_github(RESULT_FILE, RESULT_FILE)
        push_to_github(MAIN_FILE, MAIN_FILE)
    else:
        log("ℹ️ 변경 사항 없음")

    for k, name, title in changed_keys:
        log("♻️ 변경된 항목:\n" + json.dumps({
            "key": k,
            "name": name,
            "title": title
        }, ensure_ascii=False, indent=2))
    for k, name, title in added_keys:
        log("🆕 추가된 항목:\n" + json.dumps({
            "key": k,
            "name": name,
            "title": title
        }, ensure_ascii=False, indent=2))
    for k, name, title in deleted_keys:
        log("🗑️ 삭제된 항목:\n" + json.dumps({
            "key": k,
            "name": name,
            "title": title
        }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
