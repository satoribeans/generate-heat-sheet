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

    for line in lines[:30]:
        line = line.strip()

        line = re.sub(r"\bpsych\s+sheet\b", "Heat Sheet", line, flags=re.IGNORECASE)
        line = re.sub(r"\bpsyc\s+sheet\b", "Heat Sheet", line, flags=re.IGNORECASE)

        if not line:
            continue

        if re.search(r'(?:Event\s+|#)\d+', line):
            break

        if "PAGE" in line.upper():
            continue

        title_lines.append(line)

    return " - ".join(title_lines[:3]) if title_lines else "Swim Meet Heat Sheet"


# def extract_meet_title(text):
#     header = " ".join(text.splitlines()[:10])
#     current_year = str(datetime.now().year)

#     # Case 1: year is present
#     match = re.search(
#         r'^(\d{4}\s+.+?)\s*-\s*\d{1,2}/\d{1,2}/\d{4}\s+to\s+\d{1,2}/\d{1,2}/\d{4}',
#         header
#     )

#     if match:
#         return match.group(1).strip()

#     # Case 2: no year, but still has meet title + date range
#     match = re.search(
#         r'^(.+?)\s*-\s*\d{1,2}/\d{1,2}/\d{4}\s+to\s+\d{1,2}/\d{1,2}/\d{4}',
#         header
#     )

#     if match:
#         title = match.group(1).strip()

#         # If it does NOT start with a year, prepend current year
#         if not re.match(r'^\d{4}', title):
#             title = f"{current_year} {title}"

#         return title

#     return "Swim Meet"
