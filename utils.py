import re
from datetime import datetime


def safe_text(text):
    if not text:
        return ""

    replacements = {
        "★": "*",
        "–": "-",
        "—": "-",
        "'": "'",
        """: '"',
        """: '"'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)

    return text.encode("latin-1", "ignore").decode("latin-1")


def time_to_seconds(time_str):
    if time_str == "NT":
        return float("inf")

    if ":" in time_str:
        minutes, seconds = time_str.split(":")
        return int(minutes) * 60 + float(seconds)

    return float(time_str)


def clean_line(line):
    return (
        line.replace("Butter7ly", "Butterfly")
            .replace("Butterﬂy", "Butterfly")
            .replace("Butterϐly", "Butterfly")
            .replace("CrutchEield", "Crutchfield")
            .replace("Crutchﬁeld", "Crutchfield")
            .replace("-NC", "")
            # .replace("New Wave Swim Te", "WAVE")
            # .replace("SwimMAC Carolina", "MAC")
            # .replace("North Carolina A", "NCAC")
            # .replace("Tac Titans", "TAC")
            .strip()
    )

def is_long_event(name):
    name = name.lower()

    # Exclude relay events
    if "relay" in name:
        return False

    return any(x in name for x in ["500", "800", "1000", "1500", "1650"])

def is_400_free_event(name):
    name = name.lower()

    # Exclude relay events
    if "relay" in name:
        return False

    # return "400" in name and "free" in name
    return bool(re.search(r'\b400\b.*\bfree(style)?\b', name, re.IGNORECASE))

def is_400_im_event(name):

    # Exclude relay events
    if "relay" in name.lower():
        return False

    return bool(
        re.search(
            r'\b400\b.*\b(im|individual\s+medley)\b',
            name,
            re.IGNORECASE
        )
    )

def is_relay_event(name):
    return "relay" in name.lower()
# -----------------------------------------
# get_age_group("Women 11-12 400 IM")
# # '11-12'
#
# get_age_group("Girls 10&Under 50 Free")
# # '10&Under'
#
# get_age_group("Boys 13-14 200 Fly")
# # '13-14'
#
# get_age_group("Men Open 1500 Free")
# # 'Open'
# -----------------------------------------
def get_age_group(name):
    m = re.search(r'\b(\d{1,2}\s*-\s*\d{1,2}|\d{1,2}\s*&\s*Under|Open)\b',
                  name, re.IGNORECASE)
    return m.group(1) if m else None

def get_gender(name):
    m = re.search(r'\b(women|woman|girls?|men|man|boys?)\b', name, re.IGNORECASE)
    if not m:
        return None

    word = m.group(1).lower()
    if word.startswith(("w", "g")):
        return "Girls"
    return "Boys"

# ==========================================================
# TITLE EXTRACTION
# ==========================================================
def extract_meet_title(text):
    lines = text.splitlines()
    title_lines = []
    meet_year = None  # we will extract from date range

    for line in lines[:30]:
        line = line.strip()

        # Normalize psych sheet text
        line = re.sub(r"\bpsych\s+sheet\b", "", line, flags=re.IGNORECASE)
        line = re.sub(r"\bpsyc\s+sheet\b", "", line, flags=re.IGNORECASE)

        if not line:
            continue

        # Extract year from date range (once found)
        if meet_year is None:
            date_match = re.search(
                r'(\d{1,2})/\d{1,2}/(\d{4})\s+to\s+\d{1,2}/\d{1,2}/\d{4}',
                line
            )
            if date_match:
                meet_year = date_match.group(2)

        # Stop at event section
        if re.search(r'(?:Event\s+|#)\d+', line):
            break

        # Skip page markers
        if "PAGE" in line.upper():
            continue

        title_lines.append(line)

    if not title_lines:
        return "Swim Meet Heat Sheet"

    # Build title
    title = " - ".join(title_lines[:3])
    # remove date range from the title
    title = re.sub(
        r'\s*-\s*\d{1,2}/\d{1,2}/\d{4}\s+to\s+\d{1,2}/\d{1,2}/\d{4}',
        '',
        title
    )
    # remove sanction number
    title = re.sub(r'\s*-\s*Sanction\s*#\s*:\s*[^-]+', '', title, flags=re.IGNORECASE)

    # Prepend year if we found one
    if meet_year and not title.startswith(meet_year):
        title = f"{meet_year} {title}"

    return title
    # return " - ".join(title_lines[:3]) if title_lines else "Swim Meet Heat Sheet"

# ==========================================================
# NORMALIZE TEAM NAMES
# ==========================================================

TEAM_MAP = {
    "Old North State-NC": "ONSA-NC",
    "Greensboro Swimm-NC": "GSA-NC",
    "North Carolina A-NC": "NCAC-NC",
    "SwimMAC Carolina-NC": "MAC-NC",
    "Tac Titans-NC": "TAC-NC",
    "YMCA of the Tria-NC": "YOTA",
    "Marlins Of Ralei-NC": "MOR-NC",
}

def format_team_name(team: str) -> str:
    """
        Convert full/truncated team names from psych sheets
        into short heat sheet display names.

        Examples:
            Old North State-NC       -> ONSA-NC
            Greensboro Swimm-NC      -> GSA-NC
            North Carolina A-NC      -> NCAC-NC
            SwimMAC Carolina-NC      -> MAC-NC
            Tac Titans-NC            -> TAC-NC
            YMCA of the Tria-NC      -> YOTA
            Marlins Of Ralei-NC      -> MOR-NC
        """

    if not team:
        return ""

    # Normalize whitespace
    team = " ".join(team.strip().split())

    # Exact mapping
    return TEAM_MAP.get(team, team)

    return team
