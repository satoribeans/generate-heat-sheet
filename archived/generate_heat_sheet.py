
import streamlit as st
from parser import parse_psych_sheet
from seeding import build_heat_sheet
from pdf_export import generate_pdf
from html_export import generate_html_preview
from utils import is_long_event
import pypdf

st.set_page_config(page_title="Heat Sheet Generator", layout="wide")
st.title("🏊 Swim Meet Heat Sheet Generator")

heat_order = st.selectbox(
    "Heat Order",
    ["fast_to_slow", "slow_to_fast"]
)

heat_size = st.number_input("Heat Size", 4, 10, 8)

uploaded = st.file_uploader("Upload PDF", type=["pdf"])

html_content = generate_html_preview(
    meet_title,
    heat_sheet,
    set(favorites)
)

if uploaded:

    reader = pypdf.PdfReader(uploaded)
    text = "\n".join(p.extract_text() or "" for p in reader.pages)

    events = parse_psych_sheet(text)

    all_names = sorted({s["name"] for e in events for s in e["swimmers"]})
    favorites = st.multiselect("Favorites", all_names)

    heat_sheet = build_heat_sheet(
        events,
        heat_size,
        heat_order,
        is_long_event
    )

    st.success("Heat sheet generated!")

    with st.expander("👁 Preview Heat Sheet", expanded=True):
    st.components.v1.html(
        html_content,
        height=800,
        scrolling=True
    )

    pdf_bytes = generate_pdf("Meet Heat Sheet", heat_sheet, set(favorites))

    st.download_button(
    "⬇ Download HTML",
    html_content,
    file_name="heat_sheet.html",
    mime="text/html"
)


# from fpdf import FPDF
# import streamlit as st
# import pypdf
# import re
# import json

# # ==========================================================
# # UI OPTIONS
# # ==========================================================
# def get_ui_options():
#     heat_order = st.selectbox(
#         "Heat Seeding Order (400m+ events)",
#         ["fast_to_slow", "slow_to_fast", "circle_seed"],
#         index=0
#     )

#     heat_size = st.number_input(
#         "Heat Size (lanes)",
#         min_value=4,
#         max_value=10,
#         value=8
#     )

#     return heat_order, heat_size


# # ==========================================================
# # HELPERS
# # ==========================================================
# def safe_text(text):
#     if not text:
#         return ""
#     return text.encode("latin-1", "ignore").decode("latin-1")


# def time_to_seconds(t):
#     if not t or t == "NT":
#         return 9999
#     try:
#         if ":" in t:
#             m, s = t.split(":")
#             return int(m) * 60 + float(s)
#         return float(t)
#     except:
#         return 9999


# def event_is_long_distance(event):
#     name = event["name"].lower()
#     return any(x in name for x in ["400", "500", "800", "1500"])


# # ==========================================================
# # TITLE EXTRACTION
# # ==========================================================
# def extract_meet_title(text):
#     lines = text.splitlines()
#     title_lines = []

#     for line in lines[:30]:
#         line = line.strip()

#         line = re.sub(r"\bpsych\s+sheet\b", "Heat Sheet", line, flags=re.IGNORECASE)
#         line = re.sub(r"\bpsyc\s+sheet\b", "Heat Sheet", line, flags=re.IGNORECASE)

#         if not line:
#             continue

#         if re.search(r'(?:Event\s+|#)\d+', line):
#             break

#         if "PAGE" in line.upper():
#             continue

#         title_lines.append(line)

#     return " - ".join(title_lines[:3]) if title_lines else "Swim Meet Heat Sheet"


# # ==========================================================
# # PDF TEXT EXTRACTION
# # ==========================================================
# def extract_text_from_pdf(uploaded_file):
#     reader = pypdf.PdfReader(uploaded_file)
#     return "\n".join(page.extract_text() or "" for page in reader.pages)


# # ==========================================================
# # CLEAN LINE
# # ==========================================================
# def clean_line(line):
#     return (
#         line.replace("Butter7ly", "Butterfly")
#             .replace("Butterﬂy", "Butterfly")
#             .replace("CrutchEield", "Crutchfield")
#             .replace("Crutchﬁeld", "Crutchfield")
#             .replace("-NC", "")
#             .strip()
#     )


# # ==========================================================
# # PARSER
# # ==========================================================
# def parse_psych_sheet(text_content):
#     events = []
#     current_event = None

#     event_re = re.compile(r'(?:Event\s+|#)(\d+)\s+(.*)')
#     gender_header_re = re.compile(r'^(W\d+|M\d+)\s*&?\s*Under', re.IGNORECASE)

#     seed_time_pattern = r'(NT|\d+:?\d*\.\d+)'

