from io import BytesIO
from PIL import Image, ImageFont, ImageDraw

from .CutString import get_cut_str

font_file = 'app/resource/font/sarasa-mono-sc-semibold.ttf'
font = ImageFont.truetype(font_file, 32)


async def create_image(text: str, cut=64):
    imageio = BytesIO()
    cut_str = '\n'.join(get_cut_str(text, cut))
    textx, texty = font.getsize_multiline(cut_str)
    image = Image.new('RGB', (textx + 50, texty + 50), (242, 242, 242))
    draw = ImageDraw.Draw(image)
    draw.text((20, 20), cut_str, font=font, fill=(31, 31, 33))
    image.save(imageio, format="JPEG", quality=98)
    return imageio
