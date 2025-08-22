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

# --- HOME PAGE CONTENT ---
st.title(":blue[:material/finance_mode: **SalesSense**]")

st.markdown("""
#### 🚀 Turn sales calls into coaching moments
SalesSense gives instant, AI-powered feedback on your Dialpad calls—highlighting what worked, what didn't, and what to do next.
""")

st.markdown("""
- Spot strengths and blind spots fast
- See sentiment, talk-time, objections, and next steps
- Get actionable, call-specific coaching
""")

st.caption("Built on real team calls for relevance. Designed for speed. Perfect for POCs.")

col1, col2, col3 = st.columns([3, 2, 3])
with col2:
    if st.button(
        label="🚀 Proceed",
        type="primary",
        help="Click to upload your data and get started!",
        use_container_width=True
    ):
        st.success("Proceeding to Data Ingestion...")
        st.switch_page("views/upload.py")
