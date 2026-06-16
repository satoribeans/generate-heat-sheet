from utils import time_to_seconds, is_long_event


def seed_event(event, lanes=8, order="fast_to_slow"):
    swimmers = sorted(
        event["swimmers"],
        key=lambda x: time_to_seconds(x["seed_time"])
    )

    if order == "slow_to_fast":
        swimmers.reverse()

    heats = []
    heat_num = 1
    idx = 0

    while idx < len(swimmers):
        chunk = swimmers[idx:idx + lanes]

        heat = {
            "heat_number": heat_num,
            "lanes": {
                str(i + 1): s for i, s in enumerate(chunk)
            }
        }

        heats.append(heat)

        heat_num += 1
        idx += lanes

    return heats


def build_heat_sheet(events, lanes, order, is_long_event):
    heat_sheet = []

    for e in events:

        # long distance override hook (future expansion)
        if is_long_event(e["name"]):
            pass

        heat_sheet.append({
            "number": e["number"],
            "name": e["name"],
            "heats": seed_event(e, lanes, order)
        })

    return heat_sheet
