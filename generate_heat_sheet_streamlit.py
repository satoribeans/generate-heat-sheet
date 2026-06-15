
import streamlit as st
import pypdf
import re
import json
from fpdf import FPDF
from io import BytesIO

# ==========================================================
# HELPERS
# ==========================================================
def safe_text(text):
    if not text:
        return ""

    replacements = {
        "★": "*",
        "–": "-",
        "—": "-",
        "’": "'",
        "“": '"',
        "”": '"'
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    # remove any remaining non-latin1 chars
    return text.encode("latin-1", "ignore").decode("latin-1")

# ==========================================================
# MEET TITLE EXTRACTION
# ==========================================================

def extract_meet_title(text):
    lines = text.splitlines()

    title_lines = []
    for line in lines[:30]:  # only scan top of doc
        line = line.strip()

        if not line:
            continue

        # stop when we hit event list
        if re.search(r'(?:Event\s+|#)\d+', line):
            break

        # skip page markers
        if "PAGE" in line.upper():
            continue

        # likely header content
        if len(line) > 5:
            title_lines.append(line)

    if title_lines:
        return " - ".join(title_lines[:3])

    return "Swim Meet Heat Sheet"


# ==========================================================
# PDF EXTRACTION
# ==========================================================

def extract_text_from_pdf(uploaded_file):
    reader = pypdf.PdfReader(uploaded_file)
    full_text = ""

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            full_text += text + "\n"

    return full_text


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
    seed_time_pattern = r'(NT|\d+:?\d*\.\d+)'

    swimmer_re_A = re.compile(r'^(\S+)\s+' + seed_time_pattern + r'\s+(\d+)\s+(.*?)\s+(\d+)$')
    swimmer_re_B = re.compile(r'^(\S+)\s+' + seed_time_pattern + r'\s*([MW]?\d+|Boys|Girls)\s*(.*?)\s*(\d+)$')
    swimmer_re_C = re.compile(r'^(\d+)\s+(.*?)\s+([MW]?\d+|Boys|Girls)\s+(\S+)\s+' + seed_time_pattern + r'$')

    for line in text_content.splitlines():
        line = clean_line(line)
        if not line:
            continue

        event_match = event_re.search(line)
        if event_match:
            current_event = {
                "number": event_match.group(1),
                "name": event_match.group(2).replace("...", "").strip(),
                "swimmers": []
            }
            events.append(current_event)
            continue

        if not current_event:
            continue

        swimmer_data = None

        mB = swimmer_re_B.match(line)
        if mB:
            swimmer_data = {
                "team": mB.group(1),
                "seed_time": mB.group(2),
                "age": re.search(r'\d+', mB.group(3)).group(0) if re.search(r'\d+', mB.group(3)) else mB.group(3),
                "name": mB.group(4).strip(),
                "rank": int(mB.group(5))
            }

        if not swimmer_data:
            mC = swimmer_re_C.match(line)
            if mC:
                swimmer_data = {
                    "rank": int(mC.group(1)),
                    "name": mC.group(2).strip(),
                    "age": mC.group(3),
                    "team": mC.group(4),
                    "seed_time": mC.group(5)
                }

        if not swimmer_data:
            mA = swimmer_re_A.match(line)
            if mA:
                swimmer_data = {
                    "team": mA.group(1),
                    "seed_time": mA.group(2),
                    "age": mA.group(3),
                    "name": mA.group(4).strip(),
                    "rank": int(mA.group(5))
                }

        if swimmer_data:
            current_event["swimmers"].append(swimmer_data)

    return events


# ==========================================================
# SEEDING
# ==========================================================

def seed_event(event, lanes=8):
    swimmers = sorted(event["swimmers"], key=lambda x: x["rank"])
    if not swimmers:
        return []

    num_heats = (len(swimmers) + lanes - 1) // lanes
    remaining = swimmers[:]
    heats = []

    for h in range(num_heats):
        chunk = remaining[:lanes]
        remaining = remaining[lanes:]

        lane_order = [4,5,3,6,2,7,1,8]
        assigned = {
            str(lane_order[i]): s
            for i, s in enumerate(chunk)
        }

        heats.append({
            "heat_number": h+1,
            "lanes": assigned
        })

    return heats


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
                        f"Event {event['number']} Heat {heat['heat_number']} Lane {lane}"
                    )
    return index


# ==========================================================
# PDF GENERATION (OPTION A)
# ==========================================================

class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 8, self.title, ln=1, align="C")
        self.ln(2)
    
    line_height = 5

