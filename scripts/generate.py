import requests
from PIL import Image, ImageDraw, ImageFont
import os
import re

# 配置路径
BASE_IMAGE_PATH = "lottery.png"        # 你的底图
OUTPUT_IMAGE_PATH = "images/output.png" # 输出图
# 注意：GitHub Actions 里通常用 DejaVu 字体，如果报错请保持这行，或者改成你仓库里有的字体
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" 

# 3D 开奖数据 API
def get_lottery_data():
    url = "https://kaijiang.500.com/3d.shtml"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'gb2312' # 500.com 用 gb2312 编码
        
        # 【关键修改】根据你刚才截图里的 class="ball_red" 来匹配
        # 这个正则更准确，匹配 <li class="ball_red">数字</li>
        pattern = r'<li class="ball_red">(\d)</li>'
        numbers = re.findall(pattern, response.text)
        
        if len(numbers) == 3:
            return numbers  # 返回列表 ['1', '2', '3']
            
        print("正则未匹配到数据，尝试备用方案...")
        # 备用方案：找最近的开奖号码（如果上面没抓到）
        pattern2 = r'开奖号码.*?<strong>(\d)(\d)(\d)</strong>'
        match = re.search(pattern2, response.text.replace('\n', ''))
        if match:
            return [match.group(1), match.group(2), match.group(3)]
            
    except Exception as e:
        print(f"获取数据失败: {e}")
    return None

# 绘制图片
def draw_image(numbers):
    if not numbers:
        print("未获取到开奖号码，跳过绘图")
        return

    if not os.path.exists(BASE_IMAGE_PATH):
        print(f"底图不存在: {BASE_IMAGE_PATH}")
        return

    img = Image.open(BASE_IMAGE_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(FONT_PATH, 48)
    except:
        font = ImageFont.load_default()

    width, height = img.size
    num_width = 60
    total_width = num_width * 3 + 20
    start_x = (width - total_width) // 2
    y = (height - 60) // 2

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

    os.makedirs(os.path.dirname(OUTPUT_IMAGE_PATH), exist_ok=True)
    img.save(OUTPUT_IMAGE_PATH)
    print(f"图片已生成: {OUTPUT_IMAGE_PATH}")

if __name__ == "__main__":
    numbers = get_lottery_data()
    if numbers:
        print(f"获取到开奖号码: {numbers}")
        draw_image(numbers)
    else:
        print("未获取到有效号码，不生成图片")
