def parse_team_names(team_names: str) -> dict:
    id_to_name = {}
    if not team_names:
        return id_to_name

    for part in team_names.split(","):
        part = part.strip()
        if "=" not in part:
            raise ValueError(f"Sai format: `{part}`")
        raw_id, raw_name = part.split("=", 1)
        raw_id = raw_id.strip()
        name = raw_name.strip()
        if not name:
            raise ValueError(f"Tên đội trống tại ID: `{raw_id}`")
        if len(raw_id) < 3:
            raise ValueError(f"ID quá ngắn: `{raw_id}`")
        id_to_name[raw_id[:-2]] = name

    return id_to_name


def parse_remove_match(remove_match: str) -> set:
    if not remove_match:
        return set()
    try:
        return set(int(x.strip()) for x in remove_match.split(","))
    except Exception as e:
        raise ValueError(str(e))
