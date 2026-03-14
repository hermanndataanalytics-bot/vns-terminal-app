import google.generativeai as genai
import streamlit as st

genai.configure(api_key=st.secrets["FOREX_GENAI_KEY"])

st.write("### Modely azonao ampiasaina izao:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        st.code(m.name)