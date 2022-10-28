import asyncio
import time
from io import BytesIO
from pathlib import Path
from typing import Tuple, Union

from loguru import logger
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from app.entities.game import BotGame
from app.util.network import general_request

base_path = Path(__file__).parent
font_path = "app/resource/font/OPPOSans-B.ttf"
avatar_size = 384
bg_size = (1920, 1080)
mahojin_size_offset = 55
avatar_xy = int(bg_size[1] * 0.15)
stroke_width = 5

_Ink = Union[str, int, Tuple[int, int, int], Tuple[int, int, int, int]]


def get_qlogo(id: int) -> bytes:
    return asyncio.run(general_request(url=f"http://q1.qlogo.cn/g?b=qq&nk={id}&s=640", _type="bytes"))


def progress_bar(w: int, h: int, progress: float, bg: _Ink = "black", fg: _Ink = "white") -> Image.Image:
    origin_w = w
    origin_h = h
    w *= 4
    h *= 4
    bar_canvase = Image.new("RGBA", (w, h), "#00000000")
    bar_draw = ImageDraw.Draw(bar_canvase)
    _draw_background_from_progress_bar(bar_draw, h, bg, w)
    # draw progress bar
    n_w = w * progress if progress <= 1 else w
    _draw_background_from_progress_bar(bar_draw, h, fg, n_w)
    return bar_canvase.resize((origin_w, origin_h), Image.LANCZOS)


