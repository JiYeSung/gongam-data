import subprocess
import sys

def run_script(script_path, args=None):
    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)
    print(f"🚀 실행 중: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 실행 실패: {script_path}")
        print(f"↳ 에러 코드: {e.returncode}")
        sys.exit(e.returncode)

def main():
    # 1️⃣ 카운트 범위 입력 받기
    try:
        min_count = input("🟢 최소 count 값 입력 (예: 9): ").strip()
        max_count = input("🟢 최대 count 값 입력 (예: 13): ").strip()
        assert min_count.isdigit() and max_count.isdigit()
    except Exception:
        print("❌ 유효한 숫자를 입력하세요.")
        return

    # 2️⃣ 이미지 URL 수집
    run_script("./소스코드/get_image_urls.py", [min_count, max_count])

    # 3️⃣ 이미지 src → 포맷팅된 JSON 저장
    run_script("./소스코드/data_formatting.py")

    # 4️⃣ 업데이트된 JSON → DB 반영 + Git 푸시
    run_script("./소스코드/git_auto_push.py")

    print("\n✅ Git에 이미지 업데이트 완료!")

if __name__ == "__main__":
    main()
