from utils import time_to_seconds
from models import Event, Heat, Swimmer

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

def seed_event(event, lanes=8):
    swimmers = sorted(
        event["swimmers"],
        key=lambda x: x["rank"]
    )

    if not swimmers:
        return []

    num_swimmers = len(swimmers)
    num_heats = (num_swimmers + lanes - 1) // lanes

    heats_swimmers = []
    remaining = swimmers[:]

    for h in range(num_heats, 0, -1):
        count = lanes if h > 1 else len(remaining)

        if h > 1 and len(remaining) - count < 1 and len(remaining) > 1:
            count = len(remaining) - 1

        heats_swimmers.append(remaining[:count])
        remaining = remaining[count:]

    heats_swimmers.reverse()

    if lanes == 8:
        lane_order = [4, 5, 3, 6, 2, 7, 1, 8]
    elif lanes == 6:
        lane_order = [3, 4, 2, 5, 1, 6]
    else:
        lane_order = list(range(1, lanes + 1))

    final_heats = []

    for i, heat in enumerate(heats_swimmers):

        heat.sort(key=lambda x: x["rank"])

        assigned = {
            str(lane_order[j]): swimmer
            for j, swimmer in enumerate(heat)
            if j < len(lane_order)
        }

        final_heats.append({
            "heat_number": i + 1,
            "lanes": assigned
        })

    return final_heats

def build_heat_sheet(events, heat_size, order, is_long_event):
    heat_sheet = []

    for e in events:
        heat_sheet.append({
            "number": e["number"],
            "name": e["name"],
            "heats": seed_event(e, lanes=heat_size)
        })

    return heat_sheet
