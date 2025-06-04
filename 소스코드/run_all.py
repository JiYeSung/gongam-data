import subprocess

# 1단계: URL 수집
print("📌 [1/3] URL 목록 수집 중...")
subprocess.run(["python", "1_get_urls_ver2.py"], check=True)

# 2단계: HTML → JSON 데이터 포맷팅
print("\n📌 [2/3] 상세페이지 데이터 포맷팅 중...")
subprocess.run(["python", "2_data_formatting_ver2.py"], check=True)

# 3단계: DB에 반영 및 Git 푸시
print("\n📌 [3/3] DB 업데이트 및 Git Push 중...")
subprocess.run(["python", "3_auto_push_ver2.py"], check=True)

print("\n✅ 전체 작업 완료!")
