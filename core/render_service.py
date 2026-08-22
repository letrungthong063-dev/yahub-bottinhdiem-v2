"""
Render engine DUY NHẤT cho mọi bảng xếp hạng.

Không còn khái niệm "1 renderer / 1 background" — mọi background dùng chung
đúng 1 hàm render_image() ở đây. Muốn thêm bảng xếp hạng mới, chỉ cần thêm:
  - backgrounds/<tên>.png   (ảnh nền)
  - coords/<tên>.json        (toạ độ)
KHÔNG cần viết thêm code.

=== SCHEMA coords/<tên>.json ===
{
  "top_1": {
    "accountName": {"position": [x,y], "font_size": 23, "color": "#000d34"},
    "kill":        {"position": [x,y], "font_size": 23, "color": "#000d34"},
    "PTS":         {"position": [x,y], "font_size": 23, "color": "#000d34"},
    "booyah":      {"position": [x,y], "font_size": 23, "color": "#000d34"},
    "score":       {"position": [x,y], "font_size": 23, "color": "#000d34"},
    "logo": {"position": [x,y], "font_size": 50, "shape": "circle"}
  },
  "top_2": { ... }, ...

  "custom_name": {"position": [x,y], "font_size": 35, "color": "white"},
  "startTime":    {"position": [x,y], "font_size": 28, "color": "white"},

  "booyah": {
    "match_1": [x,y],
    "match_2": [x,y],
    "match_3": null,
    "font_size": 20,
    "color": "white"
  }
}

Nguyên tắc: CÓ "position" (mảng 2 phần tử) mới vẽ, KHÔNG có / rỗng thì bỏ
qua — không raise lỗi. Nhờ vậy JSON có thể khai báo dần dần (như hiện tại
bg3.json mới chỉ có top_1) mà không làm hỏng ảnh.

Field "logo.shape":
  - "circle" → crop tròn trước khi dán lên ảnh nền.
  - null (hoặc không có) → giữ nguyên hình ảnh gốc, không crop.
"""

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
    """Vẽ 1 field nếu có toạ độ; bỏ qua im lặng nếu không có."""
    if not _has_position(field_cfg):
        return
    x, y = field_cfg["position"]
    font = get_font(field_cfg.get("font_size") or 23)
    color = field_cfg.get("color") or "white"
    try:
        draw.text((x, y), text, font=font, fill=color, anchor=anchor)
    except TypeError:
        # Pillow cũ không hỗ trợ anchor
        draw.text((x, y), text, font=font, fill=color)


def _apply_shape(img: Image.Image, shape) -> Image.Image:
    """shape == 'circle' -> crop tròn. shape None (hoặc khác) -> giữ nguyên hình gốc."""
    if shape != "circle":
        return img
    size = min(img.size)
    img = img.crop((
        (img.width - size) // 2,
        (img.height - size) // 2,
        (img.width + size) // 2,
        (img.height + size) // 2,
    ))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
    out = Image.new("RGBA", (size, size))
    out.paste(img, (0, 0), mask)
    return out


def get_available_backgrounds() -> list:
    """1 background hợp lệ = có cả backgrounds/<tên>.png lẫn coords/<tên>.json."""
    if not os.path.exists("coords"):
        return []
    names = []
    for f in os.listdir("coords"):
        if f.endswith(".json"):
            name = f[:-5]
            if os.path.exists(f"backgrounds/{name}.png"):
                names.append(name)
    return sorted(names)


def render_image(bg_name, leaderboard, start_str, name_str, logo_bytes, logo_map=None, match_details=None):
    logo_map = logo_map or {}
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

    # ===== Tên giải đấu =====
    if name_str:
        _draw_field(draw, coords.get("custom_name"), name_str.upper())

    # ===== Thời gian bắt đầu =====
    if start_str:
        try:
            dt = datetime.strptime(start_str, "%d/%m/%Y %H:%M")
            time_text = dt.strftime("%H:%M %d/%m")
        except Exception:
            time_text = start_str
        _draw_field(draw, coords.get("startTime"), time_text)

    # ===== Cache ảnh logo đã load =====
    _logo_cache = {}

    def load_image(path):
        if path in _logo_cache:
            return _logo_cache[path]
        img = None
        try:
            if path and os.path.exists(path):
                img = Image.open(path).convert("RGBA")
        except Exception:
            img = None
        _logo_cache[path] = img
        return img

    generic_logo_img = None
    if logo_bytes:
        try:
            generic_logo_img = Image.open(io.BytesIO(logo_bytes)).convert("RGBA")
        except Exception:
            generic_logo_img = None

    # ===== Từng dòng bảng xếp hạng =====
    # Không giới hạn cố định top 15 — quét tới top_50, dòng nào coords không
    # định nghĩa thì bỏ qua (cho phép coords khai báo không liên tục).
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
        if _has_position(logo_cfg):
            lx, ly = logo_cfg["position"]
            logo_size = logo_cfg.get("font_size") or 50
            shape = logo_cfg.get("shape")

            team_logo = None
            logo_path = team.get("logoPath")
            if logo_path:
                team_logo = load_image(logo_path)
            if team_logo is None and generic_logo_img is not None:
                team_logo = generic_logo_img

            if team_logo:
                resized = team_logo.resize((logo_size, logo_size), Image.LANCZOS)
                final_logo = _apply_shape(resized, shape)
                background.paste(final_logo, (int(lx), int(ly)), final_logo)

    # ===== Danh sách Booyah từng trận =====
    # Lưu ý: khác với các field khác (mỗi field 1 object {position,font_size,color}
    # riêng), "booyah" ở đây là 1 object PHẲNG: mỗi match_N là toạ độ [x,y]
    # trực tiếp (hoặc null), dùng chung "font_size"/"color" cho mọi trận.
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
