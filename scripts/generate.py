import requests
from PIL import Image, ImageDraw, ImageFont
import os
import re
import sys

# 确保 Pillow 能用
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
    from PIL import Image, ImageDraw, ImageFont

# 配置路径
BASE_IMAGE_PATH = "lottery.png"         # 底图
OUTPUT_IMAGE_PATH = "images/output.png"  # 输出图
FONT_PATH = "DejaVuSans-Bold.ttf"       # 用系统默认字体

# 获取3D开奖号码
def get_lottery_data():
    try:
        url = "https://kaijiang.500.com/3d.shtml"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'gb2312'
        
        # 方法1：找 class="ball_red" 的红色球
        pattern1 = r'<li class="ball_red">(\d)</li>'
        numbers = re.findall(pattern1, response.text)
        if len(numbers) == 3:
            print(f"方法1找到号码: {numbers}")
            return numbers
        
        # 方法2：找开奖号码
        pattern2 = r'开奖号码.*?<strong>(\d)(\d)(\d)</strong>'
        match = re.search(pattern2, response.text, re.DOTALL)
        if match:
            nums = [match.group(1), match.group(2), match.group(3)]
            print(f"方法2找到号码: {nums}")
            return nums
        
        # 方法3：如果都找不到，用今天的日期数字
        from datetime import datetime
        today = datetime.now()
        day_str = str(today.day).zfill(2)
        nums = [day_str[0], day_str[1], str(today.month)[0]]
        print(f"使用测试号码: {nums}")
        return nums
        
    except Exception as e:
        print(f"获取数据出错: {e}")
        return ['1', '2', '3']

# 在图片上画数字
def draw_image(numbers):
    if not numbers or len(numbers) != 3:
        print("没有号码，不画图")
        return
    
    # 打开底图
    if not os.path.exists(BASE_IMAGE_PATH):
        print("没有底图，用白底")
        img = Image.new('RGB', (250, 128), 'white')
    else:
        img = Image.open(BASE_IMAGE_PATH).convert("RGB")
    
    draw = ImageDraw.Draw(img)
    
    # 用默认字体
    try:
        font = ImageFont.truetype(FONT_PATH, 45)
    except:
        font = ImageFont.load_default()
        print("用默认字体")
    
    # 图片大小
    width, height = img.size
    
    # 画三个圆
    circle_size = 60
    space = 15
    total_width = (circle_size * 3) + (space * 2)
    start_x = (width - total_width) // 2
    y = (height - circle_size) // 2
    
    for i, num in enumerate(numbers):
        x = start_x + i * (circle_size + space)
        
        # 画红色圆圈
        draw.ellipse(
            [x, y, x + circle_size, y + circle_size],
            fill='red',
            outline='black',
            width=2
        )
        
        # 画黑色数字
        bbox = draw.textbbox((0, 0), num, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        text_x = x + (circle_size - text_w) // 2
        text_y = y + (circle_size - text_h) // 2
        draw.text((text_x, text_y), num, fill='black', font=font)
        print(f"画数字 {num} 在 ({x},{y})")
    
    # 保存图片
    os.makedirs(os.path.dirname(OUTPUT_IMAGE_PATH), exist_ok=True)
    img.save(OUTPUT_IMAGE_PATH)
    print(f"图片保存到: {OUTPUT_IMAGE_PATH}")

# 主程序
if __name__ == "__main__":
    print("=== 开始生成开奖图片 ===")
    nums = get_lottery_data()
    print(f"开奖号码: {nums}")
    draw_image(nums)
    print("=== 完成 ===")
