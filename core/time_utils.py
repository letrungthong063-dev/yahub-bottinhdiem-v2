from datetime import datetime, timezone, timedelta

VN_TZ = timezone(timedelta(hours=7))


def convert_to_timestamp(date_str: str) -> int:
    dt = datetime.strptime(date_str, "%d/%m/%Y %H:%M")
    dt = dt.replace(tzinfo=VN_TZ)
    return int(dt.timestamp())
