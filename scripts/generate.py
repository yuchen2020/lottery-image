import requests
from PIL import Image, ImageDraw, ImageFont
import os
import re

# 配置路径
BASE_IMAGE_PATH = "lottery.png"        # 你的底图
OUTPUT_IMAGE_PATH = "images/output.png" # 输出图
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Linux 常用字体

# 3D 开奖数据 API - 使用更可靠的方法
def get_lottery_data():
    url = "https://kaijiang.500.com/3d.shtml"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'gb2312'
        
        # 使用更精确的正则匹配
        pattern = r'<li class="ball_red">(\d)</li>'
        numbers = re.findall(pattern, response.text)
        
        if len(numbers) == 3:
            return numbers  # 返回列表 ['1','2','3']
        
        # 备用方案
        pattern2 = r'开奖号码.*?<strong>(\d)(\d)(\d)</strong>'
        match = re.search(pattern2, response.text, re.IGNORECASE)
        if match:
            return [match.group(1), match.group(2), match.group(3)]
            
    except Exception as e:
        print(f"获取数据失败: {e}")
    
    # 如果都失败，返回测试数据
    print("警告: 使用测试数据")
    return ['1', '2', '3']

# 绘制图片
def draw_image(numbers):
    if not numbers or len(numbers) != 3:
        print(f"无效的号码: {numbers}")
        return

    # 检查底图是否存在
    if not os.path.exists(BASE_IMAGE_PATH):
        # 如果没有底图，创建一个空白底图
        img = Image.new('RGB', (250, 128), color='white')
        print("创建空白底图")
    else:
        img = Image.open(BASE_IMAGE_PATH).convert("RGB")
    
    draw = ImageDraw.Draw(img)

    # 设置字体
    try:
        font = ImageFont.truetype(FONT_PATH, 45)
    except:
        font = ImageFont.load_default()
        print("使用默认字体")

    # 计算位置
    width, height = img.size
    circle_diameter = 60
    spacing = 15
    total_width = (circle_diameter * 3) + (spacing * 2)
    start_x = (width - total_width) // 2
    y = (height - circle_diameter) // 2

    # 绘制三个圆形数字
    for i, num in enumerate(numbers):
        x = start_x + i * (circle_diameter + spacing)
        
        # 1. 画红色圆形背景
        draw.ellipse(
            [(x, y), (x + circle_diameter, y + circle_diameter)],
            fill="#FF0000",  # 纯红色
            outline="#000000",  # 黑色边框
            width=2
        )
        
        # 2. 居中绘制黑色数字
        bbox = draw.textbbox((0, 0), num, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = x + (circle_diameter - text_width) // 2
        text_y = y + (circle_diameter - text_height) // 2
        draw.text((text_x, text_y), num, fill="black", font=font)
        print(f"绘制数字 {num} 在位置 ({x},{y})")

    # 保存图片
    os.makedirs(os.path.dirname(OUTPUT_IMAGE_PATH), exist_ok=True)
    img.save(OUTPUT_IMAGE_PATH)
    print(f"图片已生成: {OUTPUT_IMAGE_PATH} ({width}x{height})")

# 主程序
if __name__ == "__main__":
    print("开始获取3D开奖数据...")
    numbers = get_lottery_data()
    print(f"获取到开奖号码: {numbers}")
    draw_image(numbers)
    print("完成!")
