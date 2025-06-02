import os

# ✅ 기준값: 6.3KB = 6451 bytes
THRESHOLD_BYTES = 10 * 1024

# ✅ 메인 폴더 경로
MAIN_FOLDER = "../../장지 이미지3"  # 예: "./images" 또는 "C:/Users/Me/Pictures"

# ✅ 이미지 확장자
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp")

# ✅ 하위 폴더 순회
for subdir, dirs, files in os.walk(MAIN_FOLDER):
    for file in files:
        if file.lower().endswith(IMAGE_EXTENSIONS):
            filepath = os.path.join(subdir, file)
            file_size = os.path.getsize(filepath)

            if file_size <= THRESHOLD_BYTES:
                print(f"🗑 삭제: {filepath} ({file_size} bytes)")
                os.remove(filepath)
