import re
import streamlit as st
from venv import logger

from models import Entry, Swimmer, Event
from utils import clean_line

def parse_psych_sheet(text):
    events: dict[int, Event] = {}

    event_re = re.compile(r'(?:Event\s+|#)(\d+)\s+(.*)')
    gender_header_re = re.compile(r'^(W\d+|M\d+)\s*&?\s*Under', re.IGNORECASE)
    # metadata_re = re.compile(r'^[A-Za-z][A-Za-z /()-]*:\s*')
    metadata_re = re.compile(r'^[A-Za-z][^:]{0,80}:')

    current_event = None
    current_gender = None

    for line in text.splitlines():
        line = clean_line(line)
        print(repr(line))
        if not line:
            continue

        # -------------------------
        # Event header (dedupe key fix)
        # -------------------------
        # m = event_re.search(line)
        m = event_re.match(line)
        if m:
            event_number = int(m.group(1))
            event_name = re.sub(r"\.{3,}", "", m.group(2)).strip()

            if event_number not in events:
                events[event_number] = Event(
                    event_number = event_number,
                    name = event_name,
                    entries = []
                )

            current_event = events[event_number]
            current_gender = None
            continue

        # --------------------------------
        # Gender header (optional context)
        # --------------------------------
        gm = gender_header_re.match(line)
        if gm:
            current_gender = gm.group(1)[0].upper()
            continue

        if not current_event:
            continue

        # Skip metadata lines such as:
        #   Meet qualifying: 23.50
        #   Meet record: 55.12
        #   Pool record: 54.87
        if metadata_re.match(line):
            continue

        # -------------------------
        # Swimmer row
        # -------------------------
        if current_event:
            entry = parse_swimmer_line(line, current_event, current_gender)

            if entry:
                current_event.entries.append(entry)

    return list(events.values())

def parse_swimmer_line(line, current_event, current_gender):

    # swimmer_re_B = re.compile(r'^(\S+)\s+' + seed_time_pattern + r'\s*([MW]?\d+|Boys|Girls|W\d+|M\d+)\s*(.*?)\s+(\d+)$')
    # swimmer_re_C = re.compile(r'^(\d+)\s+(.*?)\s+([MW]?\d+|Boys|Girls|W\d+|M\d+)\s+(\S+)\s+' + seed_time_pattern + r'$')

    # Seed time pattern: "NT" or "M:S.CC" or "S.CC"
    seed_time_pattern = r'(NT|\d+:?\d*\.\d+)'

    # Pattern A (Original): TEAM SEED_TIME AGE NAME RANK
    swimmer_re_A = re.compile(r'^(\S+)\s+' + seed_time_pattern + r'\s+(\d+)\s+(.*?)\s+(\d+)$')

    # Pattern B (MOTH): TEAM SEED_TIME AGE_GENDER NAME RANK
    # Example: NCAC-NC 2:03.56M21Whelehan, Colin H1 or NCAC-NC 3:56.29 18Huggins, Sam L1
    # Note: Sometimes gender prefix is missing and there might be no space after age
    swimmer_re_B = re.compile(r'^(\S+)\s+' + seed_time_pattern + r'\s*([MW]?\d+|Boys|Girls)\s*(.*?)\s*(\d+)$')

    # Pattern C (Alternative MOTH): RANK NAME AGE_GENDER TEAM SEED_TIME
    swimmer_re_C = re.compile(r'^(\d+)\s+(.*?)\s+([MW]?\d+|Boys|Girls)\s+(\S+)\s+' + seed_time_pattern + r'$')


    for pattern in (swimmer_re_B, swimmer_re_C, swimmer_re_A):
        m = pattern.match(line)
        if not m:
            continue

        # -------------------------
        # Pattern B (most common in meet manager exports)
        # NCAC 2:03.56M21Whelehan, Colin H1
        # -------------------------
        if pattern == swimmer_re_B:
            rank = int(m.group(5))
            seed_time = m.group(2)
            age = m.group(3)
            name = m.group(4).strip()
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
            team=team if 'team' in locals() else ""
        )

        entry = Entry(
            swimmer=swimmer,
            event=current_event,
            seed_num=rank,
            entry_time=seed_time,
            heat_number=None,
            lane_number=None
        )

        return entry

    return None
