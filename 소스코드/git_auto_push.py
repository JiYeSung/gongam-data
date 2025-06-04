import os
import json
import subprocess

# === 경로 설정 ===
DB_REPO_DIR = "./"
DB_FILE_PATH = os.path.join(DB_REPO_DIR, "gongam_detail_db.json")
UPDATES_FOLDER = "../images_update_data"
GIT_COMMIT_MESSAGE = "Auto update thumbnails, detail_images, and titles"

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
    # DB 로드
    with open(DB_FILE_PATH, 'r', encoding='utf-8') as f:
        db_data = json.load(f)

    is_updated = False  # 🔍 변경 여부 추적

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

        # ✅ 기존 항목 업데이트
        if found_key:
            current = db_data[found_key]
            new_thumbnail = update_data.get("thumbnail")
            new_detail_images = update_data.get("detail_images")
            new_title = update_data.get("title")

            current_thumbnail = current.get("thumbnail")
            current_detail_images = current.get("detail_images")
            current_title = current.get("summary", {}).get("title")

            if (
                current_thumbnail != new_thumbnail or
                current_detail_images != new_detail_images or
                current_title != new_title
            ):
                db_data[found_key]["thumbnail"] = new_thumbnail
                db_data[found_key]["detail_images"] = new_detail_images
                if "summary" not in db_data[found_key]:
                    db_data[found_key]["summary"] = {}
                db_data[found_key]["summary"]["title"] = new_title
                print(f"🔄 '{target_name}' 항목 업데이트 완료 (key: {found_key})")
                is_updated = True
            else:
                print(f"⏩ '{target_name}' 항목은 기존과 동일하여 생략됨")

        # ✅ 신규 항목 추가 (키는 무조건 있고, 값은 빈 포맷)
        else:
            new_key = generate_next_key(db_data)
            db_data[new_key] = {
                "name": target_name,
                "thumbnail": update_data.get("thumbnail", ""),
                "detail_images": update_data.get("detail_images", []),
                "summary": {
                    "title": update_data.get("title", "")
                },
                "area": "",
                "sub_area": "",
                "types": [],
                "price": "",
                "detailpage_url": "",
                "is_recommended": False,
                "location": {
                    "lat": "",
                    "lng": ""
                },
                "info": {},
                "price_table": {},
                "facilities": []
            }
            print(f"🆕 '{target_name}' 항목 신규 추가됨 (key: {new_key})")
            is_updated = True

    # DB 저장 및 Git 처리
    if is_updated:
        with open(DB_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(db_data, f, ensure_ascii=False, indent=2)
        print(f"💾 '{DB_FILE_PATH}' 저장 완료")
        run_git_commands(DB_REPO_DIR, GIT_COMMIT_MESSAGE)
    else:
        print("✅ 변경 사항이 없으므로 저장 및 푸시 생략")

if __name__ == "__main__":
    update_detail_db()
