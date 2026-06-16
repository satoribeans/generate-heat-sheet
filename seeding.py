from utils import time_to_seconds

def seed_swimmers(swimmers, heat_size, order="fast_to_slow"):

    sorted_swimmers = sorted(
        swimmers,
        key=lambda x: time_to_seconds(x.get("seed_time"))
    )

    if order == "slow_to_fast":
        sorted_swimmers.reverse()

    heat_num = 1
    result = []

    for i, s in enumerate(sorted_swimmers):
        s = dict(s)
        s["heat"] = heat_num
        result.append(s)

        if (i + 1) % heat_size == 0:
            heat_num += 1

    return result


def build_heat_sheet(events, heat_size, order, is_long_event):
    heat_sheet = []

    for e in events:
        heat_sheet.append({
            "number": e["number"],
            "name": e["name"],
            "heats": seed_event(e, lanes=heat_size)
        })

    return heat_sheet
