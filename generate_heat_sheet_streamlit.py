import streamlit as st
import pypdf
import re
import json
from fpdf import FPDF

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
        "'": "'",
        """: '"',
        """: '"'
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
        line = re.sub(r"\bpsych\s+sheet\b", "Heat Sheet", line, flags=re.IGNORECASE)
        line = re.sub(r"\bpsyc\s+sheet\b", "Heat Sheet", line, flags=re.IGNORECASE)

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

    for page in reader.pages:
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
    mixed_base_event = None

    event_re = re.compile(r'(?:Event\s+|#)(\d+)\s+(.*)')
    gender_header_re = re.compile(r'^(W\d+|M\d+)$', re.IGNORECASE)
    
    seed_time_pattern = r'(NT|\d+:?\d*\.\d+)'

    swimmer_re_A = re.compile(r'^(\S+)\s+' + seed_time_pattern + r'\s+(\d+)\s+(.*?)\s+(\d+)$')
    swimmer_re_B = re.compile(r'^(\S+)\s+' + seed_time_pattern + r'\s*([MW]?\d+|Boys|Girls)\s*(.*?)\s*(\d+)$')
    swimmer_re_C = re.compile(r'^(\d+)\s+(.*?)\s+([MW]?\d+|Boys|Girls)\s+(\S+)\s+' + seed_time_pattern + r'$')

    for line in text_content.splitlines():
        line = clean_line(line)
        if not line:
            continue
            
        # =============
        # Event header
        # =============
        event_match = event_re.search(line)
        if event_match:
            event_num = event_match.group(1)
            event_name = event_match.group(2).replace("...", "").strip()

            # ===================================
            # Page-break continuation:
            # Event header repeated on next page
            # ===================================
            if (current_event
                and current_event["number"] == event_num
                and len(current_event["swimmers"]) > 0
            ):
                # repeated header due to page break
                continue

            # ============
            # Mixed event
            # ============
            if "mixed" in event_name.lower():
                mixed_base_event = {
                    "number": event_num,
                    "name": event_name
                }
                current_event = None
            else:
                mixed_base_event = None
            
                current_event = {
                    "number": event_num,
                    "name": event_name,
                    "swimmers": []
                }
                events.append(current_event)
                
            continue

        # ===========================
        # Mixed-event gender section
        # ===========================
        gender_match = gender_header_re.match(line)

        if gender_match and mixed_base_event:
            gender_code = gender_match.group(1).upper()

            gender_name = (
                "Girls"
                if gender_code.startswith("W")
                else "Boys"
            )

            current_event = {
                "number": mixed_base_event["number"],
                "name": f"{mixed_base_event['name']} - {gender_name}",
                "swimmers": []
            }

            events.append(current_event)
            continue

        # ====================================
        # Ignore lines until we have an event
        # ====================================
        if not current_event:
            continue

        swimmer_data = None

        # =========
        # Format B
        # =========
        mB = swimmer_re_B.match(line)
        if mB:
            age_match = re.search(r'\d+', mB.group(3))
            swimmer_data = {
                "team": mB.group(1),
                "seed_time": mB.group(2),
                "age": age_match.group(0) if age_match else mB.group(3),
                "name": mB.group(4).strip(),
                "rank": int(mB.group(5))
            }

        # =========
        # Format A
        # =========
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
    swimmers = sorted(event['swimmers'], key=lambda x: x['rank'])
    if not swimmers: return []
    num_swimmers = len(swimmers)
    num_heats = (num_swimmers + lanes - 1) // lanes
    heats_swimmers = []
    remaining = swimmers[:]
    for h in range(num_heats, 0, -1):
        count = lanes if h > 1 else len(remaining)
        if h > 1 and len(remaining) - count < 1 and len(remaining) > 1:
            count = len(remaining) - 1
        heats_swimmers.append(remaining[:count])
        remaining = remaining[count:]
    heats_swimmers.reverse()
    lane_order = [4, 5, 3, 6, 2, 7, 1, 8] if lanes == 8 else [3, 4, 2, 5, 1, 6]
    final_heats = []
    for i, h_list in enumerate(heats_swimmers):
        h_list.sort(key=lambda x: x['rank'])
        assigned = {str(lane_order[j]): s for j, s in enumerate(h_list) if j < len(lane_order)}
        final_heats.append({'heat_number': i + 1, 'lanes': assigned})
    return final_heats

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

    # st.download_button(
    #     "Download JSON",
    #     json.dumps(heat_sheet, indent=2),
    #     file_name="heat_sheet.json",
    #     mime="application/json"
    # )

    pdf_bytes = generate_pdf(meet_title, heat_sheet, favorites)

    st.download_button(
        "Download PDF",
        pdf_bytes,
        file_name="heat_sheet.pdf",
        mime="application/pdf"
    )
