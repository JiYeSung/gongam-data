from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import subprocess, requests, os

app = FastAPI()

# ✅ CORS 설정 (아임웹 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 또는 ["https://xxx.imweb.me"]로 제한 가능
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 환경 변수
API_SECRET = os.getenv("SECRET_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "JiYeSung"
REPO_NAME = "gongam-data"
BRANCH = "main"

# ✅ 다운로드할 파일 경로
FILES = [
    "code/1_get_urls_ver2.py",
    "code/2_data_formatting_ver2.py",
    "code/3_auto_push_ver2.py",
    "run_all.py"
]

# ✅ GitHub API로 파일 다운로드 함수
def download_file_from_github(file_path):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}?ref={BRANCH}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.raw"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

# ✅ 실행 API
@app.post("/gongam-update-script")
async def run_script(request: Request):
    # 🔐 인증 확인
    token = request.headers.get("Authorization")
    if token != f"Bearer {API_SECRET}":
        raise HTTPException(status_code=403, detail="Unauthorized")

    # 📥 파일 다운로드 및 저장
    for file_name in FILES:
        try:
            content = download_file_from_github(file_name)
            local_path = os.path.join(".", file_name)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"❌ {file_name} 다운로드 실패: {str(e)}")

    # ▶ Python 스크립트 실행
    try:
        result = subprocess.run(["python", "run_all.py"], capture_output=True, text=True)
        return {
            "output": result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ 실행 실패: {str(e)}")
