import json
import os
from datetime import datetime
import subprocess

# 경로 설정
GIT_REPO_DIR = "../"
DB_PATH = os.path.join(GIT_REPO_DIR, "gongam_detail_db.json")
FOOTER_PATH = os.path.join(GIT_REPO_DIR, "footer.json")

# 1. 기존 DB와 푸터 JSON 로드
with open(DB_PATH, "r", encoding="utf-8") as f:
    db = json.load(f)

with open(FOOTER_PATH, "r", encoding="utf-8") as f:
    footer = json.load(f)

# 2. 기존 마지막 키 확인
existing_keys = sorted(int(k) for k in db.keys())
last_key_num = existing_keys[-1]

# 3. 푸터 JSON 데이터 정렬
footer_items = sorted(footer.items(), key=lambda x: int(x[0]))

# 4. 새로운 키값으로 병합 (내용이 같으면 skip)
new_data = {}
for _, value in footer_items:
    # 동일한 내용이 이미 있는지 검사
    if any(existing_value == value for existing_value in db.values()):
        print(f"⚠️ 동일한 항목이 이미 존재하여 추가 생략됨 → {value.get('name')}")
        continue

    # 신규 키 생성
    last_key_num += 1
    new_key = str(last_key_num).zfill(3)
    db[new_key] = value
    new_data[new_key] = value

# 5. 저장
with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print(f"✅ {len(new_data)}건 추가 완료 → 키값: {', '.join(new_data.keys())}")

# 6. Git 자동 처리
try:
    subprocess.run(["git", "add", "."], cwd=GIT_REPO_DIR, check=True)
    commit_message = f"Add footer data: {', '.join(new_data.keys())} - {datetime.now().isoformat(timespec='seconds')}"
    subprocess.run(["git", "commit", "-m", commit_message], cwd=GIT_REPO_DIR, check=True)
    subprocess.run(["git", "push"], cwd=GIT_REPO_DIR, check=True)
    print("🚀 Git 커밋 및 푸시 완료")
except subprocess.CalledProcessError as e:
    print(f"❌ Git 명령 중 오류 발생: {e}")
