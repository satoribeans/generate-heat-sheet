import streamlit as st
import pypdf
import re
import json
import tempfile
from weasyprint import HTML

# ==========================================================
# PDF EXTRACTION
# ==========================================================

def extract_text_from_pdf(uploaded_file):
    reader = pypdf.PdfReader(uploaded_file)

    full_text = ""

    for i, page in enumerate(reader.pages):
        full_text += f"--- PAGE {i + 1} ---\n"

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

    swimmer_re_A = re.compile(
        r'^(\S+)\s+'
        + seed_time_pattern +
        r'\s+(\d+)\s+(.*?)\s+(\d+)$'
    )

    swimmer_re_B = re.compile(
        r'^(\S+)\s+'
        + seed_time_pattern +
        r'\s*([MW]?\d+|Boys|Girls)\s*(.*?)\s*(\d+)$'
    )

    swimmer_re_C = re.compile(
        r'^(\d+)\s+(.*?)\s+([MW]?\d+|Boys|Girls)\s+(\S+)\s+'
        + seed_time_pattern +
        r'$'
    )

    for line in text_content.splitlines():

        line = clean_line(line)

        if not line:
            continue

        event_match = event_re.search(line)

        if event_match:

            event_num = event_match.group(1)
            event_name = event_match.group(2).replace(
                "...", ""
            ).strip()

            is_continuation = (
                "..." in line or "(" in line
            )

            if (
                current_event
                and current_event["number"] == event_num
                and is_continuation
            ):
                continue

            current_event = {
                "number": event_num,
                "name": event_name,
                "swimmers": []
            }

            enumber = int(event_num)

            if (
                (250 < enumber < 301)
                or (enumber > 350)
            ):
                events.append(current_event)

            continue

        if current_event:

            swimmer_data = None

            match_B = swimmer_re_B.match(line)

            if match_B:

                team = match_B.group(1)
                seed_time = match_B.group(2)
                age_gender = match_B.group(3)
                name = match_B.group(4).strip()
                rank = int(match_B.group(5))

                age_match = re.search(
                    r'\d+',
                    age_gender
                )

                age = (
                    age_match.group(0)
                    if age_match
                    else age_gender
                )

                swimmer_data = {
                    "name": name,
                    "age": age,
                    "team": team,
                    "seed_time": seed_time,
                    "rank": rank
                }

            if not swimmer_data:

                match_C = swimmer_re_C.match(line)

                if match_C:

                    swimmer_data = {
                        "rank": int(match_C.group(1)),
                        "name": match_C.group(2).strip(),
                        "age": re.search(
                            r'\d+',
                            match_C.group(3)
                        ).group(0)
                        if re.search(
                            r'\d+',
                            match_C.group(3)
                        )
                        else match_C.group(3),
                        "team": match_C.group(4),
                        "seed_time": match_C.group(5)
                    }

            if not swimmer_data:

                match_A = swimmer_re_A.match(line)

                if match_A:

                    swimmer_data = {
                        "team": match_A.group(1),
                        "seed_time": match_A.group(2),
                        "age": match_A.group(3),
                        "name": match_A.group(4).strip(),
                        "rank": int(match_A.group(5))
                    }

            if swimmer_data:
                current_event["swimmers"].append(
                    swimmer_data
                )

    return events


# ==========================================================
# SEEDING
# ==========================================================

def seed_event(event, lanes=8):

    swimmers = sorted(
        event["swimmers"],
        key=lambda x: x["rank"]
    )

    if not swimmers:
        return []

    num_swimmers = len(swimmers)

    num_heats = (
        num_swimmers + lanes - 1
    ) // lanes

    heats_swimmers = []

    remaining = swimmers[:]

    for h in range(num_heats, 0, -1):

        count = (
            lanes
            if h > 1
            else len(remaining)
        )

        heats_swimmers.append(
            remaining[:count]
        )

        remaining = remaining[count:]

    heats_swimmers.reverse()

    lane_order = [
        4, 5, 3, 6, 2, 7, 1, 8
    ]

    final_heats = []

    for i, heat in enumerate(heats_swimmers):

        heat.sort(
            key=lambda x: x["rank"]
        )

        assigned = {
            str(lane_order[j]): swimmer
            for j, swimmer
            in enumerate(heat)
        }

        final_heats.append({
            "heat_number": i + 1,
            "lanes": assigned
        })

    return final_heats


