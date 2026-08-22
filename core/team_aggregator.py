"""
Logic ghép đội theo teamName / theo ID người chơi, cộng dồn điểm nhiều trận.

Đây là phần quan trọng nhất về mặt nghiệp vụ — tách riêng khỏi Discord để
dễ kiểm thử độc lập (không cần giả lập Discord API).
"""


class TeamAggregator:
    def __init__(self):
        self.team_map: dict = {}
        self.cr_winner = None  # key của đội vô địch Champion Rush (nếu có)

    def add_team_result(
        self,
        team: dict,
        id_to_name: dict,
        logo_map: dict,
        champion_rush: int = 0,
    ):
        """Cộng dồn kết quả của 1 đội trong 1 trận vào team_map."""
        score = team.get("score", 0)
        kill = team.get("kill", 0)
        booyah = 1 if team.get("booyah") == 1 else 0
        team_name = team.get("teamName")
        current_ids = team.get("playerAccountIds", [])

        # Tìm custom name và logo theo ID (so sánh bỏ 2 số cuối)
        custom_display = None
        custom_logo_path = None
        for cid in current_ids:
            cid_prefix = str(cid)[:-2] if len(str(cid)) >= 3 else str(cid)
            if custom_display is None and cid_prefix in id_to_name:
                custom_display = id_to_name[cid_prefix]
            if custom_logo_path is None and cid_prefix in logo_map:
                custom_logo_path = logo_map[cid_prefix]

        if team_name and team_name.strip():
            self._merge_by_name(team_name.strip(), score, kill, booyah,
                                 current_ids, custom_display, custom_logo_path,
                                 champion_rush)
        else:
            self._merge_by_ids(team, score, kill, booyah, current_ids,
                                custom_display, custom_logo_path, champion_rush)

    def _merge_by_name(self, team_name, score, kill, booyah, current_ids,
                        custom_display, custom_logo_path, champion_rush):
        keyname = "NAME_" + team_name

        if keyname not in self.team_map:
            self.team_map[keyname] = {
                "displayName": custom_display or team_name,
                "accountIds": current_ids,
                "totalScore": 0,
                "totalKill": 0,
                "totalBooyah": 0,
                "logoPath": custom_logo_path,
            }
        elif custom_display and not self.team_map[keyname].get("customized"):
            self.team_map[keyname]["displayName"] = custom_display
            self.team_map[keyname]["customized"] = True

        self.team_map[keyname]["totalScore"] += score
        self.team_map[keyname]["totalKill"] += kill
        self.team_map[keyname]["totalBooyah"] += booyah

        self._check_champion_rush(keyname, score, booyah, champion_rush)

    def _merge_by_ids(self, team, score, kill, booyah, current_ids,
                       custom_display, custom_logo_path, champion_rush):
        found_key = None

        for keyname, data in self.team_map.items():
            existing_ids = data.get("accountIds", [])
            common = [i for i in existing_ids if i in current_ids]

            # FIX: chỉ cần trùng >= 1 ID là đủ để nhận diện cùng 1 đội.
            # Ngưỡng >= 2 (bản cũ) khiến đội chỉ còn 3 người (thiếu 1 người
            # so với đội gốc 4 người) dễ bị coi là đội mới nếu phần trùng < 2,
            # dẫn tới điểm bị tách ra thay vì cộng dồn vào đội chính.
            if len(common) >= 1:
                found_key = keyname
                break

        if found_key:
            data = self.team_map[found_key]
            if custom_display and not data.get("customized"):
                data["displayName"] = custom_display
                data["customized"] = True
            data["totalScore"] += score
            data["totalKill"] += kill
            data["totalBooyah"] += booyah

            # FIX: cập nhật accountIds thành hợp (union) để đội "học" thêm
            # ID mới khi có thay người/sub, giúp các trận sau khớp đúng hơn.
            merged_ids = list(data.get("accountIds", []))
            for _id in current_ids:
                if _id not in merged_ids:
                    merged_ids.append(_id)
            data["accountIds"] = merged_ids

            self._check_champion_rush(found_key, score, booyah, champion_rush)
        else:
            new_key = "IDS_" + "-".join(sorted(map(str, current_ids)))
            account_names = team.get("accountNames") or []
            fallback_name = account_names[0] if account_names else ""
            self.team_map[new_key] = {
                "displayName": custom_display or fallback_name,
                "accountIds": current_ids,
                "totalScore": score,
                "totalKill": kill,
                "totalBooyah": booyah,
                "logoPath": custom_logo_path,
            }
            if custom_display:
                self.team_map[new_key]["customized"] = True
            # Đội mới tạo không thể đã đạt ngưỡng Champion Rush trước đó.

    def _check_champion_rush(self, keyname, score, booyah, champion_rush):
        if champion_rush > 0 and self.cr_winner is None and booyah == 1:
            score_before = self.team_map[keyname]["totalScore"] - score
            if score_before >= champion_rush:
                self.cr_winner = keyname

    def build_leaderboard(self) -> list:
        """Tính PTS, sắp xếp bảng xếp hạng, áp dụng Champion Rush nếu có."""
        # PTS (điểm vị trí) = tổng điểm - tổng điểm kill.
        # Trường tính toán (derived field), không lấy từ API — tính 1 lần ở
        # đây sau khi đã cộng dồn xong toàn bộ các trận.
        for data in self.team_map.values():
            data["totalPTS"] = data["totalScore"] - data["totalKill"]

        leaderboard = sorted(
            self.team_map.values(),
            key=lambda x: (x["totalScore"], x["totalBooyah"], x["totalKill"]),
            reverse=True,
        )

        # Champion Rush: đội đạt ngưỡng điểm TRƯỚC rồi Booyah trận tiếp → lên top 1
        if self.cr_winner and self.cr_winner in self.team_map:
            cr_team = self.team_map[self.cr_winner]
            leaderboard = [cr_team] + [t for t in leaderboard if t is not cr_team]

        return leaderboard
