import streamlit as st
import pypdf

from parser import parse_psych_sheet
from seeding import build_heat_sheet
from export_pdf import generate_pdf
from export_html import generate_html_preview
from utils import extract_meet_title, is_long_event


st.set_page_config(layout="wide")
st.title("🏊 Heat Sheet Generator")

uploaded = st.file_uploader("Upload PDF", type=["pdf"])

heat_order = st.selectbox("Heat Order", ["fast_to_slow", "slow_to_fast"])
heat_size = st.number_input("Heat Size", 4, 10, 8)

if uploaded:

    text = "\n".join(
        p.extract_text() or "" for p in pypdf.PdfReader(uploaded).pages
    )

    meet_title = extract_meet_title(text)

    events = parse_psych_sheet(text)

    all_names = sorted({s["name"] for e in events for s in e["swimmers"]})
    favorites = st.multiselect("Favorites", all_names)

    from utils import is_long_event as is_long_event_func
    heat_sheet = build_heat_sheet(
        events,
        heat_size,
        heat_order,
        is_long_event_func
    )

    st.success("Generated!")

    html = generate_html_preview(meet_title, heat_sheet, set(favorites))
    # pdf = generate_pdf(meet_title, heat_sheet, set(favorites))

    st.components.v1.html(html, height=600, scrolling=True)

    st.download_button("Download HTML", html)
    # st.download_button("Download PDF", pdf, file_name="heat.pdf")
