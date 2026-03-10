import streamlit as st
import streamlit.components.v1 as components

# 1. Wide layout
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

def show_full_page():
    st.markdown("""
        <style>
            /* 1. Mba hiseho ny bokotra sidebar (hamburger) */
            header {
                background-color: rgba(0,0,0,0) !important;
                z-index: 1000 !important;
            }

            /* 2. Esory ny padding rehetra */
            .block-container {
                padding: 0rem !important;
                max-width: 100% !important;
            }

            /* 3. Amboary ny iframe mba ho lava sy hita tsara */
            iframe {
                width: 100% !important;
                border: none !important;
                margin-top: -3.5rem; /* Akisaka kely ho ambony hanarona ny toerana banga */
            }
        </style>
    """, unsafe_allow_html=True)
 
    # URL-nao
    url = "https://ludicrous-signal-stream-pro.base44.app"

    # --- VATANY ---
    # Mila atao lava ny height (ohatra: 2500) mba ho hita daholo ny votoatiny
    # Ny scrolling=True dia miteraka scrollbar eo amin'ny sisiny
    components.iframe(url, height=2500)
	
def main():
    show_full_page()