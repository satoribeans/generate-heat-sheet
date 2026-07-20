from models import Heat, Lane, Meet, Event, Entry
from utils import is_long_event, is_400_free_event, is_400_im_event, get_age_group
from collections import defaultdict

# --------------------------------------
# Heat assignment (circle seeding style)
# --------------------------------------
def _is_prelim_event(event_name: str) -> bool:
    name = event_name.lower()
    return "prelim" in name or "preliminary" in name

# ----------------------------------------------
# Generate heat sheet for each individual event
# ----------------------------------------------
def seed_event(
    entries,
    lane_count=8,
    reverse_heats=True,
    prelim_circle_top_n_heats=1,
):
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

    # If the slowest heat has 1 swimmer, move last 2 swimmers from the previous heat over
    if len(heats_entries) >= 2 and len(heats_entries[-1]) == 1:
        heats_entries[-1] = heats_entries[-2][-2:] + heats_entries[-1]
        heats_entries[-2] = heats_entries[-2][:-2]

    # Heat 1 = slowest heat
    # Last heat = fastest heat
    if reverse_heats:
        heats_entries.reverse()

    final_heats = []

    # USA swimming age group circle seeding rules for prelims:
    # default n=3
    # lane 4  5  3   6  2  7  1  8
    #------------------------------
    # seed 1  4  7  10 13 16 19 22
    # seed 2  5  8  11 14 17 20 23
    # seed 3  6  9  12 15 18 21 24
    #
    if prelim_circle_top_n_heats > 1:
        num_circle_heats = min(prelim_circle_top_n_heats, len(heats_entries))
        # Heat 1 is slowest and last heat is fastest when reverse_heats=True.
        # Circle-seed the fastest N heats as requested.
        top_heat_start = len(heats_entries) - num_circle_heats
        top_heat_indices = list(range(top_heat_start, len(heats_entries)))

        heat_lane_map = defaultdict(list)

        # Keep standard per-heat seeding for all non-circle-seeded heats.
        for heat_idx in range(top_heat_start):
            heat_num = heat_idx + 1
            heat_entries = heats_entries[heat_idx]

            for idx, entry in enumerate(heat_entries):
                lane_num = lane_order[idx]
                entry.heat_number = heat_num
                entry.lane_number = lane_num
                heat_lane_map[heat_idx].append(
                    Lane(lane_number=lane_num, entry=entry)
                )

        # Collect top-heat entries from fastest heat -> slower heat.
        circle_entries = []
        for heat_idx in reversed(top_heat_indices):
            circle_entries.extend(heats_entries[heat_idx])

        circle_ptr = 0
        # True cross-heat circle seeding across the top heats.
        # Seeds 1..N go to lane 4 (or lane 5 for 10-lane) across fastest->slower top heats,
        # then continue outward by lane order.
        for lane_idx, lane_num in enumerate(lane_order):
            for heat_idx in reversed(top_heat_indices):
                # This heat has no swimmer for this lane position.
                if lane_idx >= len(heats_entries[heat_idx]):
                    continue
                if circle_ptr >= len(circle_entries):
                    break

                entry = circle_entries[circle_ptr]
                circle_ptr += 1

                entry.heat_number = heat_idx + 1
                entry.lane_number = lane_num
                heat_lane_map[heat_idx].append(
                    Lane(lane_number=lane_num, entry=entry)
                )

        for heat_idx in range(len(heats_entries)):
            final_heats.append(
                Heat(
                    heat_number=heat_idx + 1,
                    lanes=sorted(
                        heat_lane_map[heat_idx],
                        key=lambda lane: lane.lane_number,
                    ),
                )
            )

        return final_heats

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
                heat_number=heat_num,
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
        reverse_heats = True
        entries = event.entries
        # default to 1 to disable circle seeding
        prelim_circle_top_n_heats = 1

        if _is_prelim_event(event.name) and meet.settings.enable_prelim_circle_seeding:
            prelim_circle_top_n_heats = meet.settings.circle_seed_top_n_heats

        if is_long_event(event.name.lower()) and order == "fast_to_slow":
            reverse_heats = False
        elif is_400_free_event(event.name.lower()) and meet.settings.four_free_event_order == "fast_to_slow":
            reverse_heats = False
        elif is_400_im_event(event.name.lower()) and meet.settings.four_im_additional_event_order == "fast_to_slow":
            reverse_heats = False

        # generate heats, return list[Heat]
        heats = seed_event(
            entries,
            lanes,
            reverse_heats,
            prelim_circle_top_n_heats,
        )

        if is_400_im_event(event.name.lower()):
            if get_age_group(event.name) == "11-12" and meet.settings.four_im_top_n_heats_11_12 > 1:
                if meet.settings.four_im_additional_event_order == "fast_to_slow" and meet.settings.four_im_top_n_event_order_11_12 == "slow_to_fast":
                    n = meet.settings.four_im_top_n_heats_11_12
                    heats = heats[:n][::-1]+heats[n:]
                    for i, h in enumerate(heats, start=1):
                        h.heat_number = i
                        for l in h.lanes:
                            if l.entry:
                                l.entry.heat_number = i
            elif get_age_group(event.name) == "13-14" and meet.settings.four_im_top_n_heats_13_14 > 1:
                if meet.settings.four_im_additional_event_order == "fast_to_slow" and meet.settings.four_im_top_n_event_order_13_14 == "slow_to_fast":
                    n = meet.settings.four_im_top_n_heats_13_14
                    heats = heats[:n][::-1]+heats[n:]
                    for i, h in enumerate(heats, start=1):
                        h.heat_number = i
                        for l in h.lanes:
                            if l.entry:
                                l.entry.heat_number = i

        # attach heats to the event model
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

