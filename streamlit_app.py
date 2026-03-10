import streamlit as st
from menu1 import upload_to_imgbb

# ============================
# ENDPOINT HANDLER
# ============================

query = st.query_params

if "upload_receipt" in query:

    uploaded_file = st.file_uploader("receipt")

    if uploaded_file:

        image_url = upload_to_imgbb(uploaded_file)

        st.json({
            "status": "success",
            "url": image_url
        })

    st.stop()