# ==========================================================
# HTML
# ==========================================================

def generate_html_compact(
        data,
        favorite_swimmers):

    html = """
    <html>
    <head>
    <style>

    body {
        font-family: Helvetica, Arial;
        font-size: 10pt;
    }

    table {
        width:100%;
        border-collapse:collapse;
        margin-bottom:8px;
    }

    td {
        padding:3px;
        border-bottom:1px solid #ddd;
    }

    .favorite {
        background:#ffffcc;
        font-weight:bold;
    }

    .event-header {
        font-weight:bold;
        margin-top:10px;
    }

    </style>
    </head>
    <body>

    <h2>Heat Sheet</h2>
    """

    for event in data:

        html += (
            f"<div class='event-header'>"
            f"#{event['number']} "
            f"{event['name']}</div>"
        )

        for heat in event["heats"]:

            html += (
                f"<h4>"
                f"Heat {heat['heat_number']}"
                f"</h4>"
            )

            html += "<table>"

            for lane in range(1, 9):

                swimmer = heat["lanes"].get(
                    str(lane)
                )

                if swimmer:

                    css = (
                        "favorite"
                        if swimmer["name"]
                        in favorite_swimmers
                        else ""
                    )

                    html += f"""
                    <tr class="{css}">
                        <td>{lane}</td>
                        <td>{swimmer["name"]}</td>
                        <td>{swimmer["age"]}</td>
                        <td>{swimmer["team"]}</td>
                        <td>{swimmer["seed_time"]}</td>
                    </tr>
                    """

            html += "</table>"

    html += "</body></html>"

    return html


# ==========================================================
# STREAMLIT UI
# ==========================================================

st.set_page_config(
    page_title="Heat Sheet Generator",
    layout="wide"
)

st.title("🏊 Swim Meet Heat Sheet Generator")

uploaded_file = st.file_uploader(
    "Upload Psych Sheet PDF",
    type=["pdf"]
)

if uploaded_file:

    with st.spinner(
        "Extracting PDF..."
    ):
        text = extract_text_from_pdf(
            uploaded_file
        )

    events = parse_psych_sheet(text)

    st.success(
        f"Found {len(events)} events"
    )

    all_swimmers = sorted({
        swimmer["name"]
        for event in events
        for swimmer in event["swimmers"]
    })

    favorites = st.multiselect(
        "Favorite Swimmers",
        all_swimmers
    )

    with st.expander(
        "Parsed Events"
    ):
        st.json(events)

    heat_sheet = []

    for e in events:

        heat_sheet.append({
            "number": e["number"],
            "name": e["name"],
            "heats": seed_event(e)
        })

    html = generate_html_compact(
        heat_sheet,
        favorites
    )

    st.subheader(
        "Heat Sheet Preview"
    )

    st.components.v1.html(
        html,
        height=800,
        scrolling=True
    )

    st.download_button(
        "Download HTML",
        html,
        file_name="heat_sheet.html",
        mime="text/html"
    )

    pdf_bytes = HTML(
        string=html
    ).write_pdf()

    st.download_button(
        "Download PDF",
        pdf_bytes,
        file_name="heat_sheet.pdf",
        mime="application/pdf"
    )

    st.download_button(
        "Download JSON",
        json.dumps(
            heat_sheet,
            indent=2
        ),
        file_name="heat_sheet.json",
        mime="application/json"
    )