from code import (
    _1_get_urls_ver2 as get_urls,
    _2_data_formatting_ver2 as formatter,
    _3_auto_push_ver2 as git_auto_push
)

print("✅ 실행 시작")

# 1단계
print("\n📌 [1/3] URL 목록 수집 중...")
get_urls.main()

# 2단계
print("\n📌 [2/3] 상세페이지 데이터 포맷팅 중...")
formatter.main()

# 3단계
print("\n📌 [3/3] DB 업데이트 및 Git Push 중...")
git_auto_push.run_git_commands()

print("\n✅ 전체 작업 완료!")
