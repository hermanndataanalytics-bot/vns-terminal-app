import streamlit as st
from menu1 import upload_to_imgbb
import json
from google.oauth2 import service_account
from google.cloud import firestore
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

# Famakiana ny service account avy amin'ny Secrets
service_account_info = json.loads(st.secrets["GCP_SERVICE_ACCOUNT_JSON"])
credentials = service_account.Credentials.from_service_account_info(service_account_info)

try:
    service_account_info = json.loads(st.secrets["GCP_SERVICE_ACCOUNT_JSON"])
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    db = firestore.Client(credentials=credentials, project=service_account_info['project_id'])
except Exception as e:
    st.error(f"Olana amin'ny fampitohizana amin'ny Firebase: {e}")
# Izao vao mampifandray amin'ny Firestore
# db = firestore.Client(credentials=credentials)
