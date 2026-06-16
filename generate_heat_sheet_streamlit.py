import streamlit as st
import pypdf
import re
import json
from fpdf import FPDF

# ==========================================================
# UI CONFIG
# ==========================================================
def get_ui_options():
    heat_order = st.selectbox(
        "Heat Seeding Order (400m+ events)",
        ["fast_to_slow", "slow_to_fast", "circle_seed"],
        index=0
    )

    heat_size = st.number_input(
        "Heat Size (lanes)",
        min_value=4,
        max_value=10,
        value=8
    )

    return heat_order, heat_size

# ==========================================================
# UTILS
# ==========================================================
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

    # remove any remaining non-latin1 chars
    return text.encode("latin-1", "ignore").decode("latin-1")

def time_to_seconds(t):
    if not t or t == "NT":
        return 9999

    try:
        if ":" in t:
            m, s = t.split(":")
            return int(m) * 60 + float(s)
        return float(t)
    except:
        return 9999

def event_is_long_distance(event):
    name = event["name"].lower()
    return any(x in name for x in ["400", "500", "800", "1500"])
        
# ==========================================================
# TEXT PROCESSING
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

# ==========================================================
# PDF TEXT EXTRACTION
# ==========================================================
def extract_text_from_pdf(file):
    reader = pypdf.PdfReader(file)
    return "\n".join(
        page.extract_text() or ""
        for page in reader.pages
    )

# ==========================================================
# CLEANUP
# ==========================================================

def clean_line(line):
    line = line.replace("Butter7ly", "Butterfly")
    line = line.replace("Butterﬂy", "Butterfly")
    line = line.replace("CrutchEield", "Crutchfield")
    line = line.replace("Crutchﬁeld", "Crutchfield")
    line = line.replace("-NC", "")
    return line.strip()


# ==========================================================
# PARSER
# ==========================================================
def parse_psych_sheet(text_content):
    events = []
    current_event = None

    event_re = re.compile(r'(?:Event\s+|#)(\d+)\s+(.*)')
    gender_header_re = re.compile(r'^(W\d+|M\d+)\s*&?\s*Under', re.IGNORECASE)

    seed_time_pattern = r'(NT|\d+:?\d*\.\d+)'

    swimmer_re_A = re.compile(r'^(\S+)\s+' + seed_time_pattern + r'\s+(\d+)\s+(.*?)\s+(\d+)$')
    swimmer_re_B = re.compile(r'^(\S+)\s+' + seed_time_pattern + r'\s*([MW]?\d+|Boys|Girls|W\d+|M\d+)\s*(.*?)\s*(\d+)$')
    swimmer_re_C = re.compile(r'^(\d+)\s+(.*?)\s+([MW]?\d+|Boys|Girls|W\d+|M\d+)\s+(\S+)\s+' + seed_time_pattern + r'$')

    current_gender = None

    for line in text_content.splitlines():
        line = clean_line(line)
        if not line:
            continue

        # EVENT
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

        # GENDER HEADER
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

# ==========================================================
# SEEDING
# ==========================================================
def seed_swimmers(event, heat_size, order):
    swimmers = event["swimmers"]
    swimmers_sorted = sorted(swimmers, key=lambda x: time_to_seconds(x.get("seed_time")))

    if order == "slow_to_fast":
        swimmers_sorted.reverse()

    heat_num = 1
    result = []

    for i, s in enumerate(swimmers_sorted):
        s = dict(s)
        s["heat"] = heat_num
        result.append(s)

        if (i + 1) % heat_size == 0:
            heat_num += 1

    return result

# ==========================================================
# BUILD HEAT SHEET
# ==========================================================
def build_heat_sheet(events, heat_size, order):

    heat_sheet = []

    for e in events:

        swimmers = e["swimmers"]

        if "mixed" in e["name"].lower() or event_is_long_distance(e):
            swimmers = seed_swimmers(e, heat_size, order)

        heat_sheet.append({
            "number": e["number"],
            "name": e["name"],
            "heats": seed_event({"swimmers": swimmers})
        })

    return heat_sheet
    
