import os
import io
import json
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "Arial-Bold.ttf"
_font_cache = {}


def get_font(size):
    size = int(size) if size else 23
    if size in _font_cache:
        return _font_cache[size]
    try:
        font = ImageFont.truetype(FONT_PATH, size)
    except Exception:
        font = ImageFont.load_default()
    _font_cache[size] = font
    return font


def _has_position(field_cfg) -> bool:
    if not field_cfg:
        return False
    pos = field_cfg.get("position")
    return isinstance(pos, list) and len(pos) == 2


def _draw_field(draw, field_cfg, text, anchor="lm"):
    if not _has_position(field_cfg):
        return
    x, y = field_cfg["position"]
    font = get_font(field_cfg.get("font_size") or 23)
    color = field_cfg.get("color") or "white"
    try:
        draw.text((x, y), text, font=font, fill=color, anchor=anchor)
    except TypeError:
        draw.text((x, y), text, font=font, fill=color)


def get_available_backgrounds() -> list:
    if not os.path.exists("coords"):
        return []
    names = []
    for f in os.listdir("coords"):
        if f.endswith(".json"):
            name = f[:-5]
            if os.path.exists(f"backgrounds/{name}.png"):
                names.append(name)
    return sorted(names)


def render_image(bg_name, leaderboard, start_str, name_str, logo_bytes=None, match_details=None):
    bg_path = f"backgrounds/{bg_name}.png"
    coord_path = f"coords/{bg_name}.json"

    if not os.path.exists(bg_path):
        raise FileNotFoundError(f"❌ Không tìm thấy ảnh nền cho background: `{bg_name}`")
    if not os.path.exists(coord_path):
        raise FileNotFoundError(f"❌ Không tìm thấy file toạ độ cho background: `{bg_name}`")

    with open(coord_path, "r", encoding="utf-8") as f:
        coords = json.load(f)

    background = Image.open(bg_path).convert("RGBA")
    draw = ImageDraw.Draw(background)

    if name_str:
        _draw_field(draw, coords.get("custom_name"), name_str.upper())

    if start_str:
        try:
            dt = datetime.strptime(start_str, "%d/%m/%Y %H:%M")
            time_text = dt.strftime("%H:%M %d/%m")
        except Exception:
            time_text = start_str
        _draw_field(draw, coords.get("startTime"), time_text)

    generic_logo_img = None
    if logo_bytes:
        try:
            generic_logo_img = Image.open(io.BytesIO(logo_bytes)).convert("RGBA")
        except Exception:
            generic_logo_img = None

    for i in range(1, 51):
        slot = coords.get(f"top_{i}")
        if slot is None:
            continue

        if i - 1 >= len(leaderboard):
            continue
        team = leaderboard[i - 1]

        _draw_field(draw, slot.get("accountName"), str(team.get("displayName", "")))
        _draw_field(draw, slot.get("kill"), str(team.get("totalKill", 0)), anchor="mm")
        _draw_field(draw, slot.get("PTS"), str(team.get("totalPTS", 0)), anchor="mm")
        _draw_field(draw, slot.get("booyah"), str(team.get("totalBooyah", 0)), anchor="mm")
        _draw_field(draw, slot.get("score"), str(team.get("totalScore", 0)), anchor="mm")

        logo_cfg = slot.get("logo")
        if _has_position(logo_cfg) and generic_logo_img is not None:
            lx, ly = logo_cfg["position"]
            logo_size = logo_cfg.get("font_size") or 50
            resized = generic_logo_img.resize((logo_size, logo_size), Image.LANCZOS)
            background.paste(resized, (int(lx), int(ly)), resized)

    booyah_cfg = coords.get("booyah")
    if match_details and booyah_cfg:
        font = get_font(booyah_cfg.get("font_size") or 20)
        color = booyah_cfg.get("color") or "white"
        match_keys = sorted(
            (k for k in booyah_cfg if k.startswith("match_")),
            key=lambda k: int(k.split("_")[1]),
        )
        for idx, key in enumerate(match_keys):
            if idx >= len(match_details):
                break
            pos = booyah_cfg.get(key)
            if not isinstance(pos, list) or len(pos) != 2:
                continue
            booyah_name = match_details[idx].get("booyah")
            if not booyah_name or booyah_name == "Không có":
                continue
            try:
                draw.text((pos[0], pos[1]), str(booyah_name), font=font, fill=color, anchor="lm")
            except TypeError:
                draw.text((pos[0], pos[1]), str(booyah_name), font=font, fill=color)

    buffer = io.BytesIO()
    background.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer
