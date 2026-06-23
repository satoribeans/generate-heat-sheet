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
            .strip()
    )


def is_long_event(name):
    name = name.lower()
    return any(x in name for x in ["400", "500", "800", "1000", "1500", "1650"])

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
        line = re.sub(r"\bpsych\s+sheet\b", "Heat Sheet", line, flags=re.IGNORECASE)
        line = re.sub(r"\bpsyc\s+sheet\b", "Heat Sheet", line, flags=re.IGNORECASE)

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
