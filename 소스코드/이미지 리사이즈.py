from PIL import Image

# 원본 이미지 파일 경로
input_path = "hanbok.png"
# 저장할 리사이즈 이미지 경로
output_path = "hanbok.png_96x96.png"

# 이미지 열기
img = Image.open(input_path).convert("RGBA")  # 투명 배경 유지

# 96x96 사이즈로 리사이즈
resized_img = img.resize((96, 96), Image.LANCZOS)  # 고화질 리사이징

# 저장
resized_img.save(output_path, format="PNG")

print("✅ 96x96 PNG 아이콘 저장 완료:", output_path)