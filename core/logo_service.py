"""Đọc bộ logo đội đã lưu để dùng khi render BXH.

Lưu ý: logo được lưu NGUYÊN GỐC lúc upload (/add_logo), KHÔNG crop tròn ở
bước lưu. Việc quyết định hiển thị tròn hay giữ nguyên hình gốc do field
"shape" trong coords/<bg>.json quyết định lúc render (xem core/render_service.py).
"""

import os


def load_logo_map(key_logo: str) -> dict:
    """Đọc thư mục logos/<key_logo>/ -> {id_prefix: file_path}."""
    logo_map = {}
    logo_dir = f"logos/{key_logo}"
    if not os.path.exists(logo_dir):
        return logo_map
    for fname in os.listdir(logo_dir):
        name_part = fname.rsplit(".", 1)[0]
        logo_map[name_part] = os.path.join(logo_dir, fname)
    return logo_map
