import os
import json
import subprocess

# === 경로 설정 ===
DB_REPO_DIR = "./"
DB_FILE_PATH = os.path.join(DB_REPO_DIR, "gongam_detail_db.json")
UPDATES_FOLDER = "../images_update_data"
GIT_COMMIT_MESSAGE = "Auto update thumbnails and detail_images"

def run_git_commands(repo_path, commit_message):
    try:
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
        subprocess.run(["git", "commit", "-m", commit_message], cwd=repo_path, check=True)
        subprocess.run(["git", "push"], cwd=repo_path, check=True)
        print("✅ Git 커밋 및 푸시 완료")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 명령 중 오류 발생: {e}")

def update_detail_db():
    # DB 로드
    with open(DB_FILE_PATH, 'r', encoding='utf-8') as f:
        db_data = json.load(f)

    # 업데이트할 JSON 파일들 반복
    for filename in os.listdir(UPDATES_FOLDER):
        if not filename.endswith(".json"):
            continue

        update_path = os.path.join(UPDATES_FOLDER, filename)
        with open(update_path, 'r', encoding='utf-8') as f:
            update_data = json.load(f)

        target_name = filename.replace(".json", "")
        found_key = None

        for key, value in db_data.items():
            if value.get("name") == target_name:
                found_key = key
                break

        if found_key:
            db_data[found_key]["thumbnail"] = update_data["thumbnail"]
            db_data[found_key]["detail_images"] = update_data["detail_images"]
            print(f"🔄 '{target_name}' 항목 업데이트 완료 (key: {found_key})")
        else:
            print(f"⚠️  '{target_name}' 이름으로 된 항목을 DB에서 찾을 수 없습니다.")

    # DB 저장
    with open(DB_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(db_data, f, ensure_ascii=False, indent=2)

    print(f"💾 '{DB_FILE_PATH}' 저장 완료")

    # Git 커밋 & 푸시
    run_git_commands(DB_REPO_DIR, GIT_COMMIT_MESSAGE)

if __name__ == "__main__":
    update_detail_db()
