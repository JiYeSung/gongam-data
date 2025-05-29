import os
import json
import subprocess

# === 경로 설정 ===
DB_REPO_DIR = "./"
DB_FILE_PATH = os.path.join(DB_REPO_DIR, "gongam_detail_db.json")
GIT_COMMIT_MESSAGE = "Auto-fill missing detailpage_url based on key"

def run_git_commands(repo_path, commit_message):
    try:
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
        subprocess.run(["git", "commit", "-m", commit_message], cwd=repo_path, check=True)
        subprocess.run(["git", "push"], cwd=repo_path, check=True)
        print("✅ Git 커밋 및 푸시 완료")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 명령 중 오류 발생: {e}")

def fill_missing_detail_urls():
    # DB 로드
    with open(DB_FILE_PATH, 'r', encoding='utf-8') as f:
        db_data = json.load(f)

    is_updated = False

    for key, value in db_data.items():
        if not value.get("detailpage_url"):  # detailpage_url이 비어있다면
            db_data[key]["detailpage_url"] = f"/detail/?id={key}"
            print(f"🔧 '{key}' → detailpage_url 채움: /detail/?id={key}")
            is_updated = True

    # 변경 사항이 있으면 저장 및 Git 처리
    if is_updated:
        with open(DB_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(db_data, f, ensure_ascii=False, indent=2)
        print("💾 JSON 파일 저장 완료")
        run_git_commands(DB_REPO_DIR, GIT_COMMIT_MESSAGE)
    else:
        print("✅ 모든 항목에 detailpage_url이 이미 존재합니다.")

if __name__ == "__main__":
    fill_missing_detail_urls()