#     swimmer_re_A = re.compile(r'^(\S+)\s+' + seed_time_pattern + r'\s+(\d+)\s+(.*?)\s+(\d+)$')
#     swimmer_re_B = re.compile(r'^(\S+)\s+' + seed_time_pattern + r'\s*([MW]?\d+|Boys|Girls|W\d+|M\d+)\s*(.*?)\s*(\d+)$')
#     swimmer_re_C = re.compile(r'^(\d+)\s+(.*?)\s+([MW]?\d+|Boys|Girls|W\d+|M\d+)\s+(\S+)\s+' + seed_time_pattern + r'$')

#     current_gender = None

#     for line in text_content.splitlines():
#         line = clean_line(line)
#         if not line:
#             continue

#         # EVENT
#         m = event_re.search(line)
#         if m:
#             num, name = m.group(1), m.group(2).replace("...", "").strip()

#             if current_event and current_event["number"] == num:
#                 continue

#             current_gender = None

#             current_event = {
#                 "number": num,
#                 "name": name,
#                 "swimmers": []
#             }
#             events.append(current_event)
#             continue

#         # GENDER HEADER
#         gm = gender_header_re.match(line)
#         if gm:
#             current_gender = gm.group(1)[0].upper()
#             continue

#         if not current_event:
#             continue

#         swimmer = None

#         for regex in (swimmer_re_B, swimmer_re_C, swimmer_re_A):
#             match = regex.match(line)
#             if match:
#                 if regex == swimmer_re_B:
#                     swimmer = {
#                         "team": match.group(1),
#                         "seed_time": match.group(2),
#                         "age": match.group(3),
#                         "name": match.group(4).strip(),
#                         "rank": int(match.group(5))
#                     }
#                 elif regex == swimmer_re_C:
#                     swimmer = {
#                         "rank": int(match.group(1)),
#                         "name": match.group(2).strip(),
#                         "age": match.group(3),
#                         "team": match.group(4),
#                         "seed_time": match.group(5)
#                     }
#                 else:
#                     swimmer = {
#                         "team": match.group(1),
#                         "seed_time": match.group(2),
#                         "age": match.group(3),
#                         "name": match.group(4).strip(),
#                         "rank": int(match.group(5))
#                     }
#                 break

#         if swimmer:
#             swimmer["gender"] = current_gender
#             current_event["swimmers"].append(swimmer)

#     return events


# # ==========================================================
# # SEEDING
# # ==========================================================
# def seed_swimmers(swimmers, heat_size, order):

#     def to_sec(t):
#         if not t or t == "NT":
#             return 9999
#         try:
#             if ":" in t:
#                 m, s = t.split(":")
#                 return int(m) * 60 + float(s)
#             return float(t)
#         except:
#             return 9999

#     swimmers_sorted = sorted(swimmers, key=lambda x: to_sec(x.get("seed_time")))

#     if order == "slow_to_fast":
#         swimmers_sorted.reverse()

#     heat_num = 1
#     result = []

#     for i, s in enumerate(swimmers_sorted):
#         s = dict(s)
#         s["heat"] = heat_num
#         result.append(s)

#         if (i + 1) % heat_size == 0:
#             heat_num += 1

#     return result


# # ==========================================================
# # BUILD HEAT SHEET
# # ==========================================================
# def build_heat_sheet(events, heat_size, heat_order):

#     heat_sheet = []

#     for e in events:

#         swimmers = e["swimmers"]

#         # apply custom seeding only for long/mixed events
#         if "mixed" in e["name"].lower() or event_is_long_distance(e):
#             swimmers = seed_swimmers(swimmers, heat_size, heat_order)

#         heat_sheet.append({
#             "number": e["number"],
#             "name": e["name"],
#             "heats": seed_event({"swimmers": swimmers})
#         })

#     return heat_sheet


# # ==========================================================
# # SIMPLE HEAT BUILDER (KEEP YOUR EXISTING LOGIC)
# # ==========================================================
# def seed_event(event, lanes=8):
#     swimmers = sorted(event["swimmers"], key=lambda x: x.get("rank", 0))
#     if not swimmers:
#         return []

#     num_heats = (len(swimmers) + lanes - 1) // lanes
#     heats_swimmers = []
#     remaining = swimmers[:]

#     for h in range(num_heats, 0, -1):
#         count = lanes if h > 1 else len(remaining)
#         heats_swimmers.append(remaining[:count])
#         remaining = remaining[count:]

#     heats_swimmers.reverse()

#     lane_order = [4, 5, 3, 6, 2, 7, 1, 8] if lanes == 8 else [3, 4, 2, 5, 1, 6]

#     final_heats = []
#     for i, h_list in enumerate(heats_swimmers):
#         h_list.sort(key=lambda x: x.get("rank", 0))
#         assigned = {
#             str(lane_order[j]): s
#             for j, s in enumerate(h_list)
#             if j < len(lane_order)
#         }
#         final_heats.append({
#             "heat_number": i + 1,
#             "lanes": assigned
#         })

#     return final_heats

