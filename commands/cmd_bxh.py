import time
import logging
import traceback
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from core.time_utils import convert_to_timestamp
from core.text_parsing import parse_team_names, parse_remove_match
from core.team_aggregator import TeamAggregator
from core.render_service import render_image
from core.logo_service import load_logo_map
from core import api_client

logger = logging.getLogger("yahub-bot")


class BxhCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="bxh", description="Bảng xếp hạng")
    @app_commands.describe(
        accountid="id_game",
        start_time="Thời gian bắt đầu (ngày/tháng/năm giờ:phút)",
        end_time="Thời gian kết thúc (ngày/tháng/năm giờ:phút)",
        background="Tên background, dùng /list_bg để xem tất cả",
        custom_name="Tên custom hiển thị trên bảng",
        logo_custom="Ảnh logo hiển thị cho tất cả đội (không bắt buộc)",
        remove_match="Xóa trận theo số thứ tự, cách nhau bằng dấu phẩy (vd: 1,3)",
        team_names="Đặt tên đội theo ID (vd: 123456789012=Team A,987654321098=Team B)",
        add_logo="Nhập tên key_logo đã tạo (vd: custom1)",
        champion_rush="Ngưỡng điểm kích hoạt Champion Rush (vd: 50)",
    )
    async def bxh(
        self,
        interaction: discord.Interaction,
        accountid: str,
        start_time: str,
        end_time: str,
        background: str,
        custom_name: str = "",
        logo_custom: discord.Attachment = None,
        remove_match: str = "",
        team_names: str = "",
        add_logo: str = "",
        champion_rush: int = 0,
    ):
        guild_id = str(interaction.guild_id)
        user_id = str(interaction.user.id)
        storage = self.bot.storage
        settings = self.bot.settings

        # Bọc defer trong try/except để tránh lỗi 10062 (Unknown interaction)
        # Xảy ra khi Render free tier bị spin down, interaction hết hạn 3s trước khi bot kịp xử lý
        try:
            await interaction.response.defer()
        except discord.errors.NotFound:
            logger.warning(f"[BXH] Interaction hết hạn (Unknown interaction) - user: {interaction.user}")
            return
        except discord.errors.InteractionResponded:
            pass
        except Exception as e:
            logger.error(f"[BXH] Lỗi defer: {e}")
            return

        if not storage.is_enabled(guild_id):
            return await interaction.followup.send("❌ Bot chưa bật.")

        if user_id not in settings.BOT_OWNERS and not storage.is_public(guild_id) and not storage.is_allowed_user(guild_id, user_id):
            return await interaction.followup.send("❌ Bạn chưa được cấp quyền.")

        try:
            id_to_name = parse_team_names(team_names)
        except ValueError as ve:
            return await interaction.followup.send(
                f"❌ team_names không hợp lệ. {ve}\nFormat đúng: `123456789012=Team A,987654321098=Team B`"
            )

        logo_map = {}
        if add_logo:
            logo_map = load_logo_map(add_logo)
            if not logo_map:
                return await interaction.followup.send(f"❌ Không tìm thấy bộ logo `{add_logo}`.")

        cooldown_key = f"{guild_id}_{user_id}"
        remaining = self.bot.cooldowns.remaining(cooldown_key)
        if remaining > 0:
            logger.info(f"[COOLDOWN] {interaction.user} còn {remaining}s")
            return await interaction.followup.send(f"⏳ Vui lòng chờ {remaining}s.")
        self.bot.cooldowns.set(cooldown_key, 10)

        try:
            fetch_start = time.time()
            start_ts = convert_to_timestamp(start_time)
            end_ts = convert_to_timestamp(end_time)

            try:
                skip_indexes = parse_remove_match(remove_match)
            except ValueError as e:
                logger.warning(f"[BXH] remove_match parse lỗi: {e}")
                return await interaction.followup.send("❌ Tham số remove_match không hợp lệ. Ví dụ: `1,3`")

            logo_bytes = None
            aggregator = TeamAggregator()
            match_details = []

            async with aiohttp.ClientSession() as session:
                if logo_custom:
                    async with session.get(logo_custom.url) as logo_response:
                        if logo_response.status == 200:
                            logo_bytes = await logo_response.read()

                matches = await api_client.find_matches(session, settings.headers, accountid, start_ts, end_ts)

                if skip_indexes:
                    matches = [m for i, m in enumerate(matches, 1) if i not in skip_indexes]

                for idx, match in enumerate(matches):
                    detail = await api_client.get_match_detail(session, settings.headers, match["id"])
                    ranks = detail.get("ranks", [])

                    booyah_team = "Không có"
                    for team in ranks:
                        if team.get("booyah") == 1:
                            name = (team.get("teamName") or "").strip()
                            if not name:
                                acc_names = team.get("accountNames") or []
                                name = acc_names[0].strip() if acc_names else ""
                            booyah_team = name if name else "Unknown"
                            break

                    match_details.append({
                        "index": idx + 1,
                        "id": match["id"],
                        "booyah": booyah_team,
                        "success": bool(ranks),
                    })

                    if not ranks:
                        continue

                    for team in ranks:
                        aggregator.add_team_result(team, id_to_name, logo_map, champion_rush)

            leaderboard = aggregator.build_leaderboard()

            if not leaderboard:
                return await interaction.followup.send("❌ Không tìm thấy dữ liệu.")

            elapsed = round(time.time() - fetch_start, 1)
            so_doi = len(leaderboard)
            logger.info(f"[BXH] {interaction.user} | bg={background} | matches={len(match_details)} | teams={so_doi} | time={elapsed}s")

            info = "🔍 **Thông tin chung**\n"
            info += f"🎮 ID-Game: `{accountid}`\n"
            info += f"⏱️  Time: `{elapsed}s`\n"
            info += f"🕐 Start-time: `{start_time}`\n"
            info += f"🕐 End-time: `{end_time}`\n"
            info += f"👥 Team: `{so_doi} đội`\n\n"

            info += f"🔍 **Danh sách {len(match_details)} trận:**\n"
            for m in match_details:
                status = "✅ success" if m["success"] else "❌ Thất bại"
                info += f"📄 Number {m['index']}:\n"
                info += f"🆔 MatchID: `{m['id']}`\n"
                info += f"🚦 Status: {status}\n"
                info += f"🥇 Booyah: `{m['booyah']}`\n"
            info += "└─────────────────"

            image = render_image(background, leaderboard, start_time, custom_name, logo_bytes, logo_map, match_details=match_details)

            await interaction.followup.send(
                content=info,
                file=discord.File(fp=image, filename="leaderboard.png"),
            )

        except FileNotFoundError as e:
            logger.error(f"[BXH] {e}")
            await interaction.followup.send(str(e))
        except Exception as e:
            logger.error(f"[BXH] {traceback.format_exc()}")
            await interaction.followup.send(f"❌ Lỗi: `{type(e).__name__}: {e}`")


async def setup(bot):
    await bot.add_cog(BxhCog(bot))
