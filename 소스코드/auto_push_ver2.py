import os
import json
import subprocess

# === 경로 설정 ===
DB_REPO_DIR = "./"
DB_FILE_PATH = os.path.join(DB_REPO_DIR, "gongam_detail_db.json")
UPDATE_FILE_PATH = "./gongam_detail_db_result.json"  # ✅ 크롤링 결과 파일
GIT_COMMIT_MESSAGE = "Auto update detail DB with new entries"

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

    for new_key_candidate, new_item in update_items.items():
        new_name = new_item.get("name", "")
        new_title = new_item.get("summary", {}).get("title", "")

        # ✅ 기존 항목과 중복 여부 확인
        is_duplicate = False
        for key, old_item in db_data.items():
            if old_item.get("name") == new_name and old_item.get("summary", {}).get("title", "") == new_title:
                print(f"⏩ 중복: '{new_name}' - '{new_title}' (key: {key}) → 추가 생략")
                is_duplicate = True
                break

        if is_duplicate:
            continue

        # ✅ 새 키 생성 및 detailpage_url 삽입
        new_key = generate_next_key(db_data)
        new_item["detailpage_url"] = f"/detail/?id={new_key}"

        db_data[new_key] = new_item
        print(f"🆕 신규 추가됨: '{new_name}' (key: {new_key})")
        is_updated = True

    # ✅ DB 저장 및 Git 처리
    if is_updated:
        with open(DB_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(db_data, f, ensure_ascii=False, indent=2)
        print(f"💾 '{DB_FILE_PATH}' 저장 완료")
        run_git_commands(DB_REPO_DIR, GIT_COMMIT_MESSAGE)
    else:
        print("✅ 변경 사항 없음 → 저장 및 푸시 생략")

if __name__ == "__main__":
    update_detail_db()
