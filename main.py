from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import subprocess, requests, os
import logging

# ✅ 로그 설정
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# ✅ CORS 설정 (필요 시 도메인 제한 가능)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 환경 변수 불러오기
API_SECRET = os.getenv("SECRET_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "JiYeSung"
REPO_NAME = "gongam-data"
BRANCH = "main"

# ✅ 다운로드할 GitHub 경로들
FILES = [
    "code/1_get_urls_ver2.py",
    "code/2_data_formatting_ver2.py",
    "code/3_auto_push_ver2.py",
    "run_all.py"
]

# ✅ GitHub API에서 파일을 다운로드
def download_file_from_github(file_path):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}?ref={BRANCH}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.raw"
    }

    # 디버깅 로그
    logging.info(f"📥 GitHub API 요청: {url}")
    logging.info(f"🔐 Authorization: Bearer {GITHUB_TOKEN[:10]}...")

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logging.error(f"❌ 요청 실패 ({response.status_code}) → {response.text}")
        response.raise_for_status()

    return response.text

# ✅ 실행 API 엔드포인트
@app.post("/gongam-update-script")
async def run_script(request: Request):
    # 🔐 API 키 검증
    token = request.headers.get("Authorization")
    if token != f"Bearer {API_SECRET}":
        raise HTTPException(status_code=403, detail="Unauthorized")

    # 🧪 환경변수 확인 로그
    logging.info(f"📌 SECRET_KEY 유무: {'O' if API_SECRET else 'X'}")
    logging.info(f"📌 GITHUB_TOKEN 유무: {'O' if GITHUB_TOKEN else 'X'}")

    # 📥 GitHub 파일 다운로드 및 저장
    for file_name in FILES:
        try:
            content = download_file_from_github(file_name)
            local_path = os.path.join(".", file_name)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, "w", encoding="utf-8") as f:
                f.write(content)
            logging.info(f"✅ 다운로드 완료: {file_name}")
        except Exception as e:
            logging.exception(f"❌ {file_name} 다운로드 실패")
            raise HTTPException(status_code=500, detail=f"❌ {file_name} 다운로드 실패: {str(e)}")

    # ▶ run_all.py 실행
    try:
        result = subprocess.run(["python", "run_all.py"], capture_output=True, text=True)
        logging.info("▶ run_all.py 실행 완료")
        return {
            "output": result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        logging.exception("❌ run_all.py 실행 실패")
        raise HTTPException(status_code=500, detail=f"❌ 실행 실패: {str(e)}")
