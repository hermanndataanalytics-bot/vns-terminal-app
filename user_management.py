# user_management.py
import streamlit as st
import time
from datetime import datetime
from firebase_admin import firestore

# ---------- UTILS ----------
def ts_to_date(ts):
    if not ts:
        return "—"
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")

def get_db():
    # Firestore client rehefa ilaina ihany
    return firestore.client()

# ---------- MAIN ----------
def show_admin_section():
    st.subheader("👥 User Management (Enterprise / Firestore)")

    db = get_db()  # 👈 eto ihany no alaina

    users = db.collection("users").stream()

    for u in users:
        data = u.to_dict()
        uid = u.id

        expiry = data.get("expiry")
        active = expiry and expiry > time.time()

        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 2, 2])

            with c1:
                st.markdown(f"👤 `{uid}`")
                st.caption(f"📅 Expiry: {ts_to_date(expiry)}")

            with c2:
                st.write(f"📦 Plan: {data.get('plan', 'free')}")
                st.write("🟢 Active" if active else "🔴 Expired")

            with c3:
                if st.button("❌ Revoke", key=f"revoke_{uid}"):
                    db.collection("users").document(uid).update({
                        "plan": "free",
                        "expiry": None
                    })
                    st.success("Access revoked")
                    st.rerun()