# --- print heat as a block ---
def print_heat(pdf, heat, x, y):
    pdf.set_xy(x, y)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, safe_text(f"Heat {heat['heat_number']}"), ln=1)

    pdf.set_font("Helvetica", "", 9)

    for lane in range(1, 9):
        s = heat["lanes"].get(str(lane))
        if not s:
            continue

        name = s["name"][:20]

        pdf.set_x(x)
        pdf.cell(5, line_height, str(lane), 0, 0, 'C')
        pdf.cell(30, line_height, name, 0, 0, 'L')
        pdf.cell(8, line_height, str(s['age']), 0, 0, 'C')
        pdf.cell(20, line_height, s.get('team','')[:8], 0, 0, 'L')
        pdf.cell(20, line_height, s['seed_time'], 0, 1, 'R')

    return pdf.get_y()

def generate_pdf(meet_title, heat_sheet, favorites):
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
            pdf.cell(0, 5, it, ln=1)

    # ---------------- SUMMARY PAGE ----------------
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, "Meet Summary", ln=1)

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 6, f"Events: {len(heat_sheet)}", ln=1)
    pdf.cell(0, 6, f"Favorites: {len(favorites)}", ln=1)

    # ---------------- HEAT SHEETS ----------------
    # for event in heat_sheet:
    #     pdf.add_page()
    #     pdf.set_font("Helvetica", "B", 11)
    #     pdf.multi_cell(0, 6, safe_text(f"Event {event['number']}: {event['name']}"))

    #     for heat in event["heats"]:
    #         pdf.set_font("Helvetica", "B", 10)
    #         pdf.set_x(pdf.l_margin)
    #         pdf.cell(0, 6, safe_text(f"Heat {heat['heat_number']}"), align='L', ln=1)

    #         pdf.set_font("Helvetica", "", 10)
    #         for lane in range(1, 9):
    #             s = heat["lanes"].get(str(lane))
    #             if s:
    #                 name = s["name"]
    #                 if name in favorites:
    #                     name = "* " + name

    #                 # line = f"{lane} {name[:25]:25} {s['age']} {s.get('team','')} {s['seed_time']}"
    #                 # pdf.cell(0, 5, safe_text(line), ln=1)

    #                 pdf.cell(5, 5, str(lane), border=0, align='C')
    #                 pdf.cell(40, 5, name[:25], border=0, align='L')
    #                 pdf.cell(5, 5, str(s['age']), border=0, align='C')
    #                 pdf.cell(10, 5, s.get('team', ''), border=0, align='L')
    #                 pdf.cell(15, 5, s['seed_time'], border=0, align='R')
    #                 pdf.ln()

    for event in heat_sheet:
        pdf.add_page()
        # two-column page
        page_width = pdf.w - 2 * pdf.l_margin
        col_width = page_width / 2
    
        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 6, safe_text(f"Event {event['number']}: {event['name']}"))
    
        x_left = pdf.l_margin
        x_right = pdf.l_margin + col_width
        y_start = pdf.get_y()
    
        col = 0
        x = x_left
        y = y_start
    
        for heat in event["heats"]:
            # estimate height (important for page breaks)
            estimated_height = 8 * line_height + 10
    
            # page break check
            if y + estimated_height > pdf.h - pdf.b_margin:
                pdf.add_page()
                y = pdf.get_y()
                col = 0
                x = x_left
    
            # switch column
            if col == 1:
                x = x_right
            else:
                x = x_left
    
            y = print_heat(pdf, heat, x, y)
    
            # move to next column or next row
            if col == 0:
                col = 1
            else:
                col = 0
                y += 8 * line_height + 5

    return bytes(pdf.output())

# ==========================================================
# STREAMLIT UI
# ==========================================================

st.set_page_config(page_title="Heat Sheet Generator", layout="wide")
st.title("🏊 Swim Meet Heat Sheet Generator")

uploaded_file = st.file_uploader("Upload Psych Sheet PDF", type=["pdf"])

if uploaded_file:

    text = extract_text_from_pdf(uploaded_file)
    meet_title = extract_meet_title(text)

    events = parse_psych_sheet(text)

    all_swimmers = sorted({
        s["name"]
        for e in events
        for s in e["swimmers"]
    })

    st.subheader("Select Favorite Swimmers")
    favorites = st.multiselect("Favorites", all_swimmers)

    st.caption(f"Meet: {meet_title}")

    heat_sheet = []
    for e in events:
        heat_sheet.append({
            "number": e["number"],
            "name": e["name"],
            "heats": seed_event(e)
        })

    st.download_button(
        "Download JSON",
        json.dumps(heat_sheet, indent=2),
        file_name="heat_sheet.json",
        mime="application/json"
    )

    pdf_bytes = generate_pdf(meet_title, heat_sheet, favorites)

    st.download_button(
        "Download PDF",
        pdf_bytes,
        file_name="heat_sheet.pdf",
        mime="application/pdf"
    )
