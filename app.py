import streamlit as st
from parser import parse_psych_sheet
from seeding import build_heat_sheet
from pdf_export import generate_pdf
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

    pdf_bytes = generate_pdf("Meet Heat Sheet", heat_sheet, set(favorites))

    st.download_button(
        "Download PDF",
        pdf_bytes,
        file_name="heat_sheet.pdf"
    )
