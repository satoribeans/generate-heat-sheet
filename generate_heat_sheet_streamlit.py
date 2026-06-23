import streamlit as st
import pypdf
import base64

from export_html import generate_html_preview
from export_pdf import generate_pdf, generate_favorite_pdf
from models import Meet, MeetSettings
from parser import parse_psych_sheet
from seeding import build_heat_sheet
from utils import extract_meet_title


@st.cache_data
def build_favorite_pdf(meet_id, favorite_entries):
    return generate_favorite_pdf(meet_id, favorite_entries)


def show_pdf_preview(pdf_bytes):
    b64 = base64.b64encode(pdf_bytes).decode("utf-8")
    pdf_display = f"""
    <iframe
        src="data:application/pdf;base64,{b64}"
        width="100%"
        height="800px"
        type="application/pdf">
    </iframe>
    """
    st.components.v1.html(pdf_display, height=800)

def reset_meet_state():
    keys_to_clear = [
        "meet",
        "meet_title",
        "all_names",
        "favorites",
        "html",
        "pdf",
    ]

    for k in keys_to_clear:
        if k in st.session_state:
            del st.session_state[k]

    # clear cached functions (important)
    build_favorite_pdf.clear()

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

    # Detect new file upload and reset state
    if uploaded:
        file_id = uploaded.name + str(uploaded.size)
    
        if st.session_state.get("last_file_id") != file_id:
            reset_meet_state()
            st.session_state["last_file_id"] = file_id

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
    st.session_state["favorite_entries"] = favorite_entries

    show_pdf_preview(pdf)
    
# -------------------------
# ALWAYS RENDER OUTPUT (KEY FIX)
# -------------------------

if "html" in st.session_state:
    
    meet = st.session_state.get("meet")
    favorite_entries = st.session_state.get("favorite_entries", {})

    st.download_button(
        "Download HTML",
        st.session_state["html"],
        key="download_html"
    )

    st.download_button(
        "Download Meet Heat Sheet PDF",
        st.session_state["pdf"],
        file_name=f"{meet.name}_heatsheet.pdf",
        key="download_pdf"
    )

    if favorite_entries and len(favorite_entries) > 0:
        pdf_bytes = generate_favorite_pdf(meet, favorite_entries)

        st.download_button(
            "📄 Download Favorite Swimmers Heat Sheet PDF",
            data=pdf_bytes,
            file_name=f"{meet.name}_favorites.pdf",
            mime="application/pdf"
        )

    st.components.v1.html(
        st.session_state["html"],
        height=800,
        scrolling=True
    )
