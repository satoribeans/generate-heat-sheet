from utils import time_to_seconds, is_long_event


def seed_event(event, lanes=8):
    swimmers = sorted(event["swimmers"], key=lambda x: x.get("rank", 0))
    if not swimmers:
        return []

    num_heats = (len(swimmers) + lanes - 1) // lanes
    heats_swimmers = []
    remaining = swimmers[:]

    for h in range(num_heats, 0, -1):
        count = lanes if h > 1 else len(remaining)
        heats_swimmers.append(remaining[:count])
        remaining = remaining[count:]

    heats_swimmers.reverse()

    lane_order = [4, 5, 3, 6, 2, 7, 1, 8] if lanes == 8 else [3, 4, 2, 5, 1, 6]

    final_heats = []
    for i, h_list in enumerate(heats_swimmers):
        h_list.sort(key=lambda x: x.get("rank", 0))
        assigned = {
            str(lane_order[j]): s
            for j, s in enumerate(h_list)
            if j < len(lane_order)
        }
        final_heats.append({
            "heat_number": i + 1,
            "lanes": assigned
        })

    return final_heats


def seed_swimmers_by_time(swimmers, heat_size, order):
    swimmers_sorted = sorted(swimmers, key=lambda x: time_to_seconds(x.get("seed_time")))

    if order == "slow_to_fast":
        swimmers_sorted.reverse()

    # We update the rank based on the sorted order to use seed_event's logic
    for i, s in enumerate(swimmers_sorted):
        s["rank"] = i + 1

    return swimmers_sorted


def build_heat_sheet(events, lanes, order, is_long_event_func):
    heat_sheet = []

    for e in events:
        swimmers = e["swimmers"]

        # apply custom seeding only for long/mixed events
        if "mixed" in e["name"].lower() or is_long_event_func(e["name"]):
            swimmers = seed_swimmers_by_time(swimmers, lanes, order)

        heat_sheet.append({
            "number": e["number"],
            "name": e["name"],
            "heats": seed_event({"swimmers": swimmers}, lanes)
        })

    return heat_sheet
