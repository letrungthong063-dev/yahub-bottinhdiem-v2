class TeamAggregator:
    def __init__(self):
        self.team_map: dict = {}
        self.cr_winner = None

    def add_team_result(
        self,
        team: dict,
        id_to_name: dict,
        champion_rush: int = 0,
    ):
        score = team.get("score", 0)
        kill = team.get("kill", 0)
        booyah = 1 if team.get("booyah") == 1 else 0
        team_name = team.get("teamName")
        current_ids = team.get("playerAccountIds", [])

        custom_display = None
        for cid in current_ids:
            cid_prefix = str(cid)[:-2] if len(str(cid)) >= 3 else str(cid)
            if custom_display is None and cid_prefix in id_to_name:
                custom_display = id_to_name[cid_prefix]

        if team_name and team_name.strip():
            self._merge_by_name(team_name.strip(), score, kill, booyah,
                                 current_ids, custom_display, champion_rush)
        else:
            self._merge_by_ids(team, score, kill, booyah, current_ids,
                                custom_display, champion_rush)

    def _merge_by_name(self, team_name, score, kill, booyah, current_ids,
                        custom_display, champion_rush):
        keyname = "NAME_" + team_name

        if keyname not in self.team_map:
            self.team_map[keyname] = {
                "displayName": custom_display or team_name,
                "accountIds": current_ids,
                "totalScore": 0,
                "totalKill": 0,
                "totalBooyah": 0,
            }
        elif custom_display and not self.team_map[keyname].get("customized"):
            self.team_map[keyname]["displayName"] = custom_display
            self.team_map[keyname]["customized"] = True

        self.team_map[keyname]["totalScore"] += score
        self.team_map[keyname]["totalKill"] += kill
        self.team_map[keyname]["totalBooyah"] += booyah

        self._check_champion_rush(keyname, score, booyah, champion_rush)

    def _merge_by_ids(self, team, score, kill, booyah, current_ids,
                       custom_display, champion_rush):
        found_key = None

        for keyname, data in self.team_map.items():
            existing_ids = data.get("accountIds", [])
            common = [i for i in existing_ids if i in current_ids]

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
            }
            if custom_display:
                self.team_map[new_key]["customized"] = True
    def _check_champion_rush(self, keyname, score, booyah, champion_rush):
        if champion_rush > 0 and self.cr_winner is None and booyah == 1:
            score_before = self.team_map[keyname]["totalScore"] - score
            if score_before >= champion_rush:
                self.cr_winner = keyname

    def build_leaderboard(self) -> list:
        for data in self.team_map.values():
            data["totalPTS"] = data["totalScore"] - data["totalKill"]

        leaderboard = sorted(
            self.team_map.values(),
            key=lambda x: (x["totalScore"], x["totalBooyah"], x["totalKill"]),
            reverse=True,
        )

        if self.cr_winner and self.cr_winner in self.team_map:
            cr_team = self.team_map[self.cr_winner]
            leaderboard = [cr_team] + [t for t in leaderboard if t is not cr_team]

        return leaderboard
