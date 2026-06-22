from models import Heat, Lane, Meet
from utils import time_to_seconds, is_long_event
from collections import defaultdict



# -----------------------------
# Convert Entry objects → sortable list
# -----------------------------
def sort_entries(entries, order):
    if order == "fast_to_slow":
        return sorted(
            entries,
            key=lambda e: time_to_seconds(e.entry_time)
        )

    return sorted(
        entries,
        key=lambda e: time_to_seconds(e.entry_time),
        reverse=True
    )

# -----------------------------
# Heat assignment (circle seeding style)
# -----------------------------
def seed_event(entries, lane_count=8):
    if not entries:
        return []

    # entries should already be sorted:
    #   normal events -> by seed_num
    #   distance events -> by entry_time according to settings
    lane_order = (
        [4, 5, 3, 6, 2, 7, 1, 8]
        if lane_count == 8
        else [5, 6, 4, 7, 3, 8, 2, 9, 1, 10]
    )
    num_heats = (len(entries) + lane_count - 1) // lane_count

    heats_entries = []
    remaining = list(entries)

    # Build heats from fastest to slowest
    for h in range(num_heats, 0, -1):

        # count = lane_count if h > 1 else len(remaining)
        count = min(lane_count, len(remaining))

        # avoid empty heat #1
        if h > 1 and len(remaining) - count < 1 and len(remaining) > 1:
            count = len(remaining) - 1

        heats_entries.append(remaining[:count])
        remaining = remaining[count:]

    # Heat 1 = slowest heat
    # Last heat = fastest heat
    heats_entries.reverse()

    final_heats = []

    for heat_num, heat_entries in enumerate(
        heats_entries,
        start=1
    ):
        heat_lanes = []

        for idx, entry in enumerate(heat_entries):
            lane_num = lane_order[idx]

            entry.heat_number = heat_num
            entry.lane_number = lane_num

            heat_lanes.append(
                Lane(
                    lane_number=lane_num,
                    entry=entry,
                )
            )

        final_heats.append(
            Heat(
                heat_number= entry.heat_number,
                lanes = heat_lanes
            )
        )

    return final_heats


# -----------------------------
# Main entry point
# -----------------------------
def build_heat_sheet(meet) -> Meet:
    lanes = meet.settings.lanes
    order = meet.settings.distance_event_order

    for event in meet.events:

        entries = event.entries

        # long/mixed event logic
        # if "mixed" in event.name.lower():
        if is_long_event(event.name.lower()):
            entries = sort_entries(entries, order)

        # generate heats, return list[Heat]
        heats = seed_event(entries, lanes)
        # attach to event model
        event.heats = heats

    return meet


def get_favorite_swimmers(
    meet: Meet,
    favorites: set[str]
):

    result = defaultdict(list)

    for entry in meet.all_entries():

        if entry.swimmer.name not in favorites:
            continue

        result[entry.swimmer.name].append({
            "event_number": entry.event.event_number,
            "event_name": entry.event.name,
            "heat": entry.heat_number,
            "lane": entry.lane_number,
            "entry": entry,
        })

    for swims in result.values():
        swims.sort(key=lambda x: x["event_number"])

    return dict(result)
