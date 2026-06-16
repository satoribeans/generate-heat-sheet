import re
from utils import clean_line

def parse_psych_sheet(text):
    events = []
    current_event = None

    event_re = re.compile(r'(?:Event\s+|#)(\d+)\s+(.*)')
    seed_time_pattern = r'(NT|\d+:?\d*\.\d+)'

    gender_header_re = re.compile(r'^(W\d+|M\d+)\s*&?\s*Under', re.IGNORECASE)

    swimmer_re_A = re.compile(r'^(\S+)\s+' + seed_time_pattern + r'\s+(\d+)\s+(.*?)\s+(\d+)$')
    swimmer_re_B = re.compile(r'^(\S+)\s+' + seed_time_pattern + r'\s*([MW]?\d+|Boys|Girls|W\d+|M\d+)\s*(.*?)\s+(\d+)$')
    swimmer_re_C = re.compile(r'^(\d+)\s+(.*?)\s+([MW]?\d+|Boys|Girls|W\d+|M\d+)\s+(\S+)\s+' + seed_time_pattern + r'$')

    current_gender = None

    for line in text.splitlines():
        line = clean_line(line)
        if not line:
            continue

        m = event_re.search(line)
        if m:
            current_event = {
                "number": m.group(1),
                "name": m.group(2).replace("...", "").strip(),
                "swimmers": []
            }
            events.append(current_event)
            current_gender = None
            continue

        gm = gender_header_re.match(line)
        if gm:
            current_gender = gm.group(1)[0].upper()
            continue

        if not current_event:
            continue

        swimmer = None
        for regex in (swimmer_re_B, swimmer_re_C, swimmer_re_A):
            match = regex.match(line)
            if match:
                if regex == swimmer_re_B:
                    swimmer = {
                        "team": match.group(1),
                        "seed_time": match.group(2),
                        "age": match.group(3),
                        "name": match.group(4).strip(),
                        "rank": int(match.group(5))
                    }
                elif regex == swimmer_re_C:
                    swimmer = {
                        "rank": int(match.group(1)),
                        "name": match.group(2).strip(),
                        "age": match.group(3),
                        "team": match.group(4),
                        "seed_time": match.group(5)
                    }
                else:
                    swimmer = {
                        "team": match.group(1),
                        "seed_time": match.group(2),
                        "age": match.group(3),
                        "name": match.group(4).strip(),
                        "rank": int(match.group(5))
                    }
                break

        if swimmer:
            swimmer["gender"] = current_gender
            current_event["swimmers"].append(swimmer)

    return events