# class PDF(FPDF):
#     def header(self):
#         self.set_font("Helvetica", "B", 12)
#         self.cell(0, 8, self.title, ln=1, align="C")
#         self.ln(2)

#     def print_heat(self, heat, event_total_heats, x, y):
#         self.set_xy(x, y)
#         start_y = y

#         self.set_font("Helvetica", "B", 9)
#         self.cell(0, 6, f"Heat {heat['heat_number']} of {event_total_heats}", ln=1)

#         self.set_font("Helvetica", "", 9)

#         for lane in range(1, 9):
#             s = heat["lanes"].get(str(lane))
#             if not s:
#                 continue

#             self.set_x(x)
#             self.cell(5, 5, str(lane), 0, 0, "C")
#             self.cell(50, 5, s["name"][:22], 0, 0, "L")
#             self.cell(10, 5, str(s.get("age", "")), 0, 0, "C")
#             self.cell(15, 5, s.get("team", "")[:8], 0, 0, "L")
#             self.cell(20, 5, s.get("seed_time", ""), 0, 1, "R")

#         return self.get_y() - start_y

# def generate_pdf(meet_title, heat_sheet, favorites):

#     pdf = PDF()
#     pdf.title = meet_title
#     pdf.set_auto_page_break(True, margin=10)

#     # ---------------- FAVORITES ----------------
#     pdf.add_page()
#     pdf.set_font("Helvetica", "B", 14)
#     pdf.cell(0, 8, "Favorite Swimmers", ln=1)

#     pdf.set_font("Helvetica", "", 10)

#     for event in heat_sheet:
#         for heat in event["heats"]:
#             for lane, s in heat["lanes"].items():
#                 if s["name"] in favorites:
#                     pdf.cell(0, 5,
#                              f"Event {event['number']} Heat {heat['heat_number']} Lane {lane} - {s['name']}",
#                              ln=1)

#     # ---------------- SUMMARY ----------------
#     pdf.add_page()
#     pdf.set_font("Helvetica", "B", 12)
#     pdf.cell(0, 8, "Meet Summary", ln=1)

#     pdf.set_font("Helvetica", "", 10)
#     pdf.cell(0, 6, f"Events: {len(heat_sheet)}", ln=1)
#     pdf.cell(0, 6, f"Favorites: {len(favorites)}", ln=1)

#     # ---------------- HEAT SHEETS ----------------
#     pdf.add_page()

#     x_left = pdf.l_margin
#     x_right = pdf.w / 2
#     y_left = pdf.get_y()
#     y_right = pdf.get_y()

#     col = 0

#     for event in heat_sheet:

#         x = x_left if col == 0 else x_right
#         y = y_left if col == 0 else y_right

#         pdf.set_xy(x, y)
#         pdf.set_font("Helvetica", "B", 9)
#         pdf.cell(0, 6, f"Event {event['number']}: {event['name']}", ln=1)

#         event_total_heats = len(event["heats"])

#         if col == 0:
#             y_left = pdf.get_y()
#         else:
#             y_right = pdf.get_y()

#         for heat in event["heats"]:

#             estimated_height = 8 * 5 + 10

#             if col == 0 and y_left + estimated_height > pdf.h - pdf.b_margin:
#                 col = 1
#                 x = x_right
#                 y = y_right

#             elif col == 1 and y_right + estimated_height > pdf.h - pdf.b_margin:
#                 pdf.add_page()
#                 col = 0
#                 x = x_left
#                 y_left = pdf.get_y()
#                 y_right = pdf.get_y()

#             h = pdf.print_heat(heat, event_total_heats, x, y)

#             if col == 0:
#                 y_left += h + 4
#             else:
#                 y_right += h + 4

#     return bytes(pdf.output(dest="S").encode("latin-1"))
    
# # ==========================================================
# # STREAMLIT APP
# # ==========================================================
# st.set_page_config(page_title="Heat Sheet Generator", layout="wide")
# st.title("🏊 Swim Meet Heat Sheet Generator")

# heat_order, heat_size = get_ui_options()

# uploaded_file = st.file_uploader("Upload Psych Sheet PDF", type=["pdf"])

# if uploaded_file:

#     pdf_bytes = generate_pdf(meet_title, heat_sheet, set(favorites))

#     st.download_button(
#         "⬇ Download PDF",
#         data=pdf_bytes,
#         file_name="heat_sheet.pdf",
#         mime="application/pdf"
#     )
    
#     text = extract_text_from_pdf(uploaded_file)
#     meet_title = extract_meet_title(text)

#     events = parse_psych_sheet(text)

#     all_swimmers = sorted({s["name"] for e in events for s in e["swimmers"]})

#     favorites = st.multiselect("Favorites", all_swimmers)

#     heat_sheet = build_heat_sheet(events, heat_size, heat_order)

#     st.subheader(meet_title)

#     st.json(heat_sheet[:1])  # quick debug preview

#     st.success("Heat sheet generated successfully.")
