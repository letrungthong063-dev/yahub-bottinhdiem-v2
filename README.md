# 🎮 Yahub Bot Tính Điểm

Bot Discord tự động tạo bảng xếp hạng từ dữ liệu trận đấu Free Fire.

## ✨ Tính năng

- 🏆 Tạo bảng xếp hạng theo ID game và thời gian thi đấu.
- 👥 Tổng hợp điểm theo đội, đặt tên đội tùy chỉnh.
- 🗑️ Bỏ qua các trận không mong muốn.
- 🔥 Thiết lập ngưỡng Champion Rush.
- 🔐 Phân quyền theo server: public hoặc private.
- ⚡ Cooldown chống spam và health check cho Render.

## 🚀 Cài đặt

### Yêu cầu

- Python 3.10+
- Discord Bot Token
- Cookie hợp lệ của web cộng đồng Free Fire

### Chạy local

```bash
git clone https://github.com/letrungthong063-dev/yahub-bottinhdiem-v2.git
cd yahub-bottinhdiem-v2
python -m venv .venv
```

Kích hoạt trên Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Cài thư viện và khởi động:

```bash
pip install -r requirements.txt
python yahub.py
```

## 🔑 Cấu hình

Sao chép `.env.example` thành `.env` ở thư mục gốc. **Không commit file `.env` lên GitHub.**

```env
TOKEN=your_discord_bot_token
CLIENT_ID=your_discord_application_id
BOT_OWNERS=your_discord_user_id
COOKIE=your_garena_cookie
```


## 🤖 Slash commands

| Lệnh | Mô tả |
| --- | --- |
| `/bxh` | Tạo bảng xếp hạng |
| `/list_bg` | Xem background có sẵn |
| `/enable` / `/disable` | Bật hoặc tắt bot trong server |
| `/public` / `/private` | Mở công khai hoặc giới hạn quyền dùng bot |
| `/grant @user` / `/revoke @user` | Cấp hoặc thu hồi quyền người dùng |
| `/list` | Xem danh sách người được cấp quyền |
| `/upt` | Xem uptime, latency và số server |

Các lệnh quản trị chỉ dành cho user có trong `BOT_OWNERS`.


## 🖌️ Thêm background

Một background cần có hai file cùng tên:

```text
backgrounds/<name>.png
coords/<name>.json
```

File JSON định nghĩa vị trí, cỡ chữ và màu sắc trên ảnh. `Arial-Bold.ttf` là font mặc định của hệ thống render.

## ☁️ Deploy trên Render

`render.yaml` đã cấu hình sẵn worker:

```text
Build: pip install -r requirements.txt
Start: python yahub.py
```

Thêm các Environment Variables trong Render:

| Biến | Bắt buộc | Nội dung |
| --- | --- | --- |
| `TOKEN` | ✅ | Discord Bot Token |
| `COOKIE` | ✅ | Cookie gọi API Garena |
| `BOT_OWNERS` | Khuyến nghị | Discord user ID quản trị |
| `CLIENT_ID` | Không | Discord Application ID |

Không đặt token hoặc cookie trực tiếp trong `render.yaml`.

## 🛡️ Bảo mật

- Không public `.env`, token, cookie hoặc session cookie.
- Nếu thông tin xác thực từng bị lộ, hãy thu hồi và tạo mới ngay.
- Không public `logs.json` và `permissions.json` từ môi trường thật vì chúng có thể chứa Discord ID.
- Thêm `.env`, `__pycache__/`, `.venv/` và file log vào `.gitignore`.
- Chỉ phân phối font/background khi bạn có quyền sử dụng.

## 📁 Cấu trúc

```text
backgrounds/       Ảnh background
commands/          Slash commands
coords/            Tọa độ và kiểu chữ
core/              API, render, storage, cấu hình
requirements.txt   Dependencies
render.yaml        Cấu hình Render
yahub.py           Entry point
```

## ⚠️ Lưu ý

Bot phụ thuộc vào API và cookie của dịch vụ bên ngoài. Cookie hết hạn hoặc API thay đổi có thể khiến chức năng tra cứu ngừng hoạt động. Dữ liệu quyền và log hiện được lưu trong file JSON local.

## 📄 License

Dự án được phát hành theo [MIT License](LICENSE).
