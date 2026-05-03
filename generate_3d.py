import requests
from PIL import Image, ImageDraw, ImageFont

# ===================== 路径设置 =====================
TEMPLATE_PATH = "template.png"
OUTPUT_PATH = "3d_result.png"
FONT_PATH = "simhei.ttf"
# ====================================================

def get_latest_3d_result():
    try:
        url = "http://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice?name=3d&issueCount=1"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        result = data["result"][0]
        numbers = result["code"]
        date = result["date"]
        return numbers, date
    except:
        return "000", "获取失败"

def generate_image(numbers, date):
    img = Image.open(TEMPLATE_PATH)
    draw = ImageDraw.Draw(img)

    # 字体设置
    font_num = ImageFont.truetype(FONT_PATH, 24)  # 数字字体，适配圆形
    font_date = ImageFont.truetype(FONT_PATH, 12)

    # 三个数字的位置（圆形中心）
    centers = [(70, 60), (125, 60), (180, 60)]
    circle_radius = 20  # 圆形半径，根据你的模板调整

    # 画红底黑字圆形数字
    for i, center in enumerate(centers):
        # 画红色圆形
        draw.ellipse(
            [
                center[0] - circle_radius,
                center[1] - circle_radius,
                center[0] + circle_radius,
                center[1] + circle_radius
            ],
            fill="red"
        )
        # 用getbbox获取文字尺寸，兼容新版本Pillow
        bbox = font_num.getbbox(numbers[i])
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        text_x = center[0] - text_w / 2
        text_y = center[1] - text_h / 2
        draw.text((text_x, text_y), numbers[i], font=font_num, fill="black")

    # 时间位置（居中偏下，不超出）
    draw.text((90, 105), f"更新: {date}", font=font_date, fill="black")

    img.save(OUTPUT_PATH)
    print("生成成功！文件：3d_result.png")

if __name__ == "__main__":
    numbers, date = get_latest_3d_result()
    generate_image(numbers, date)