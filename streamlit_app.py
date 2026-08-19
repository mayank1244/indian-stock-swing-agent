import os
import streamlit as st

# Page Config: Dark Theme & Wide Layout
st.set_page_config(
    page_title="SwingPulse 🇮🇳 | Indian Equity Swing Trading Agent",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject custom CSS to remove standard Streamlit padding for full-screen original view
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100% !important;
    }
    iframe {
        border: none !important;
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

standalone_path = os.path.join(os.path.dirname(__file__), "web", "standalone.html")

if os.path.exists(standalone_path):
    with open(standalone_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    st.components.v1.html(html_content, height=1400, scrolling=True)
else:
    st.error("⚠️ Original standalone application (`web/standalone.html`) not found.")
