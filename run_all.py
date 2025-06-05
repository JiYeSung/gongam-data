from scripts import get_urls_ver2, data_formatting_ver2, auto_push_ver2

print("✅ 실행 시작")

print("\n📌 [1/3] URL 목록 수집 중...")
get_urls_ver2.main()

print("\n📌 [2/3] 상세페이지 데이터 포맷팅 중...")
data_formatting_ver2.main()

print("\n📌 [3/3] GitHub API를 통해 자동 푸시 중...")
auto_push_ver2.run_git_api_push()

print("\n✅ 전체 작업 완료!")
