import os
import json
import subprocess

# === 경로 설정 ===
DB_REPO_DIR = "./"
DB_FILE_PATH = os.path.join(DB_REPO_DIR, "gongam_detail_db.json")
UPDATE_FILE_PATH = "./gongam_detail_db_result.json"
GIT_COMMIT_MESSAGE = "Auto update detail DB with new or updated entries"

def run_git_commands(repo_path, commit_message):
    try:
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
        subprocess.run(["git", "commit", "-m", commit_message], cwd=repo_path, check=True)
        subprocess.run(["git", "push"], cwd=repo_path, check=True)
        print("✅ Git 커밋 및 푸시 완료")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 명령 중 오류 발생: {e}")

def generate_next_key(db_data):
    existing_keys = [int(k) for k in db_data.keys() if k.isdigit()]
    next_key = str(max(existing_keys, default=0) + 1).zfill(3)
    return next_key

def update_detail_db():
    # ✅ 기존 DB 로드
    if os.path.exists(DB_FILE_PATH):
        with open(DB_FILE_PATH, 'r', encoding='utf-8') as f:
            db_data = json.load(f)
    else:
        db_data = {}

    # ✅ 새로 수집한 JSON 로드
    if not os.path.exists(UPDATE_FILE_PATH):
        print(f"❌ '{UPDATE_FILE_PATH}' 파일이 존재하지 않습니다.")
        return

    with open(UPDATE_FILE_PATH, 'r', encoding='utf-8') as f:
        update_items = json.load(f)

    is_updated = False

    for _, new_item in update_items.items():
        new_name = new_item.get("name", "")
        new_title = new_item.get("summary", {}).get("title", "")

        matched_key = None
        for key, old_item in db_data.items():
            if old_item.get("name") == new_name and old_item.get("summary", {}).get("title", "") == new_title:
                matched_key = key
                # ✅ 전체 내용이 같으면 스킵
                if old_item == new_item:
                    print(f"⏩ 동일 항목: '{new_name}' (key: {key}) → 건너뜀")
                    matched_key = None  # 덮어쓰기, 추가 모두 생략
                break

        if matched_key:
            # ✅ 동일 name/title이지만 내용 다르면 덮어쓰기
            new_item["detailpage_url"] = f"/detail/?id={matched_key}"
            db_data[matched_key] = new_item
            print(f"🔄 내용 변경: '{new_name}' (key: {matched_key}) → 덮어쓰기")
            is_updated = True
        elif matched_key is None:
            # ✅ 완전한 신규 항목 → 새 key 발급
            new_key = generate_next_key(db_data)
            new_item["detailpage_url"] = f"/detail/?id={new_key}"
            db_data[new_key] = new_item
            print(f"🆕 신규 추가: '{new_name}' (key: {new_key})")
            is_updated = True

    if is_updated:
        with open(DB_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(db_data, f, ensure_ascii=False, indent=2)
        print(f"💾 '{DB_FILE_PATH}' 저장 완료")
        run_git_commands(DB_REPO_DIR, GIT_COMMIT_MESSAGE)
    else:
        print("✅ 모든 항목이 동일 → 저장 및 푸시 생략")

if __name__ == "__main__":
    update_detail_db()
