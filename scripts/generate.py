import requests
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

# 配置路径
BASE_IMAGE_PATH = "lottery.png"        # 你的底图
OUTPUT_IMAGE_PATH = "images/output.png" # 输出图
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Linux 常用字体

# 3D 开奖数据 API（公开可用）
def get_lottery_data():
    url = "https://datachart.500.com/3d/history/newinc/history.php?start=0&end=1"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        # 解析 HTML 提取开奖号（简单正则）
        import re
        match = re.search(r'<td class="red">(\d{3})<\/td>', response.text)
        if match:
            return match.group(1)
    except Exception as e:
        print(f"获取数据失败: {e}")
    return None

# 绘制图片
def draw_image(numbers):
    if not numbers:
        print("未获取到开奖号码，跳过绘图")
        return

    # 打开底图
    if not os.path.exists(BASE_IMAGE_PATH):
        print(f"底图不存在: {BASE_IMAGE_PATH}")
        return

    img = Image.open(BASE_IMAGE_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 设置字体和大小（根据 250x128 调整）
    try:
        font = ImageFont.truetype(FONT_PATH, 48)
    except:
        font = ImageFont.load_default()

    # 计算每个数字的位置（横向居中）
    width, height = img.size
    num_width = 60
    total_width = num_width * 3 + 20  # 3个数字 + 间距
    start_x = (width - total_width) // 2
    y = (height - 60) // 2

    # 绘制三个数字（红底黑字圆形）
    for i, num in enumerate(numbers):
        x = start_x + i * (num_width + 5)
        # 画红色圆形背景
        draw.ellipse([(x, y), (x + num_width, y + 60)], fill="red", outline="black")
        # 画黑色数字
        bbox = draw.textbbox((0, 0), num, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = x + (num_width - text_width) // 2
        text_y = y + (60 - text_height) // 2 - 5
        draw.text((text_x, text_y), num, fill="black", font=font)

    # 保存图片
    os.makedirs(os.path.dirname(OUTPUT_IMAGE_PATH), exist_ok=True)
    img.save(OUTPUT_IMAGE_PATH)
    print(f"图片已生成: {OUTPUT_IMAGE_PATH}")

# 主程序
if __name__ == "__main__":
    numbers = get_lottery_data()
    if numbers:
        print(f"获取到开奖号码: {numbers}")
        draw_image(numbers)
    else:
        print("未获取到有效号码，不生成图片")
