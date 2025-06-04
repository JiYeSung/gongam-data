import subprocess
import sys

def run_script(script_path, args=None):
    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)
    print(f"\n🚀 실행 중: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 실행 실패: {script_path}")
        sys.exit(e.returncode)

def main():
    print("===== 공감 이미지 자동화 파이프라인 =====")

    # 1️⃣ 게시판에서 수집할 count 필터 입력
    print("🎯 [1단계] 이미지 게시글 수집 조건 설정")
    print("예: 5 10 23 또는 9-12 또는 [엔터] = 전체")
    user_input = input("입력 ▶ ").strip()

    args = []
    if user_input:
        args = [user_input]

    # 2️⃣ 수집 실행 (2_get_image_urls.py)
    run_script("2_get_image_urls.py", args)

    # 3️⃣ 이미지 포맷팅 실행 (3_data_formatting.py)
    run_script("3_data_formatting.py")

    # 4️⃣ DB 병합 및 Git 푸시 (4_git_auto_push.py)
    run_script("4_git_auto_push.py")

    print("\n✅ 전체 파이프라인 완료! 🎉")

if __name__ == "__main__":
    main()
