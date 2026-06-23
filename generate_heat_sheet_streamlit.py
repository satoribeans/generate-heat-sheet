import streamlit as st
import pypdf

from export_html import generate_html_preview
from export_pdf import generate_pdf, generate_favorite_pdf
from models import Meet, MeetSettings
from parser import parse_psych_sheet
from seeding import build_heat_sheet
from utils import extract_meet_title


st.set_page_config(layout="wide")
st.title("🏊 Heat Sheet Generator")

# --------------------------------------------------
#  Always Show Meet Settings
# --------------------------------------------------
st.sidebar.header("Meet Settings")
lanes = st.sidebar.selectbox(
    "Lanes per Heat",
    options=[8, 10],
    index=0
)

# disable for now
# circle_seed_top_n_heats = st.sidebar.number_input(
#     "Circle Seed Top N Heats",
#     min_value=1,
#     max_value=10,
#     value=1,
#     step=1
# )

distance_event_order = st.sidebar.selectbox(
    "Long Distance Event Heat Order",
    options=["Fast to Slow", "Slow to Fast"],
    index=0
)

distance_event_order = {
    "Fast to Slow": "fast_to_slow",
    "Slow to Fast": "slow_to_fast"
}[distance_event_order]

st.sidebar.caption(
    "Only used for long-distance events. "
    "All other events use standard seeding."
)

col1, col2 = st.columns([1, 4])
with col1:
    st.markdown("**Upload PDF**")
    st.caption("Upload your psych sheet")   # optional subtitle

with col2:
    uploaded = st.file_uploader("", type=["pdf"], label_visibility="collapsed")

if "all_names" not in st.session_state:
    st.session_state["all_names"] = []

if "favorites" not in st.session_state:
    st.session_state["favorites"] = []

if uploaded and "meet" not in st.session_state:
    text = "\n".join(
        p.extract_text() or "" for p in pypdf.PdfReader(uploaded).pages
    )

    meet_title = extract_meet_title(text)
    events = parse_psych_sheet(text)

    meet = Meet(
        name=meet_title,
        events=events,
    )
    st.session_state["meet"] = meet
    st.session_state["meet_title"] = meet_title
    st.session_state["all_names"] = sorted(
        {e.swimmer.name for e in meet.all_entries()}
    )

# Always visible
col1, col2 = st.columns([1, 4])
with col1:
    st.markdown("**Favorites**")
    st.caption("Select favorite swimmers")

with col2:
    favorites = st.multiselect(
        "", st.session_state["all_names"],
        default=st.session_state.get("favorites", []))
st.session_state["favorites"] = favorites

generate = st.button("Generate Heat Sheet")

# -------------------------
# GENERATE ONLY ON CLICK
# -------------------------
if generate and "meet" in st.session_state:

    meet = st.session_state["meet"]
    meet_title = st.session_state["meet_title"]

    # getting the current meet settings
    settings = MeetSettings(
        lanes=lanes,
        circle_seed_top_n_heats=1, # default to 1
        distance_event_order=distance_event_order
    )
    meet.settings = settings

    # Generate heat sheet and update session state
    meet = build_heat_sheet(meet)
    st.session_state["meet"] = meet

    favorites = set(st.session_state.get("favorites", []))
    favorite_entries = meet.favorite_entries(favorites)

    html = generate_html_preview(meet, favorites)
    pdf = generate_pdf(meet, favorite_entries)

    st.session_state["html"] = html
    st.session_state["pdf"] = pdf

# -------------------------
# ALWAYS RENDER OUTPUT (KEY FIX)
# -------------------------

if "html" in st.session_state:

    st.download_button(
        "Download HTML",
        st.session_state["html"],
        key="download_html"
    )

    st.download_button(
        "Download Meet Heat Sheet PDF",
        st.session_state["pdf"],
        file_name="heat.pdf",
        key="download_pdf"
    )

     st.download_button(
        label="📄 Download Favorite Swimmers Heat Sheet PDF",
        data=pdf_bytes,
        file_name=f"{meet.name}_favorites.pdf",
        mime="application/pdf"
     )

    st.components.v1.html(
        st.session_state["html"],
        height=800,
        scrolling=True
    )