# ==========================================================
# FAVORITES INDEX
# ==========================================================

def build_index(heat_sheet, favorites):
    index = {f: [] for f in favorites}

    for event in heat_sheet:
        for heat in event["heats"]:
            for lane, s in heat["lanes"].items():
                if s["name"] in favorites:
                    index[s["name"]].append(
                        f"Event {event['number']} Heat {heat['heat_number']} Lane {lane} {event['name']}"
                    )
    return index


# ==========================================================
# PDF GENERATION
# ==========================================================

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.line_height = 5

    def header(self):
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 8, self.title, ln=1, align="C")
        self.ln(2)

    def print_heat(self, heat, event_total_heats, x, y):
        self.set_xy(x, y)
        start_y =y

        self.set_font("Helvetica", "B", 9)
        self.cell(0, 6, safe_text(f"Heat {heat['heat_number']} of {event_total_heats}"), ln=1)

        self.set_font("Helvetica", "", 9)
        for lane in range(1, 9):
            s = heat["lanes"].get(str(lane))
            if not s:
                continue

            name = s["name"][:20]

            self.set_x(x)
            self.cell(5, self.line_height, str(lane), 0, 0, 'C')
                    
            self.set_font("Helvetica", "", 10)
            self.cell(50, self.line_height, name, 0, 0, 'L')
            
            self.set_font("Helvetica", "", 9)
            self.cell(5, self.line_height, str(s['age']), 0, 0, 'C')
            self.cell(10, self.line_height, s.get('team', '')[:8], 0, 0, 'L')
            self.set_font("Helvetica", "", 10)
            self.cell(20, self.line_height, s['seed_time'], 0, 1, 'R')

        return self.get_y() - start_y   # return height ONLY


def generate_pdf(meet_title, heat_sheet, favorites):
    def __init__(self):
        super().__init__()

    pdf = PDF()
    pdf.title = meet_title

    pdf.set_auto_page_break(True, margin=10)

    # ---------------- FAVORITES PAGE ----------------
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, "Favorite Swimmers", ln=1)

    index = build_index(heat_sheet, favorites)

    pdf.set_font("Helvetica", "", 11)

    for name, items in index.items():
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 6, name, ln=1)

        pdf.set_font("Helvetica", "", 10)
        for it in items:
            pdf.cell(5, 5, it, ln=1)

    # ---------------- SUMMARY PAGE ----------------
    # pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, "Meet Summary", ln=1)

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 6, f"Events: {len(heat_sheet)}", ln=1)
    pdf.cell(0, 6, f"Favorites: {len(favorites)}", ln=1)

    pdf.add_page()
    # two-column page
    page_width = pdf.w - 2 * pdf.l_margin
    col_width = page_width / 2
    
    # ---------------- HEAT SHEETS ----------------
    col = 0
    x_left = pdf.l_margin
    x_right = pdf.l_margin + col_width
    y_left = pdf.get_y()
    y_right = pdf.get_y()
    top_y = pdf.get_y()
    
    for event in heat_sheet:
        # --- EVENT HEADER (full width) ---
        pdf.set_font("Helvetica", "B", 9)
        start_y = pdf.get_y()
        x = x_left if col == 0 else x_right
        y = y_left if col == 0 else y_right        
        pdf.set_xy(x, y)
        pdf.cell(0, 6, safe_text(f"Event {event['number']}: {event['name']}"))

        # sync both columns after header
        if col == 0:
            y_left += 5
        else:
            y_right += 5

        event_total_heats = len(event["heats"])
        for heat in event["heats"]:
            # estimate height (important for page breaks)
            estimated_height = 8 * pdf.line_height + 10

            # pick correct column position
            if col == 0:
                x = x_left
                y = y_left

                # if left column full -> switch to right
                if y + estimated_height > pdf.h - pdf.b_margin:
                    col = 1
                    x = x_right
                    y = y_right
            
            else:
                x = x_right
                y = y_right

                # page right column full -> new page
                if y + estimated_height > pdf.h - pdf.b_margin:
                    pdf.add_page()
                    pdf.set_font("Helvetica", "B", 9)
                    pdf.cell(0, 6, safe_text(f"Event {event['number']}: {event['name']}"))
                    y_left = pdf.get_y() + 5
                    y_right = pdf.get_y()
                    col = 0;
                    x = x_left
                    y = y_left
                        
            # print heat
            h = pdf.print_heat(heat, event_total_heats, x, y)

            # update ONLY that column's Y
            if col == 0:
                y_left += h+5
            else:
                y_right += h+5

    return bytes(pdf.output())

