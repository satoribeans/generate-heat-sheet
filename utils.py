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

TEAM_NAME_MAP = {
    "Aquatic Team Of" :  "ATOM-NC",
    "Asheville Jewish": "AJCC-NC",
    "Carolina Aquatic": "CAT-NC",
    "Catawba Valley A": "CVAC-NC",
    "Crystal Coast Aq": "CCA-NC",
    "East Carolina Aq": "ECA-NC",
    "Enfinity Aquatic": "EAC-NC",
    "Gaston Gators"   : "GG-NC",
    "Granite Falls Sw": "GFSC-NC",
    "Greensboro Commu": "GCY-NC",
    "Greensboro Swimm": "GSA-NC",
    "Hickory Foundati": "YSST-NC",
    "Hillsborough Aqu": "HAC-NC",
    "Life Time North" : "LIFE-NC",
    "Marlins Of Ralei": "MOR-NC",
    "MCA of Northwes" : "TYDE-NC",
    "MCA of the Tria" : "YOTA",
    "MCA of Western"  :  "WNCY-NC",
    "Mecklenburg Swim": "MSA-NC",
    "New Wave Swim Te": "WAVE-NC",
    "North Carolina A": "NCAC-NC",
    "Nsea Swim"       : "NSEA-NC",
    "O'Neal Aquatics" : "NEAL-NC",
    "Old North State" : "ONSA-NC",
    "Queen City Dolph": "QCD-NC",
    "Raleigh Swimming": "RSA-NC",
    "Rocky Mount Fami": "RMY-NC",
    "Sailfish Aquatic": "SAIL-NC",
    "Sharks Aquatic C": "SAC-NC",
    "Star Aquatics"   : "STAR-NC",
    "Streamline Aquat": "SAQ-NC",
    "SwimMAC Carolina": "MAC-NC",
    "Tac Titans"      : "TAC-NC",
    "Team Charlotte S": "TEAM-NC",
    "Unattached"      : "UN-NC",
    "Watauga County S": "WST-NC",
    "Waves Of Wilming": "WOW-NC",
    "YMCA of Northwes": "TYDE-NC",
    "YMCA of the Tria": "YOTA",
    "YMCA of Western":  "WNCY-NC",
}

def get_team_code(team: str) -> str:
    """
        Convert full/truncated team names from psych sheets
        into short heat sheet display names.

        Examples:
            Old North State       -> ONSA-NC
            Greensboro Swimm      -> GSA-NC
            North Carolina A      -> NCAC-NC
            SwimMAC Carolina      -> MAC-NC
            Tac Titans            -> TAC-NC
            YMCA of the Tria      -> YOTA
            Marlins Of Ralei      -> MOR-NC
        """

    if not team:
        return ""

    # Normalize whitespace
    team = " ".join(team.strip().split())

    # Exact mapping
    return TEAM_NAME_MAP.get(team, team)
