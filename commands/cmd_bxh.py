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
from core import api_client

logger = logging.getLogger("yahub-bot")


class BxhCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="bxh", description="Tạo bảng xếp hạng từ ID-Game và thời gian")
    @app_commands.describe(
        accountid="id game của bạn",
        start_time="Thời gian bắt đầu (ngày/tháng/năm giờ:phút)",
        end_time="Thời gian kết thúc (ngày/tháng/năm giờ:phút)",
        background="Tên background, dùng /list_bg để xem tất cả",
        custom_name="Tên custom của bạn để hiển thị trên bảng xếp hạng",
        logo_custom="Ảnh logo hiển thị cho tất cả đội ",
        remove_match="Xóa trận theo số thứ tự, cách nhau bằng dấu phẩy (vd: 1,3)",
        team_names="Đặt tên đội theo ID (vd: 123456789012=Team A,987654321098=Team B)",
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
        champion_rush: int = 0,
    ):
        guild_id = str(interaction.guild_id)
        user_id = str(interaction.user.id)
        storage = self.bot.storage
        settings = self.bot.settings

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
            return await interaction.followup.send("❌ Bot chưa được kích hoạt ở server này, hãy liên hệ admin.")

        if user_id not in settings.BOT_OWNERS and not storage.is_public(guild_id) and not storage.is_allowed_user(guild_id, user_id):
            return await interaction.followup.send("❌ Bạn chưa được cấp quyền, hãy liên hệ admin.")

        try:
            id_to_name = parse_team_names(team_names)
        except ValueError as ve:
            return await interaction.followup.send(
                f"❌ team_names không hợp lệ. {ve}\nFormat đúng: `123456789012=Team A,987654321098=Team B`"
            )

        cooldown_key = f"{guild_id}_{user_id}"
        remaining = self.bot.cooldowns.remaining(cooldown_key)
        if remaining > 0:
            logger.info(f"[COOLDOWN] {interaction.user} còn {remaining}s")
            return await interaction.followup.send(f"⏳ Nhanh quá rồi, hãy đợi {remaining}s.")
        self.bot.cooldowns.set(cooldown_key, 5)

        try:
            fetch_start = time.time()
            start_ts = convert_to_timestamp(start_time)
            end_ts = convert_to_timestamp(end_time)

            try:
                skip_indexes = parse_remove_match(remove_match)
            except ValueError as e:
                logger.warning(f"[BXH] remove_match parse lỗi: {e}")
                return await interaction.followup.send("❌ Tham số remove_match không hợp lệ. Ví dụ: `1,3`")

            aggregator = TeamAggregator()
            match_details = []
            logo_bytes = None

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
                        aggregator.add_team_result(team, id_to_name, champion_rush)

            leaderboard = aggregator.build_leaderboard()

            if not leaderboard:
                return await interaction.followup.send("❌ Không tìm thấy dữ liệu trận đấu, hãy kiểm tra lại ID-Game và thời gian.")

            elapsed = round(time.time() - fetch_start, 1)
            so_doi = len(leaderboard)
            logger.info(f"[BXH] {interaction.user} | bg={background} | matches={len(match_details)} | teams={so_doi} | time={elapsed}s")

            info = "🔍 **Thông tin chung**\n"
            info += f"🎮 ID-Game: `{accountid}`\n"
            info += f"⏱️ Thời gian: `{elapsed}s`\n"
            info += f"🕐 Thời gian bắt đầu: `{start_time}`\n"
            info += f"🕐 Thời gian kết thúc: `{end_time}`\n"
            info += f"👥 Số đội: `{so_doi} đội`\n\n"

            info += f"🔍 **Danh sách {len(match_details)} trận:**\n"
            for m in match_details:
                status = "✅ Hoàn thành" if m['booyah'] != "Không có" else "⚠️ Chưa hoàn thành"
                info += f"📄 Trận {m['index']}:\n"
                info += f"|—🆔 MatchID: `{m['id']}`\n"
                info += f"|—🏆 Trạng thái: `{status}`\n"
                info += f"|—🥇 Booyah: `{m['booyah']}`\n"
            info += "└─────────────────"

            image = render_image(background, leaderboard, start_time, custom_name, logo_bytes, match_details=match_details)

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
