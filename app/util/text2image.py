from io import BytesIO

from PIL import Image, ImageFont, ImageDraw

from .CutString import get_cut_str
from .tools import to_thread

font_file = 'app/resource/font/sarasa-mono-sc-semibold.ttf'
font = ImageFont.truetype(font_file, 32)


async def create_image(text: str, cut=64) -> bytes:
    """文本转图片（自动使用子线程）

    :param text: 文本
    :param cut: 自动断行长度
    """
    imageio: bytes = await to_thread(create_image_thread, text, cut)
    return imageio


def create_image_thread(text: str, cut=64) -> bytes:
    """文本转图片

    :param text: 文本
    :param cut: 自动断行长度
    """
    imageio = BytesIO()
    cut_str = '\n'.join(get_cut_str(text.replace('\t', '    '), cut))
    textx, texty = font.getsize_multiline(cut_str)
    image = Image.new('RGB', (textx + 50, texty + 50), (242, 242, 242))
    draw = ImageDraw.Draw(image)
    draw.text((20, 20), cut_str, font=font, fill=(31, 31, 33))
    image.save(imageio, format="JPEG", quality=98)
    return imageio.getvalue()
