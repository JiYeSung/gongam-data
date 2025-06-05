from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import subprocess, requests, os

app = FastAPI()

# ✅ CORS 설정 추가 (아임웹에서 호출 가능하게)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 또는 ["https://xxx.imweb.me"] 등 특정 도메인
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 환경 변수
API_SECRET = os.getenv("SECRET_KEY")
GITHUB_RAW_BASE = os.getenv("RAW_BASE_URL")  # 예: https://raw.githubusercontent.com/JiYeSung/gongam-data/main/

# ✅ 다운로드 대상 파일 목록
FILES = [
    "code/1_get_urls_ver2.py",
    "code/2_data_formatting_ver2.py",
    "code/3_auto_push_ver2.py",
    "run_all.py"
]

@app.post("/gongam-update-script")
async def run_script(request: Request):
    # 🔐 인증 체크
    token = request.headers.get("Authorization")
    if token != f"Bearer {API_SECRET}":
        raise HTTPException(status_code=403, detail="Unauthorized")

    # 📥 파일 다운로드
    for file_name in FILES:
        file_url = f"{GITHUB_RAW_BASE}{file_name}"
        try:
            response = requests.get(file_url)
            response.raise_for_status()

            local_path = os.path.join(".", file_name)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            with open(local_path, "w", encoding="utf-8") as f:
                f.write(response.text)

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