#=============================================
# Future work - alternative seeding methods 1
#=============================================
def seed_event_fastest_in_center(entries, lane_count=8, reverse_heats=True):
    if not entries:
        return []

    # Center-out lane order (fastest gets center lane)
    lane_order = (
        [4, 5, 3, 6, 2, 7, 1, 8]        # 8-lane pool
        if lane_count == 8
        else [5, 6, 4, 7, 3, 8, 2, 9, 1, 10]  # 10-lane pool
    )

    num_heats = (len(entries) + lane_count - 1) // lane_count

    heats_entries = []
    remaining = list(entries)  # already sorted fastest → slowest

    # ── Step 1: Split entries into heats ──────────────────────
    # Build from fastest heat down to slowest.
    # Avoid leaving a heat-1 with 0 swimmers.
    for h in range(num_heats, 0, -1):
        count = min(lane_count, len(remaining))

        # If taking `count` would leave heat #1 empty, hold one back
        if h > 1 and len(remaining) - count < 1 and len(remaining) > 1:
            count = len(remaining) - 1

        heats_entries.append(remaining[:count])
        remaining = remaining[count:]

    # heats_entries[0] = fastest heat, [-1] = slowest heat
    if reverse_heats:
        heats_entries.reverse()
    # Now heats_entries[0] = slowest (Heat 1), [-1] = fastest (last heat)

    # ── Step 2: Assign lanes using circle seeding ─────────────
    #
    # Circle seeding rule:
    #   Within each heat, fastest swimmer gets center lane (lane_order[0]),
    #   next fastest gets lane_order[1], and so on outward.
    #
    # Cross-heat circle seeding (USA Swimming standard):
    #   The single fastest swimmer in the meet goes in center lane
    #   of the LAST heat. The 2nd fastest goes in center lane of
    #   the 2nd-to-last heat. Then we fill remaining lanes outward
    #   alternating across heats.
    #
    #   Seeding order across heats (for an 8-lane, 3-heat example):
    #     Seed 1  → Heat 3, Lane 4  (center, fastest heat)
    #     Seed 2  → Heat 2, Lane 4  (center, 2nd heat)
    #     Seed 3  → Heat 1, Lane 4  (center, slowest heat)
    #     Seed 4  → Heat 3, Lane 5  (1 right of center, fastest heat)
    #     Seed 5  → Heat 2, Lane 5
    #     Seed 6  → Heat 1, Lane 5
    #     Seed 7  → Heat 3, Lane 3  (1 left of center)
    #     ... and so on

    final_heats = []
    for heat_idx, heat_entries in enumerate(heats_entries):
        # Sort this heat's entries fastest first for lane assignment
        # (entries are already sorted but just to be explicit)
        sorted_entries = sorted(heat_entries, key=lambda e: e.seed_num)

        lanes = {}
        for rank, entry in enumerate(sorted_entries):
            if rank < len(lane_order):
                lane_num = lane_order[rank]
                lanes[lane_num] = entry

        final_heats.append({
            "heat_number": heat_idx + 1,
            "lanes": lanes,
        })

    return final_heats

#=============================================
# Future work - alternative seeding methods 2
#=============================================
def seed_event_cross_heat(entries, lane_count=8, reverse_heats=True):
    if not entries:
        return []

    lane_order = (
        [4, 5, 3, 6, 2, 7, 1, 8]
        if lane_count == 8
        else [5, 6, 4, 7, 3, 8, 2, 9, 1, 10]
    )

    num_heats = (len(entries) + lane_count - 1) // lane_count

    # ── Step 1: Split into heats (fastest first) ──────────────
    remaining = list(entries)
    heats_entries = []

    for h in range(num_heats, 0, -1):
        count = min(lane_count, len(remaining))
        if h > 1 and len(remaining) - count < 1 and len(remaining) > 1:
            count = len(remaining) - 1
        heats_entries.append(remaining[:count])
        remaining = remaining[count:]

    if reverse_heats:
        heats_entries.reverse()
    # heats_entries[0]=Heat1(slowest) ... [-1]=last heat(fastest)

    # ── Step 2: True circle seeding across heats ──────────────
    #
    # Build a seeding grid: for each lane position (center outward),
    # assign entries top-down through heats from fastest to slowest.
    #
    # Example — 3 heats, 8 lanes, 20 swimmers:
    #
    #   Lane pos:  [4]  [5]  [3]  [6]  [2]  [7]  [1]  [8]
    #   Heat 3:     1    4    7   10   13   16   19    -
    #   Heat 2:     2    5    8   11   14   17   20    -
    #   Heat 1:     3    6    9   12   15   18    -    -
    #
    # Seed numbers fill down each column before moving to next lane.

    # Initialize empty lane assignments for each heat
    heat_lanes = [{} for _ in range(num_heats)]

    # Flatten entries in seeding order:
    # fastest heat first within each lane position
    seed_idx = 0
    all_entries = list(entries)  # fastest → slowest (seed 1 first)

    for lane_pos in lane_order:
        # Fill this lane top-down: fastest heat → slowest heat
        for heat_idx in range(num_heats - 1, -1, -1):
            if seed_idx >= len(all_entries):
                break
            # Only assign if this heat has a swimmer at this position
            if seed_idx < len(heats_entries[heat_idx]) + sum(
                len(heats_entries[i]) for i in range(heat_idx)
            ):
                heat_lanes[heat_idx][lane_pos] = all_entries[seed_idx]
                seed_idx += 1

    # ── Step 3: Build final heat objects ──────────────────────
    final_heats = []
    for heat_idx, lanes in enumerate(heat_lanes):
        final_heats.append({
            "heat_number": heat_idx + 1,
            "lanes": lanes,
        })

    return final_heats
