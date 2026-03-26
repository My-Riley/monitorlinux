import base64
import random
import string
import uuid
from datetime import timedelta
from io import BytesIO

from fastapi import APIRouter, Request
from PIL import Image, ImageDraw

from config.enums import RedisInitKeyConfig
from utils.response_util import ResponseUtil

captchaController = APIRouter()


def generate_captcha_image(code: str):
    """生成验证码图片"""
    width, height = 120, 40
    image = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    # 绘制干扰线
    for _ in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

    # 绘制验证码
    for i, char in enumerate(code):
        x = 10 + i * 25
        y = random.randint(5, 15)
        draw.text((x, y), char, fill=(random.randint(0, 150), random.randint(0, 150), random.randint(0, 150)))

    # 转换为base64
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str


@captchaController.get("/captchaImage")
async def get_captcha_image(request: Request):
    """获取验证码"""
    # 生成纯数字验证码
    code = "".join(random.choices(string.digits, k=4))
    captcha_uuid = str(uuid.uuid4())

    # 存储到Redis
    await request.app.state.redis.set(
        f"{RedisInitKeyConfig.CAPTCHA_CODES.key}:{captcha_uuid}", code.lower(), ex=timedelta(minutes=2)
    )

    # 生成图片
    img_base64 = generate_captcha_image(code)

    return ResponseUtil.success(
        dict_content={"captchaEnabled": True, "uuid": captcha_uuid, "img": f"data:image/png;base64,{img_base64}"}
    )
