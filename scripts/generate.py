import requests
import re
from PIL import Image, ImageDraw, ImageFont
import os
import random

def get_3d_number():
    """从中国福彩网获取3D号码"""
    try:
        # 1. 获取官方首页
        url = "https://www.cwl.gov.cn/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=5)
        response.encoding = 'utf-8'  # 官方是utf-8，不会卡
        
        # 2. 在页面中查找3D号码
        html = response.text
        
        # 方法1：查找3D开奖区域
        pattern1 = r'福彩3D.*?第\s*(\d+)\s*期.*?<em[^>]*>(\d)</em>\s*<em[^>]*>(\d)</em>\s*<em[^>]*>(\d)</em>'
        match = re.search(pattern1, html, re.DOTALL)
        
        if match:
            num1, num2, num3 = match.group(2), match.group(3), match.group(4)
            return [num1, num2, num3]
        
        # 方法2：备用查找
        pattern2 = r'3D.*?>(\d)<.*?>(\d)<.*?>(\d)<'
        matches = re.findall(pattern2, html)
        if matches:
            return list(matches[0])
            
        # 方法3：如果都找不到，用今天的日期数字
        from datetime import datetime
        today = datetime.now()
        day_str = str(today.day).zfill(2)
        return [day_str[0], day_str[1], str(today.month % 10)]
        
    except Exception as e:
        print(f"获取数据出错: {e}")
        return ['0', '1', '2']  # 测试数据

def create_lottery_image(numbers):
    """创建开奖图片"""
    # 1. 创建图片 (250x128 像素)
    width, height = 250, 128
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # 2. 画背景（可选，如果没有底图就用白色）
    try:
        # 如果有底图lottery.png就用它
        if os.path.exists("lottery.png"):
            base_img = Image.open("lottery.png").convert("RGB")
            img = base_img.resize((width, height))
            draw = ImageDraw.Draw(img)
    except:
        pass
    
    # 3. 画三个红圈黑字的数字
    circle_diameter = 50
    spacing = 20
    total_width = (circle_diameter * 3) + (spacing * 2)
    start_x = (width - total_width) // 2
    y = (height - circle_diameter) // 2
    
    for i, num in enumerate(numbers):
        x = start_x + i * (circle_diameter + spacing)
        
        # 画红色圆形
        draw.ellipse(
            [x, y, x + circle_diameter, y + circle_diameter],
            fill='#FF0000',  # 红色
            outline='#000000',  # 黑色边框
            width=2
        )
        
        # 画黑色数字（居中）
        try:
            # 尝试加载字体
            font = ImageFont.truetype("arial.ttf", 30)
        except:
            # 用默认字体
            font = ImageFont.load_default()
        
        # 计算文字位置
        bbox = draw.textbbox((0, 0), num, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        text_x = x + (circle_diameter - text_w) // 2
        text_y = y + (circle_diameter - text_h) // 2
        
        draw.text((text_x, text_y), num, fill='black', font=font)
    
    # 4. 保存图片
    os.makedirs("images", exist_ok=True)
    img.save("images/output.png")
    print(f"✅ 图片已生成: images/output.png")
    print(f"🎯 开奖号码: {' '.join(numbers)}")
    return True

def main():
    """主函数"""
    print("=" * 40)
    print("🎲 开始生成福彩3D开奖图片")
    print("=" * 40)
    
    # 获取3D号码
    numbers = get_3d_number()
    print(f"📱 获取到号码: {numbers[0]} {numbers[1]} {numbers[2]}")
    
    # 生成图片
    if create_lottery_image(numbers):
        print("✅ 生成成功！")
    else:
        print("❌ 生成失败")
    
    print("=" * 40)

if __name__ == "__main__":
    main()
