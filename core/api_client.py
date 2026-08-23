import json

FIND_MATCH_URL = "https://congdong.ff.garena.vn/league-score-api/player/find-match"
MATCH_DETAIL_URL = "https://congdong.ff.garena.vn/league-score-api/match"


async def _read_json_response(res) -> dict:
    body = await res.text()
    if not body.strip():
        raise RuntimeError(f"API trả về nội dung rỗng (HTTP {res.status}). Cookie có thể đã hết hạn.")
    try:
        data = json.loads(body)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"API trả về dữ liệu không phải JSON (HTTP {res.status}). Cookie có thể đã hết hạn."
        ) from error
    if not isinstance(data, dict):
        raise RuntimeError("API trả về JSON không đúng định dạng object.")
    return data


async def find_matches(session, headers, account_id: str, start_ts: int, end_ts: int) -> list:
    async with session.post(
        FIND_MATCH_URL,
        json={"accountId": account_id, "startTime": start_ts, "endTime": end_ts},
        headers=headers,
    ) as res:
        data = await _read_json_response(res)
    return data.get("matches", [])


async def get_match_detail(session, headers, match_id) -> dict:
    async with session.post(
        MATCH_DETAIL_URL,
        json={"matchId": match_id},
        headers=headers,
    ) as res:
        data = await _read_json_response(res)
    return data.get("match", {})
