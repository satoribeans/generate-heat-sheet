import re
from utils import clean_line

def parse_psych_sheet(text):
    events = []
    current_event = None

    event_re = re.compile(r'(?:Event\s+|#)(\d+)\s+(.*)')
    seed_time_pattern = r'(NT|\d+:?\d*\.\d+)'

    swimmer_re = re.compile(
        r'^(\S+)\s+' + seed_time_pattern + r'\s+(\d+)\s+(.*?)\s+(\d+)$'
    )

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
            continue

        if not current_event:
            continue

        s = swimmer_re.match(line)
        if s:
            current_event["swimmers"].append({
                "team": s.group(1),
                "seed_time": s.group(2),
                "age": s.group(3),
                "name": s.group(4).strip(),
                "rank": int(s.group(5)),
                "gender": None
            })

    return events
