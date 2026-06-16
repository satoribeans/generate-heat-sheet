import re
from utils import clean_line
from models import Event, Heat, Swimmer

event_re = re.compile(r'(?:Event\s+|#)(\d+)\s+(.*)')
gender_header_re = re.compile(r'^(W\d+|M\d+)\s*&?\s*Under', re.IGNORECASE)

seed_time_pattern = r'(NT|\d+:?\d*\.\d+)'

swimmer_re_A = re.compile(r'^(\S+)\s+' + seed_time_pattern + r'\s+(\d+)\s+(.*?)\s+(\d+)$')
swimmer_re_B = re.compile(r'^(\S+)\s+' + seed_time_pattern + r'\s*([MW]?\d+|Boys|Girls|W\d+|M\d+)\s*(.*?)\s*(\d+)$')
swimmer_re_C = re.compile(r'^(\d+)\s+(.*?)\s+([MW]?\d+|Boys|Girls|W\d+|M\d+)\s+(\S+)\s+' + seed_time_pattern + r'$')


def parse_psych_sheet(text):
    events = []
    current_event = None
    current_gender = None

    for line in text.splitlines():
        line = clean_line(line)
        if not line:
            continue

        m = event_re.search(line)
        if m:
            num, name = m.group(1), m.group(2).replace("...", "").strip()

            if current_event and current_event["number"] == num:
                continue

            current_gender = None

            current_event = {
                "number": num,
                "name": name,
                "swimmers": []
            }

            events.append(current_event)
            continue

        gm = gender_header_re.match(line)
        if gm:
            current_gender = gm.group(1)[0].upper()
            continue

        if not current_event:
            continue

        swimmer = None

        for r in (swimmer_re_B, swimmer_re_C, swimmer_re_A):
            m = r.match(line)
            if m:
                if r == swimmer_re_B:
                    swimmer = {
                        "team": m.group(1),
                        "seed_time": m.group(2),
                        "age": m.group(3),
                        "name": m.group(4),
                        "rank": int(m.group(5))
                    }
                elif r == swimmer_re_C:
                    swimmer = {
                        "rank": int(m.group(1)),
                        "name": m.group(2),
                        "age": m.group(3),
                        "team": m.group(4),
                        "seed_time": m.group(5)
                    }
                else:
                    swimmer = {
                        "team": m.group(1),
                        "seed_time": m.group(2),
                        "age": m.group(3),
                        "name": m.group(4),
                        "rank": int(m.group(5))
                    }
                break

        if swimmer:
            swimmer["gender"] = current_gender
            current_event["swimmers"].append(swimmer)

    return events
