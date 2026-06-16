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


def time_to_seconds(t):
    if not t or t == "NT":
        return 9999
    try:
        if ":" in t:
            m, s = t.split(":")
            return int(m) * 60 + float(s)
        return float(t)
    except (ValueError, TypeError):
        return 9999


def clean_line(line):
    return (
        line.replace("Butter7ly", "Butterfly")
            .replace("Butterﬂy", "Butterfly")
            .replace("CrutchEield", "Crutchfield")
            .replace("Crutchﬁeld", "Crutchfield")
            .replace("-NC", "")
            .strip()
    )


def is_long_event(name):
    name = name.lower()
    return any(x in name for x in ["400", "500", "800", "1500"])

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

