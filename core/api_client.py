"""Gọi API tính điểm cộng đồng Garena FF."""

FIND_MATCH_URL = "https://congdong.ff.garena.vn/league-score-api/player/find-match"
MATCH_DETAIL_URL = "https://congdong.ff.garena.vn/league-score-api/match"


async def find_matches(session, headers, account_id: str, start_ts: int, end_ts: int) -> list:
    async with session.post(
        FIND_MATCH_URL,
        json={"accountId": account_id, "startTime": start_ts, "endTime": end_ts},
        headers=headers,
    ) as res:
        data = await res.json(content_type=None)
    return data.get("matches", [])


async def get_match_detail(session, headers, match_id) -> dict:
    async with session.post(
        MATCH_DETAIL_URL,
        json={"matchId": match_id},
        headers=headers,
    ) as res:
        data = await res.json(content_type=None)
    return data.get("match", {})
