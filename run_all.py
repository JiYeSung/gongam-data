from scripts import get_urls_ver2, data_formatting_ver2, auto_push_ver2

print("✅ 실행 시작")

# 1단계
print("\n📌 [1/3] URL 목록 수집 중...")
get_urls_ver2.main()

# 2단계
print("\n📌 [2/3] 상세페이지 데이터 포맷팅 중...")
data_formatting_ver2.main()

# 3단계
print("\n📌 [3/3] DB 업데이트 및 Git Push 중...")
auto_push_ver2.main()  

# 클라이언트 전용 로그 메시지
print("\n✅ 모든 스크립트 실행이 완료되었습니다.")
