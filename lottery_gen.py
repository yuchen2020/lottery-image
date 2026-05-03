#!/usr/bin/env python3
import requests
import re
from PIL import Image, ImageDraw, ImageFont
import traceback
import platform

WIDTH = 250
HEIGHT = 128
OUTPUT_FILE = "lottery_result.png"

# ==================== 字体兼容（Windows + Linux） ====================
def get_font(size):
    system = platform.system()
    if system == "Windows":
        paths = ["C:/Windows/Fonts/simhei.ttf", "C:/Windows/Fonts/msyh.ttc"]
    else:
        paths = ["/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"]
    for p in paths:
        try:
            return ImageFont.truetype(p, size=size)
        except:
            continue
    return ImageFont.load_default()

font_title = get_font(12)
font_period = get_font(10)
font_num = get_font(15)

# ==================== 数据获取（优先官网，失败用备用） ====================
def fetch_lottery(name):
    try:
        # 1. 优先用官网接口
        url = "https://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice"
        params = {"name": name, "pageNo": 1, "pageSize": 1}
        headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.cwl.gov.cn/"}
        resp = requests.get(url, params=params, headers=headers, timeout=15, verify=False)
        resp.raise_for_status()
        data = resp.json()
        if data["state"] == 0 and data["result"]:
            item = data["result"][0]
            return item["code"], item["red"], item.get("blue", "")
    except Exception as e:
        print(f"官网接口失败: {e}")

    try:
        # 2. 备用接口
        url = f"http://www.zhcw.com/json/kj/kj_{name}.json"
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10, verify=False)
        resp.encoding = "utf-8"
        match = re.search(r'callback\((.*)\)', resp.text, re.DOTALL)
        if match:
            data = requests.utils.json.loads(match.group(1))
            item = data["data"][0]
            return item["code"], item["red"], item.get("blue", "")
    except Exception as e:
        print(f"备用接口失败: {e}")

    raise Exception("所有接口均失败")

# ==================== 绘制（强制生成图片） ====================
def draw_row(draw, title, period, balls, blue, y_start):
    draw.text((8, y_start+2), title, fill=0, font=font_title)
    period_text = f"第{period}期"
    title_w = draw.textbbox((8, y_start+2), title, font=font_title)[2]
    draw.text((8+title_w+8, y_start+3), period_text, fill=0, font=font_period)

    num_y = y_start + 22
    r = 10
    gap = 2
    x_start = 10

    balls_list = [(b, "red") for b in balls]
    if blue:
        balls_list.append((blue, "blue"))

    for i, (num, color_type) in enumerate(balls_list):
        cx = x_start + i*(2*r + gap) + r
        cy = num_y + r
        fill = (220, 0, 0) if color_type == "red" else (0, 0, 200)
        text_color = 0 if color_type == "red" else 255
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fill)
        bbox = draw.textbbox((0,0), num, font=font_num)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
        draw.text((cx-tw/2, cy-th/2-1), num, fill=text_color, font=font_num)

def main():
    print("脚本开始执行...")
    try:
        print("获取双色球数据...")
        ssq_period, ssq_red, ssq_blue = fetch_lottery("ssq")
        print("获取福彩3D数据...")
        td_period, td_red, _ = fetch_lottery("3d")

        print("解析号码...")
        ssq_balls = [n.strip().zfill(2) for n in re.split(r'[, ]', ssq_red) if n.strip()][:6]
        blue = ssq_blue.strip().zfill(2) if ssq_blue else ""
        td_balls = [n.strip() for n in re.split(r'[, ]', td_red) if n.strip()][:3]

        print("生成图片...")
        img = Image.new("RGB", (WIDTH, HEIGHT), (255,255,255))
        draw = ImageDraw.Draw(img)
        draw_row(draw, "双色球", ssq_period, ssq_balls, blue, 5)
        draw_row(draw, "福彩3D", td_period, td_balls, None, 69)
        img.save(OUTPUT_FILE)
        print(f"✅ 成功生成: {OUTPUT_FILE}")
    except Exception as e:
        print(f"❌ 脚本失败: {e}")
        traceback.print_exc()
        # 兜底：强制生成占位图
        img = Image.new("RGB", (WIDTH, HEIGHT), (255,255,255))
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "数据获取失败", fill=0, font=font_title)
        img.save(OUTPUT_FILE)
        print(f"⚠️ 已生成兜底图片: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
