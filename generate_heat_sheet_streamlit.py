import streamlit as st
import pypdf

from parser import parse_psych_sheet
from seeding import build_heat_sheet
from pdf_export import generate_pdf
from html_export import generate_html_preview
from utils import is_long_event, extract_meet_title
from models import Event, Heat, Swimmer

st.set_page_config(
    page_title="Heat Sheet Generator",
    layout="wide"
)

st.title("🏊 Swim Meet Heat Sheet Generator")

heat_order = st.selectbox(
    "Heat Order",
    ["fast_to_slow", "slow_to_fast"]
)

heat_size = st.number_input(
    "Heat Size",
    min_value=4,
    max_value=10,
    value=8
)

uploaded = st.file_uploader(
    "Upload Psych Sheet PDF",
    type=["pdf"]
)

if uploaded:

    # -----------------------------
    # Extract PDF text
    # -----------------------------
    reader = pypdf.PdfReader(uploaded)

    text = "\n".join(
        page.extract_text() or ""
        for page in reader.pages
    )

    # -----------------------------
    # Meet title
    # -----------------------------
    meet_title = extract_meet_title(text)

    # -----------------------------
    # Parse events
    # -----------------------------
    events = parse_psych_sheet(text)

    if not events:
        st.error("No events found in PDF.")
        st.stop()

    # -----------------------------
    # Favorites picker
    # -----------------------------
    all_names = sorted({
        s["name"]
        for e in events
        for s in e["swimmers"]
    })

    favorites = st.multiselect(
        "Favorite Swimmers",
        all_names
    )

    # -----------------------------
    # Build heat sheet
    # -----------------------------
    heat_sheet = build_heat_sheet(
        events,
        heat_size,
        heat_order,
        is_long_event
    )

    st.success(
        f"Generated {len(heat_sheet)} events"
    )

    # -----------------------------
    # HTML Preview
    # -----------------------------
    html_content = generate_html_preview(
        meet_title,
        heat_sheet,
        set(favorites)
    )

    with st.expander("👁 Preview Heat Sheet", expanded=True):
        st.components.v1.html(
            html_content,
            height=800,
            scrolling=True
        )

    # -----------------------------
    # PDF
    # -----------------------------
    pdf_bytes = generate_pdf(
        meet_title,
        heat_sheet,
        set(favorites)
    )

    # -----------------------------
    # Downloads
    # -----------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "⬇ Download HTML",
            html_content,
            file_name="heat_sheet.html",
            mime="text/html"
        )

    with col2:
        st.download_button(
            "⬇ Download PDF",
            pdf_bytes,
            file_name="heat_sheet.pdf",
            mime="application/pdf"
        )
