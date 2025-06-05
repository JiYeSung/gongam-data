import os
import subprocess

# ✅ 환경 변수로부터 GitHub 토큰과 레포지토리 정보 불러오기
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "JiYeSung"
REPO_NAME = "gongam-data"
REPO_URL_WITH_TOKEN = f"https://{GITHUB_TOKEN}@github.com/{REPO_OWNER}/{REPO_NAME}.git"

def run_git_commands(repo_path="."):
    try:
        # ✅ Git 사용자 정보 설정 (커밋할 사용자 이름/이메일)
        subprocess.run(["git", "config", "--global", "user.name", "Gongam Bot"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "bot@gongam.ai"], check=True)

        # ✅ Git remote URL을 토큰 인증 주소로 설정 (푸시를 위해)
        subprocess.run(["git", "remote", "set-url", "origin", REPO_URL_WITH_TOKEN], cwd=repo_path, check=True)

        # ✅ 변경사항을 스테이지에 추가하고 커밋
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
        subprocess.run(["git", "commit", "-m", "Auto update thumbnails and detail_images"], cwd=repo_path, check=True)

        # ✅ GitHub로 푸시
        subprocess.run(["git", "push", "origin", "main"], cwd=repo_path, check=True)

        print("✅ Git 자동 푸시 완료")

    except subprocess.CalledProcessError as e:
        print(f"❌ Git 명령 실행 중 오류 발생: {e}")
