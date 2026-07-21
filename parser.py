import re

from models import Entry, Swimmer, Event
from utils import clean_line, get_team_code

event_re = re.compile(r'(?:Event\s+|#)(\d+)\s+(.*)')
gender_header_re = re.compile(r'^(W\d+|M\d+)\s*&?\s*Under', re.IGNORECASE)
metadata_re = re.compile(
    r'^(Meet\s+Qualifying|Meet\s+Record|Pool\s+Record)\s*:',
    re.IGNORECASE,
)
column_header_re = re.compile(r'^(Age\s+TeamName|RelayTeam)\b', re.IGNORECASE)

# NCS / Meet Manager 8.0 layout: TEAM SEED_TIME AGENAME RANK
# Example: Old North State 9:29.92 14Teague, Rowan1
ncs_seed_time_pattern = r'(NT|\d+(?::\d+)?\.\d+[YL]?)'
swimmer_re_ncs = re.compile(
    r'^(.*?)\s+'
    + ncs_seed_time_pattern +
    r'\s+'
    r'(\d{1,2})'
    r'(.+?)'
    r'(\d+)\s*(?:B)?$'
)

relay_re = re.compile(
    r'^([A-Z])\s+'
    + ncs_seed_time_pattern +
    r'(.+?)'
    r'(\d+)\s*(?:B)?$'
)


def gender_from_event_name(event_name: str) -> str:
    name = event_name.lower()
    if name.startswith(("women", "girls")):
        return "F"
    if name.startswith(("men", "boys")):
        return "M"
    return ""


def parse_psych_sheet(text):
    events: dict[int, Event] = {}

    current_event = None
    current_gender = None

    for line in text.splitlines():
        line = clean_line(line)
        if not line:
            continue

        m = event_re.match(line)
        if m:
            event_number = int(m.group(1))
            event_name = re.sub(r"\.{3,}", "", m.group(2)).strip()

            if event_number not in events:
                events[event_number] = Event(
                    event_number=event_number,
                    name=event_name,
                    entries=[],
                )

            current_event = events[event_number]
            current_gender = gender_from_event_name(event_name)
            continue

        gm = gender_header_re.match(line)
        if gm:
            current_gender = gm.group(1)[0].upper()
            continue

        if not current_event:
            continue

        if metadata_re.match(line) or column_header_re.match(line):
            continue

        #### debug only ####
        # print(f"Parsing line: {line!r}")

        entry = parse_swimmer_line(line, current_event, current_gender)
        if entry:
            current_event.entries.append(entry)

    return list(events.values())


def parse_swimmer_line(line, current_event, current_gender):
    if "relay" in current_event.name.lower():
        relay_match = relay_re.match(line)
        if relay_match:
            letter, seed_time, team, rank = relay_match.groups()
            swimmer = Swimmer(
                name=f"{team.strip()} {letter}",
                gender=current_gender or "",
                age="",
                team=team.strip(),
                team_code=get_team_code(team.strip()),
            )
            return Entry(
                swimmer=swimmer,
                event=current_event,
                seed_num=int(rank),
                entry_time=seed_time,
                heat_number=None,
                lane_number=None,
            )

    # Seed time pattern: "NT" or "M:S.CC" or "S.CC"
    seed_time_pattern = r'(NT|\d+:?\d*\.\d+)'

    # Pattern A (Original): TEAM SEED_TIME AGE NAME RANK
    swimmer_re_A = re.compile(
        r'^(\S+)\s+' + seed_time_pattern + r'\s+(\d+)\s+(.*?)\s+(\d+)$'
    )

    # Pattern B (MOTH & NCSA): TEAM SEED_TIME AGE_GENDER NAME RANK
    # Example: NCAC-NC 2:03.56M21Whelehan, Colin H1 or NCAC-NC 3:56.29 18Huggins, Sam L1
    # Note: Sometimes gender prefix is missing and there might be no space after age
    # swimmer_re_B = re.compile(
    #     r'^(\S+)\s+' + seed_time_pattern + r'\s*([MW]?\d+|Boys|Girls)\s*(.*?)\s*(\d+)$'
    # )
    swimmer_re_B = re.compile(
        r'^(\S+)\s+'  # team
        + seed_time_pattern +  # time
        r'([YL])?' +  # optional course: Y/L
        r'\s*'
        r'([MW]?\d+|Boys|Girls)\s*'  # age
        r'(.*?)\s*'  # swimmer name
        r'([A-Z]{1,5})?'  # optional standard: QT/J/O/TYR
        r'(\d+)$'  # rank
    )


    # Pattern C (Alternative MOTH): RANK NAME AGE_GENDER TEAM SEED_TIME
    swimmer_re_C = re.compile(
        r'^(\d+)\s+(.*?)\s+([MW]?\d+|Boys|Girls)\s+(\S+)\s+' + seed_time_pattern + r'$'
    )

    # Pattern D (LC AG Champs, NCSA) - National Club Swimming Association
    # Examples:
    # NTA-IL 23.91 14Liu-Tchorbadjiyski, Lubo J12
    # TG-SC 24.14 16Bridges, Will QT20
    # NCAP-PV 24.18 15Hanson, Gabe QT21
    # swimmer_re_D = re.compile(
    #     r'^(\S+)\s+'  # team
    #     + seed_time_pattern +
    #     r'\s*([MW]?\d+|Boys|Girls)\s*'  # age
    #     r'(.*?)\s*'  # swimmer name
    #     r'(?:[A-Z]+)?'  # optional qualifier (J, QT, Q, etc.)
    #     r'(\d+)$'  # rank
    # )

    for pattern in (swimmer_re_B, swimmer_re_C, swimmer_re_A):
        m = pattern.match(line)
        if not m:
            continue

        # print(f"following pattern: {pattern.pattern}")

        # -------------------------
        # Pattern B (most common in meet manager exports)
        # NCAC 2:03.56M21Whelehan, Colin H1
        # -------------------------
        if pattern == swimmer_re_B:
            rank = int(m.group(7))

            seed_time = m.group(2)

            if m.group(3):
                seed_time += m.group(3)

            if m.group(6):
                seed_time += " " + m.group(6)

            age = m.group(4)
            name = m.group(5).strip()
            team = m.group(1)

        # -------------------------
        # Pattern C (rank-first layouts)
        # -------------------------
        elif pattern == swimmer_re_C:
            rank = int(m.group(1))
            name = m.group(2).strip()
            age = m.group(3)
            team = m.group(4)
            seed_time = m.group(5)


        # -------------------------
        # Pattern A (compact layouts)
        # -------------------------
        else:
            rank = int(m.group(5))
            seed_time = m.group(2)
            age = m.group(3)
            name = m.group(4).strip()
            team = m.group(1)


        swimmer = Swimmer(
            name=name,
            gender=current_gender or "",
            age=str(age).lstrip("WM"),
            team= team if 'team' in locals() else "",
            team_code=get_team_code(team),
        )

        return Entry(
            swimmer=swimmer,
            event=current_event,
            seed_num=rank,
            entry_time=seed_time,
            heat_number=None,
            lane_number=None,
        )

    ncs_match = swimmer_re_ncs.match(line)
    if ncs_match:
        team, seed_time, age, name, rank = ncs_match.groups()
        swimmer = Swimmer(
            name=name.strip(),
            gender=current_gender or "",
            age=age,
            team=team.strip(),
            team_code=get_team_code(team.strip()),
        )
        return Entry(
            swimmer=swimmer,
            event=current_event,
            seed_num=int(rank),
            entry_time=seed_time,
            heat_number=None,
            lane_number=None,
        )

    return None