def generate_html_preview(meet_title, heat_sheet, favorites):
    rows = []
    for event in heat_sheet:
        rows.append(f"""
            <div class="event-header">
                Event {event['number']}: {event['name']}
                <span class="heat-count">({len(event['heats'])} heats)</span>
            </div>
        """)
        for heat in event["heats"]:
            rows.append(f"<div class='heat-header'>Heat {heat['heat_number']}</div>")
            rows.append("<table><tr><th>Ln</th><th>Name</th><th>Age</th><th>Team</th><th>Seed</th></tr>")
            for lane in range(1, 9):
                s = heat["lanes"].get(str(lane))
                if not s:
                    continue
                name     = s.get("name", "")
                is_fav   = name in favorites
                name_disp = f"★ {name}" if is_fav else name
                fav_class = "favorite" if is_fav else ""
                rows.append(f"""
                    <tr class="{fav_class}">
                        <td class="center">{lane}</td>
                        <td>{name_disp}</td>
                        <td class="center">{s.get('age','')}</td>
                        <td class="center">{s.get('team','')}</td>
                        <td class="right">{s.get('seed_time','')}</td>
                    </tr>
                """)
            rows.append("</table>")

    body = "\n".join(rows)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body        {{ font-family: Helvetica, sans-serif; font-size: 9pt;
                 column-count: 2; column-gap: 12mm; }}
  h1          {{ column-span: all; text-align: center; font-size: 13pt; }}
  .event-header {{ font-weight: bold; font-size: 10pt; margin-top: 10pt;
                   border-bottom: 2px solid #000; column-span: none; }}
  .heat-count {{ font-weight: normal; font-size: 8pt; color: #555; }}
  .heat-header {{ font-weight: bold; margin-top: 6pt; font-size: 9pt; }}
  table       {{ width: 100%; border-collapse: collapse; margin-top: 2pt; }}
  th          {{ background: #eee; font-size: 7pt; border: 1px solid #aaa;
                 padding: 2px 3px; }}
  td          {{ border: 1px solid #ccc; padding: 2px 3px; font-size: 8.5pt;
                 white-space: nowrap; overflow: hidden; }}
  .center     {{ text-align: center; }}
  .right      {{ text-align: right; }}
  .favorite   {{ font-weight: bold; text-decoration: underline;
                 background: #fffbcc; }}
</style>
</head>
<body>
<h1>{meet_title}</h1>
{body}
</body>
</html>"""

# ==========================================================
# STREAMLIT UI
# ==========================================================

st.set_page_config(page_title="Heat Sheet Generator", layout="wide")
st.title("🏊 Swim Meet Heat Sheet Generator")

heat_order, heat_size = get_ui_options()

uploaded_file = st.file_uploader("Upload Psych Sheet PDF", type=["pdf"])

if uploaded_file:

    text = extract_text_from_pdf(uploaded_file)
    meet_title = extract_meet_title(text)

    events = parse_psych_sheet(text)

    all_swimmers = sorted({s["name"] for e in events for s in e["swimmers"]})

    favorites = st.multiselect("Favorites", all_swimmers)

    heat_sheet = build_heat_sheet(events, heat_size, heat_order)

    html = generate_html_preview(meet_title, heat_sheet, favorites)

    st.components.v1.html(html, height=600, scrolling=True)

    col1, col2 = st.columns(2)

    with col1:
        st.download_button("Download HTML", html, "heat.html")

    with col2:
        pdf_bytes = generate_pdf(meet_title, heat_sheet, set(favorites))
        st.download_button("Download PDF", pdf_bytes, "heat.pdf")
