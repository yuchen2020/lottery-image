#!/usr/bin/env python3
import requests
import re
from PIL import Image, ImageDraw, ImageFont
import urllib3
import traceback

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

WIDTH = 250
HEIGHT = 128
OUTPUT_FILE = "lottery_result.png"

# 字体适配 Actions 的 Ubuntu 环境
def get_font(size):
    paths = ["/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except:
            continue
    return ImageFont.load_default()

font_title = get_font(12)
font_period = get_font(10)
font_num = get_font(15)

# 获取数据（备用接口）
def fetch_lottery(name):
    url = f"http://www.zhcw.com/json/kj/kj_{name}.json"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.encoding = "utf-8"
    match = re.search(r'callback\((\{.*\})\)', resp.text, re.DOTALL)
    if not match:
        raise Exception("数据解析失败")
    data = requests.utils.json.loads(match.group(1))
    item = data["data"][0]
    return item.get("code"), item.get("red"), item.get("blue")

# 解析号码
def parse_ssq(red_str, blue_str):
    reds = [n.strip().zfill(2) for n in re.split(r'[, ]', red_str) if n.strip()][:6]
    blue = blue_str.strip().zfill(2) if blue_str else ""
    return reds, blue

def parse_3d(red_str):
    return [n.strip() for n in re.split(r'[, ]', red_str) if n.strip()][:3]

# 绘制函数
def draw_row(draw, title, period, balls, blue, y_start):
    draw.text((8, y_start + 2), title, fill=0, font=font_title)
    period_text = f"第{period}期"
    title_w = draw.textbbox((8, y_start + 2), title, font=font_title)[2]
    draw.text((8 + title_w + 8, y_start + 3), period_text, fill=0, font=font_period)

    num_y = y_start + 22
    r = 10
    gap = 2
    x_start = 10

    balls_list = [(b, "red") for b in balls]
    if blue:
        balls_list.append((blue, "blue"))

    for i, (num, color_type) in enumerate(balls_list):
        cx = x_start + i * (2 * r + gap) + r
        cy = num_y + r
        fill = (220, 0, 0) if color_type == "red" else (0, 0, 200)
        text_color = 0 if color_type == "red" else 255
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fill)
        tw, th = draw.textbbox((0,0), num, font=font_num)
        draw.text((cx-tw/2, cy-th/2-1), num, fill=text_color, font=font_num)

# 主函数（带异常捕获）
def create_image():
    print("获取双色球数据...")
    ssq_period, ssq_red, ssq_blue = fetch_lottery("ssq")
    print("获取福彩3D数据...")
    td_period, td_red, _ = fetch_lottery("3d")

    ssq_balls, blue = parse_ssq(ssq_red, ssq_blue)
    td_balls = parse_3d(td_red)

    img = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw_row(draw, "双色球", ssq_period, ssq_balls, blue, y_start=5)
    draw_row(draw, "福彩3D", td_period, td_balls, None, y_start=69)
    img.save(OUTPUT_FILE, "PNG")
    print(f"✅ 图片已保存为 {OUTPUT_FILE}")

if __name__ == "__main__":
    try:
        create_image()
    except Exception as e:
        print(f"❌ 脚本出错: {e}")
        traceback.print_exc()
        # 出错时也生成一张占位图，避免文件为空
        img = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "数据获取失败", fill=0, font=font_title)
        img.save(OUTPUT_FILE, "PNG")
