import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(
    layout="wide",
    page_title="SalesSense",
    page_icon="📞",
    menu_items={
        'Get Help': 'mailto:support@example.com',
        'Report a bug': 'mailto:support@example.com',
        'About': "# Cogent Infotech Innovation Lab"
    }
)

# --- INITIALIZE SESSION STATE ---
# Initialize all session state variables at app startup to prevent data loss
if "upload_ready" not in st.session_state:
    st.session_state.upload_ready = False
if "audio_file_data" not in st.session_state:
    st.session_state.audio_file_data = None
if "participants_data" not in st.session_state:
    st.session_state.participants_data = ""
if "details_data" not in st.session_state:
    st.session_state.details_data = ""
if "call_types_data" not in st.session_state:
    st.session_state.call_types_data = []
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None

# --- PAGE SETUP ---
home_page = st.Page(
    page="views/home.py",
    title="Home",
    icon=":material/home:",
    default=True
)

upload_page = st.Page(
    page="views/upload.py",
    title="Data Ingestion",
    icon=":material/upload:",
)

results_page = st.Page(
    page="views/results.py",
    title="Results",
    icon=":material/insights:",
)

about_us_page = st.Page(
    page="views/about_us.py",
    title="About Us",
    icon=":material/info:",
)

# --- NAVIGATION SETUP ---
navigation = st.navigation(
    pages={
        "SalesSense": [home_page, upload_page, results_page],
        "Info": [about_us_page]
    },
)

# --- SHARED ON ALL PAGES ---
st.logo(
    image="assets/images/cogent_tagline_color.png",
    icon_image="assets/images/cogent_logo.png"
)

# Custom CSS (optional placeholder)
st.markdown("", unsafe_allow_html=True)

# --- RUN NAVIGATION ---
navigation.run()