def _draw_background_from_progress_bar(bar_draw, h, fill, arg3):
    # draw background
    bar_draw.ellipse((0, 0, h, h), fill=fill)
    bar_draw.ellipse((arg3 - h, 0, arg3, h), fill=fill)
    bar_draw.rectangle((h // 2, 0, arg3 - h // 2, h), fill=fill)


def get_time() -> str:
    return time.strftime("%Y/%m/%d/ %p%I:%M:%S", time.localtime())


def cut_text(
    font: ImageFont.FreeTypeFont,
    origin: str,
    chars_per_line: int,
):
    target = ""
    start_symbol = "[{<(【《（〈〖［〔“‘『「〝"
    end_symbol = ",.!?;:]}>)%~…，。！？；：】》）〉〗］〕”’～』」〞"
    line_width = chars_per_line * font.getlength("一")
    for i in origin.splitlines(False):
        if i == "":
            target += "\n"
            continue
        j = 0
        for ind, elem in enumerate(i):
            if i[j : ind + 1] == i[j:]:
                target += i[j : ind + 1] + "\n"
                continue
            elif font.getlength(i[j : ind + 1]) <= line_width:
                continue
            elif ind - j > 3:
                if i[ind] in end_symbol and i[ind - 1] != i[ind]:
                    target += i[j : ind + 1] + "\n"
                    j = ind + 1
                    continue
                elif i[ind] in start_symbol and i[ind - 1] != i[ind]:
                    target += i[j:ind] + "\n"
                    continue
            target += i[j:ind] + "\n"
            j = ind
    return target.rstrip()


def get_sign_image(
    uuid: str,
    qid: int,
    name: str,
    coin: int,
    intimacy: int,
    intimacy_level: int,
    consecutive_days: int,
    total_days: int,
) -> bytes:
    """生成签到图

    :param uuid: 用户UUID
    :param qid: QQ号
    :param name: QQ昵称/群昵称
    :param coin: 获得原石
    :param intimacy: 好感度
    :param intimacy_level: 好感度等级
    :param consecutive_days: 连续签到天数
    :param total_days: 累计签到天数
    """
    canvas = Image.new("RGB", bg_size, "#FFFFFF")
    draw = ImageDraw.Draw(canvas)

    qlogo = Image.open(BytesIO(get_qlogo(id=qid)))
    if bg_size[1] > bg_size[0]:
        qlogo1 = qlogo.resize((bg_size[1], bg_size[1]), Image.LANCZOS).filter(ImageFilter.GaussianBlur(radius=50))
        canvas.paste(qlogo1, ((bg_size[0] - bg_size[1]) // 2, 0))
    else:
        qlogo1 = qlogo.resize((bg_size[0], bg_size[0]), Image.LANCZOS).filter(ImageFilter.GaussianBlur(radius=50))
        canvas.paste(qlogo1, (0, (bg_size[1] - bg_size[0]) // 2))

    # 背景加一层黑
    mask = Image.new("RGBA", bg_size, "#00000055")
    canvas.paste(mask, (0, 0), mask.split()[3])

    # 魔法阵
    mahojin_size = avatar_size + 2 * mahojin_size_offset
    mahojin = Image.open(str(base_path.joinpath("magic.png")))
    mahojin = mahojin.resize((mahojin_size, mahojin_size), Image.LANCZOS)
    canvas.paste(
        mahojin,
        (avatar_xy - mahojin_size_offset, avatar_xy - mahojin_size_offset),
        mask=mahojin.split()[3],
    )

    # 头像描边
    stroke = Image.new(
        "RGBA",
        ((avatar_size + 2 * stroke_width) * 4, (avatar_size + 2 * stroke_width) * 4),
        "#00000000",
    )
    stroke_draw = ImageDraw.Draw(stroke)
    stroke_draw.ellipse(
        (
            0,
            0,
            (avatar_size + 2 * stroke_width) * 4,
            (avatar_size + 2 * stroke_width) * 4,
        ),
        fill="#000000bb",
    )
    stroke = stroke.resize((avatar_size + 2 * stroke_width, avatar_size + 2 * stroke_width), Image.LANCZOS)
    canvas.paste(
        stroke,
        (avatar_xy - stroke_width, avatar_xy - stroke_width),
        mask=stroke.split()[3],
    )

    # 圆形头像蒙版
    avatar_mask = Image.new("RGBA", (avatar_size * 4, avatar_size * 4), "#00000000")
    avatar_mask_draw = ImageDraw.Draw(avatar_mask)
    avatar_mask_draw.ellipse((0, 0, avatar_size * 4, avatar_size * 4), fill="#000000ff")
    avatar_mask = avatar_mask.resize((avatar_size, avatar_size), Image.LANCZOS)

    qlogo2 = qlogo.resize((avatar_size, avatar_size), Image.LANCZOS)
    canvas.paste(qlogo2, (avatar_xy, avatar_xy), avatar_mask)

    font_1 = ImageFont.truetype(font_path, size=60)
    font_2 = ImageFont.truetype(font_path, size=35)
    font_3 = ImageFont.truetype(font_path, size=45)
    qq = f"QQ：{qid}"
    uid = f"uid：{uuid}"
    need_intimacy = BotGame.get_intimacy_by_level(intimacy_level)

    impression = f"好感度：Lv{intimacy_level}  {intimacy} / {need_intimacy}"

    y = avatar_xy + 25

    draw.text((2 * avatar_xy + avatar_size, y), name, font=font_1, fill="#ffffff")
    y += font_1.getsize(name)[1] + 50
    draw.text((2 * avatar_xy + avatar_size, y), qq, font=font_2, fill="#ffffff")
    y += font_2.getsize(qq)[1] + 30
    draw.text((2 * avatar_xy + avatar_size, y), uid, font=font_2, fill="#ffffff")
    y += font_2.getsize(uid)[1] + 30
    draw.text((2 * avatar_xy + avatar_size, y), impression, font=font_2, fill="#ffffff")
    bar = progress_bar(
        font_2.getsize(impression)[0],
        6,
        intimacy / need_intimacy,
        fg="#80d0f1",
        bg="#00000055",
    )
    canvas.paste(
        bar,
        (2 * avatar_xy + avatar_size, y + font_2.getsize(impression)[1] + 10),
        mask=bar.split()[3],
    )

    gift_1 = f"+{coin}"
    temp = consecutive_days
    temp = min(temp, 7)
    gift_2 = f"+{BotGame.get_intimacy_by_consecutive_days(temp)}"
    y = avatar_xy + avatar_size + 100
    draw.text((avatar_xy + 30, y), f"共签到 {total_days} 天", font=font_3, fill="#ffffff")

    if total_days != 1 and consecutive_days != 1:
        y += font_3.getsize("签到")[1] + 20
        draw.text(
            (avatar_xy + 30, y),
            f"连续签到 {consecutive_days} 天",
            font=font_3,
            fill="#ffffff",
        )
    y += font_3.getsize("签到")[1] + 30
    datetime_text = f"现在是 {get_time()}，祝你天天开心捏~"

    primogem = Image.open(str(base_path.joinpath("primogems.png"))).convert("RGBA")
    primogem = primogem.resize((font_2.getsize(gift_1)[1], font_2.getsize(gift_1)[1]), Image.LANCZOS)
    canvas.paste(primogem, (avatar_xy + 30, y + 5), mask=primogem.split()[3])
    draw.text((avatar_xy + primogem.size[0] + 50, y), gift_1, font=font_2, fill="#ffffff")
    y += font_2.getsize(gift_1)[1] + 30

    intertwined_fate = Image.open(str(base_path.joinpath("intertwined_fate.png"))).convert("RGBA")
    intertwined_fate = intertwined_fate.resize((font_2.getsize(gift_2)[1], font_2.getsize(gift_2)[1]), Image.LANCZOS)
    canvas.paste(intertwined_fate, (avatar_xy + 30, y + 5), mask=intertwined_fate.split()[3])
    draw.text(
        (avatar_xy + intertwined_fate.size[0] + 50, y),
        gift_2,
        font=font_2,
        fill="#ffffff",
    )
    y += font_2.getsize(gift_2)[1] + 30

    # 一言背景
    hitokoto_bg = Image.new("RGBA", (1045, 390), "#00000000")
    hitokoto_bg_draw = ImageDraw.Draw(hitokoto_bg)
    hitokoto_bg_draw.rounded_rectangle((0, 0, 1045, 390), 20, fill="#00000030")
    hitokoto_bg = hitokoto_bg.resize((1045, 390), Image.LANCZOS)
    canvas.paste(
        hitokoto_bg,
        (2 * avatar_xy + avatar_size, avatar_xy + avatar_size + 55),
        mask=hitokoto_bg.split()[3],
    )

    try:
        hotokoto = asyncio.run(general_request("https://v1.hitokoto.cn/?encode=text&charset=utf-8&max_length=100"))
    except Exception as e:
        hotokoto = datetime_text
        logger.warning(e)
    font_4 = ImageFont.truetype(font_path, size=45)
    draw.text(
        (2 * avatar_xy + avatar_size + 50, avatar_xy + avatar_size + 100),
        cut_text(font_4, hotokoto, 21),
        font=font_4,
        fill="#ffffff",
        spacing=10,
    )  # 最大不要超过5行

    # footer
    font_5 = ImageFont.truetype(font_path, size=15)
    draw.text(
        (15, bg_size[1] - 55),
        f"madoka ©2021-2022\n{get_time()}",
        font=font_5,
        fill="#cccccc",
    )

    canvas.save(imageio := BytesIO(), format="JPEG", quality=98)
    return imageio.getvalue()
