# =========================================================
# VNS TERMINATOR PRO – CLEAN ARCHITECTURE VERSION
# =========================================================
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import time
import datetime
import base64
import requests
import qrcode
from io import BytesIO
import streamlit.components.v1 as components
import uuid
import os
import sys
import si_dashboard 
import Forex_dashboard
import crypto_intelligence_dashboard
import base44_url
import streamlit.components.v1 as components
from datetime import datetime
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import random
import string
from dotenv import load_dotenv
import secrets
import re
from st_supabase_connection import SupabaseConnection

def generate_invoice(user_email, plan_name, price):
    pdf = FPDF()
    pdf.add_page()

    # Titre
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="OFFICIAL INVOICE - YOUR APP NAME", ln=True, align="C")

    # Detail
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Bill To: {user_email}", ln=True)
    pdf.cell(200, 10, txt=f"Plan: {plan_name}", ln=True)
    pdf.cell(200, 10, txt=f"Amount Paid: ${price}", ln=True)
    pdf.cell(200, 10, txt=f"Status: PAID", ln=True)
    pdf.cell(200, 10, txt=f"Date: {time.strftime('%Y-%m-%d')}", ln=True)

    # Footer
    pdf.ln(20)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(
        200,
        10,
        txt="Thank you for choosing our AI Trading Intelligence.",
        ln=True,
        align="C",
    )

    filename = f"invoice_{user_email}.pdf"
    pdf.output(filename)
    return filename
# Raha nampiasa st-supabase-connection ianao
conn = st.connection("supabase", type=SupabaseConnection)	

def apply_ultra_premium_ui(status_text="SYSTEM ONLINE"):

    # Loko arakaraka ny status
    if status_text.upper() == "SYSTEM ONLINE":
        led_color = "#22c55e"
        accent_color = "#00f0ff"
        text_glow = "rgba(0, 240, 255, 0.4)"
        status_bg = "rgba(34,197,94,0.15)"
        status_border = "rgba(34,197,94,0.3)"
    else:
        led_color = "#ef4444"
        accent_color = "#ff4b4b"
        text_glow = "rgba(255, 75, 75, 0.4)"
        status_bg = "rgba(239,68,68,0.15)"
        status_border = "rgba(239,68,68,0.3)"

    html_code = f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=JetBrains+Mono:wght@400;700&display=swap');

        .ultra-hero {{
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.6) 0%, rgba(30, 41, 59, 0.4) 100%);
            backdrop-filter: blur(12px);
            padding: 40px;
            border-radius: 28px;
            border: 1px solid rgba(255,255,255,0.08);
            display: grid;
            grid-template-columns: 1.2fr 0.8fr; /* Manitatra ny ankavanana ho 80% an'ny ankavia */
            gap: 30px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }}

        /* Glow EFFECT amin'ny zorony */
        .ultra-hero::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle, rgba(0, 240, 255, 0.05) 0%, transparent 70%);
            z-index: 0;
        }}

        .ultra-left {{
            position: relative;
            z-index: 1;
        }}

        .ultra-title {{
            font-size: clamp(32px, 5vw, 64px);
            font-weight: 900;
            line-height: 1;
            letter-spacing: -2px;
            color: #ffffff;
            margin: 15px 0;
        }}

        .ultra-title .highlight {{
            background: linear-gradient(90deg, #ff4b4b, #facc15, #22c55e);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-size: 200% auto;
            animation: glowGradient 4s linear infinite;
        }}

        @keyframes glowGradient {{
            0% {{ background-position: 0% center; }}
            100% {{ background-position: 200% center; }}
        }}

        /* TERMINAL STYLE (ANKAVANANA) */
        .ultra-right {{
            position: relative;
            z-index: 1;
            background: rgba(0, 0, 0, 0.6);
            border: 1px solid rgba(0, 240, 255, 0.2);
            border-radius: 16px;
            padding: 25px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
            line-height: 1.8;
            color: {accent_color};
            box-shadow: inset 0 0 20px rgba(0, 240, 255, 0.05);
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        .terminal-line {{
            display: flex;
            gap: 10px;
            text-shadow: 0 0 10px {text_glow};
        }}

        .cursor {{
            display: inline-block;
            width: 8px;
            height: 15px;
            background: {accent_color};
            animation: blink 1s infinite;
            vertical-align: middle;
        }}

        @keyframes blink {{
            50% {{ opacity: 0; }}
        }}

        .ultra-status {{
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 8px 20px;
            border-radius: 50px;
            background: {status_bg};
            border: 1px solid {status_border};
            color: #ffffff;
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 25px;
        }}

        .led-dot {{
            width: 8px;
            height: 8px;
            background: {led_color};
            border-radius: 50%;
            box-shadow: 0 0 10px {led_color};
        }}
        </style>

        <div class="ultra-hero">
            <div class="ultra-left">
                <div style="font-size: 12px; letter-spacing: 4px; color: #facc15; font-weight: 700; text-transform: uppercase; opacity: 0.8;">
                    Institutional Risk-Control Signals
                </div>
                <div class="ultra-title">
                    Vortex Neural Signals<br>TERMINA<span class="highlight">TOR</span>
                </div>
                <div style="color: #94a3b8; font-size: 18px; margin-bottom: 20px; font-weight: 400;">
                    Autonomous Smart Money Intelligence.
                </div>
                <div class="ultra-status">
                    <div class="led-dot"></div>
                    {status_text} · CORE AI SYNCHRONIZED
                </div>
            </div>

            <div class="ultra-right">
                <div class="terminal-line"><span>&gt;</span> <span>Initializing Neural Liquidity Grid...</span></div>
                <div class="terminal-line"><span>&gt;</span> <span>Order Flow Scanner: <b style="color:#fff">ACTIVE</b></span></div>
                <div class="terminal-line"><span>&gt;</span> <span>AI Confidence: <b style="color:#22c55e">92.18%</b></span></div>
                <div class="terminal-line"><span>&gt;</span> <span>Latency: <b style="color:#facc15">9ms</b></span></div>
                <div class="terminal-line"><span>&gt;</span> <span class="cursor"></span></div>
            </div>
        </div>
        """
    components.html(html_code, height=350)


# =========================================================
# 1. PAGE CONFIG & THEME
# =========================================================
st.set_page_config(page_title="VNS TERMINATOR PRO", layout="wide")


def apply_custom_css():
    # 1. Jereo raha efa tafiditra (logged_in) ny mpampiasa
    is_logged_in = st.session_state.get("logged_in", False)

    st.markdown(
        f"""
    <style>
   
    /* Signal Card (mangarahara kely mba ho hita ny sary ao aoriana raha ao amin'ny login) */
    .signal-card {{
        background: rgba(30, 35, 41, 0.85);
        backdrop-filter: blur(8px);
        border-radius: 12px; 
        padding: 20px;
        border-left: 6px solid #f0b90b; 
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }}

    /* Price Card */
    .price-card {{
        background: linear-gradient(135deg, rgba(30, 35, 41, 0.9) 0%, rgba(20, 23, 31, 0.9) 100%);
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid #f0b90b;
        text-align: center; 
        margin-bottom: 20px;
    }}

    /* Ny bokotra (Buttons) */
    .stButton>button {{
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        background-color: #f0b90b;
        color: black;
        border: none;
        transition: 0.3s;
    }}
    
    .stButton>button:hover {{
        background-color: #d8a60a;
        box-shadow: 0 0 10px #f0b90b;
    }}

    /* Contrast fix ho an'ny soratra */
    p, span, label, h1, h2, h3 {{
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 1);
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )


# Antsoy ny fonction (mila antsoina isaky ny rerun ny Streamlit)
apply_custom_css()

# =========================================================
# 2. FIREBASE INITIALIZATION
# =========================================================
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred)

db = firestore.client()


# =========================================================
# 3. DATABASE FUNCTIONS
# =========================================================
@st.cache_data(ttl=300)
def fetch_signals(market_type):
    col = "forex_signals" if market_type == "Forex" else "crypto_signals"
    docs = (
        db.collection(col)
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(10)
        .get()
    )
    return [doc.to_dict() for doc in docs]


def get_user_data(email):
    uid = email.replace(".", "_")
    doc = db.collection("users").document(uid).get()
    return doc.to_dict() if doc.exists else None


def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


def set_png_as_page_bg(bin_file):
    bin_str = get_base64_of_bin_file(bin_file)
    page_bg_img = f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)


# =========================================================
# 1. CONFIG & INITIALIZATION
# =========================================================
# Ity dia tokony ho any amin'ny fiantombohan'ny script-nao foana
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_data" not in st.session_state:
    st.session_state.user_data = {"email": "user@example.com", "plan": "Free Access"}

# --- INITIALIZE SESSION STATE FOR PAYMENT ---
if "selected_tier" not in st.session_state:
    st.session_state.selected_tier = "Basic Access"
if "selected_duration" not in st.session_state:
    st.session_state.selected_duration = "Monthly"
if "last_invoice_id" not in st.session_state:
    st.session_state.last_invoice_id = None


def send_email_with_invoice(receiver_email, plan_name, invoice_path):
    sender_email = st.secrets["SENDER_EMAIL"]
    sender_password = st.secrets["SENDER_PASSWORD"]
    smtp_server = st.secrets["SMTP_SERVER"]
    smtp_port = st.secrets["SMTP_PORT"]

    msg = MIMEMultipart()
    msg["From"] = f"VNS Terminator Sales <{sender_email}>"
    msg["To"] = receiver_email
    msg["Subject"] = f"✅ Access Activated: {plan_name} - VNS TERMINATOR"

    body = f"""
    Dear Customer,
    
    Your payment has been successfully verified by our team. 
    Your access to the {plan_name} is now ACTIVE.
    
    Please find your official invoice attached below.
    
    Best regards,
    The VNS Terminator Team
    """
    msg.attach(MIMEText(body, "plain"))

    # Fametahana ny PDF (Invoice)
    try:
        with open(invoice_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition", f"attachment; filename= {invoice_path}"
            )
            msg.attach(part)
    except Exception as e:
        print(f"Error attaching PDF: {e}")

    # Fandefasana amin'ny alalan'ny SMTP SSL
    try:
        # Mampiasa SMTP_SSL ho an'ny port 465 (azo antoka kokoa)
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Professional Mail Error: {e}")
        return False


payment_url = st.secrets["PAYMENT_URL"]


def verify_payment(txid):
    """Maka porofo fandoavana amin'ny backend"""
    try:
        response = requests.get(f"{payment_url}/verify?txid={txid}")
        if response.status_code == 200:
            data = response.json()
            return data.get("status") == "paid"
        else:
            return False
    except Exception as e:
        st.error(f"Error verifying payment: {e}")
        return False


def admin_panel():
    # --- 1. CONFIGURATION & CONNECTION ---
    try:
        # Ampiasao ny SERVICE_ROLE_KEY ao amin'ny secrets ho an'ny Admin
        conn = st.connection("supabase", type=SupabaseConnection)
    except Exception as e:
        st.error(f"Error connecting to Supabase: {e}")
        return
        
    # --- 2. ADMIN CHECK ---
    user_email_session = st.session_state.get("user_email", "")
    is_admin = user_email_session == "hermannhe18@gmail.com"

    if not is_admin:
        st.warning("Tsy manana alalana ianao hijery ity pejy ity.")
        return

    st.title("👨‍💻 Admin Command Center")
    t1, t2, t3 = st.tabs(["💳 Pending Payments", "📡 Signal Control", "👥 User List"])

    # --- TAB 1: PENDING PAYMENTS ---
    with t1:
        st.subheader("📊 Dashboard & Fankatoavana")
        try:
            # 1. Alaina ny data rehetra (na approved na pending)
            res_all = conn.table("payment_proofs").select("*").execute()
            all_data = res_all.data
            
            # 2. Configuration ny vidin'ny plan tsirairay
            prices_map = {
                "Basic Access": 19,
                "Pro Access": 49,
                "Elite Access": 99,
                "Premium Elite": 149,
            }
            
            # 3. FIKAJIANA REVENU
            # Isaina ny isan'ny nandoa sy ny vola miditra (Approved ihany)
            approved_list = [row for row in all_data if row['status'] == 'approved']
            total_rev = sum(prices_map.get(row['plan'], 0) for row in approved_list)
            
            # Isaina ny pending
            pending_pends = [row for row in all_data if row['status'] == 'pending']
            pending_count = len(pending_pends)

            # 4. MAMPISEHO METRICS
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Revenue", f"${total_rev:,}")
            c2.metric("Pending Tasks", f"{pending_count}")
            c3.metric("Total Users Paid", f"{len(approved_list)}")

            # --- REVENUE BREAKDOWN (Antsipiriany isaky ny tolotra) ---
            with st.expander("🔍 Jereo ny Revenue isaky ny Plan"):
                rev_cols = st.columns(len(prices_map))
                for i, (plan_name, price) in enumerate(prices_map.items()):
                    plan_count = len([r for r in approved_list if r['plan'] == plan_name])
                    plan_revenue = plan_count * price
                    rev_cols[i].metric(plan_name, f"${plan_revenue}", f"{plan_count} users")

            st.divider()

            # 5. LISITRY NY PENDING (NY AMBONY TEO ALOHA)
            if not pending_pends:
                st.info("Tsy misy fandoavam-bola miandry amin'izao.")
            else:
                for pay in pending_pends:
                    row_id = pay.get("id")
                    u_email = pay.get("email") or pay.get("user_uid")

                    with st.container(border=True):
                        col1, col2, col3 = st.columns([2, 2, 1])
                        with col1:
                            st.markdown(f"👤 **User:** `{u_email}`")
                            st.markdown(f"💎 **Plan:** `{pay.get('plan')}`")
                            st.markdown(f"🔗 **TXID:** `{pay.get('txid')}`")
                            st.caption(f"📅 Date: {pay.get('created_at', '-')}")

                        with col2:
                            url = pay.get("image_url")
                            if url:
                                st.image(url, use_container_width=True)
                            else:
                                st.warning("No image URL")

                        with col3:
                            # APPROVE
                            if st.button("Approve ✅", key=f"app_{row_id}", use_container_width=True):
                                # UPDATE SUPABASE
                                conn.table("payment_proofs").update({"status": "approved"}).eq("id", row_id).execute()
                                
                                # Eto ianao no mampiditra ny generate_invoice raha ilaina
                                st.success("Nekena!")
                                time.sleep(1)
                                st.rerun()

                            # REJECT
                            if st.button("Reject ❌", key=f"rej_{row_id}", use_container_width=True):
                                conn.table("payment_proofs").update({"status": "rejected"}).eq("id", row_id).execute()
                                st.warning("Nolavina!")
                                time.sleep(1)
                                st.rerun()
        except Exception as e:
            st.error(f"Error in Tab 1: {e}")

    # --- TAB 2: SEND SIGNAL (OVANA HO SUPABASE) ---
    with t2:
        st.subheader("Andefasana Signal Vaovao")
        with st.form("admin_sig_form", clear_on_submit=True):
            m = st.selectbox("Market", ["Forex", "Crypto"])
            pa = st.text_input("Pair (ohatra: EURUSD)")
            ty = st.selectbox("Type", ["BUY", "SELL"])
            en = st.text_input("Entry Price")
            tp = st.text_input("Take Profit (TP)")
            sl = st.text_input("Stop Loss (SL)")
            submitted = st.form_submit_button("🚀 SEND SIGNAL")

        if submitted:
            if pa and en:
                table_name = "forex_signals" if m == "Forex" else "crypto_signals"
                signal_data = {
                    "pair": pa.upper(),
                    "type": ty,
                    "entry": en,
                    "tp": tp if tp else "TBD",
                    "sl": sl if sl else "TBD",
                    "tf": "H1"
                }
                # Ampiasao ny conn.table fa aza mampiasa db.collection
                conn.table(table_name).insert(signal_data).execute()
                st.success("Signal voatahiry ao amin'ny Supabase! ✅")
            else:
                st.error("Fenoy ny Pair sy ny Entry azafady.")

    # --- TAB 3: USER MANAGEMENT (GOOGLE SHEETS) ---
    with t3:
        st.header("📝 Editable Database")
        try:
            import gspread
            from google.oauth2.service_account import Credentials

            scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            
            if "gcp_service_account" not in st.secrets:
                st.error("Credential 'gcp_service_account' missing in secrets.")
            else:
                creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
                client = gspread.authorize(creds)
                spreadsheet = client.open("Drafitra Vns")
                sheet = spreadsheet.worksheet("users")
                
                df = pd.DataFrame(sheet.get_all_records())
                edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic", key="editor_v1")

                if st.button("Tehirizo ny fiovana 💾"):
                    data_to_save = [edited_df.columns.values.tolist()] + edited_df.values.tolist()
                    sheet.update(values=data_to_save, range_name="A1")
                    st.success("Tafiditra ny fanovana!")
                    time.sleep(1)
                    st.rerun()
        except Exception as e:
            st.error(f"Google Sheets Error: {e}")

def main_app():

    # 1. Alao ny sanda avy amin'ny session_state
    # Raha mbola tsy misy ao dia omeo sanda default (ohatra: "dashboard")
    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"

    current_page = st.session_state.current_page  # Eto vao voafaritra ny variable local

    # 2. Ny sisa amin'ny setup (user_plan, sns.)
    user_plan = st.session_state.get("user_plan", "Free Access")

    # Ampiasaina ny .lower() mba tsy hisy olana na sora-baventy na sora-madinika
    # Ary ampidirina ao anaty lisitra ny "pro" (sora-madinika)
    plan_lowercase = user_plan.lower()
    has_pro_access = any(p in plan_lowercase for p in ["elite", "premium", "pro"])

    # 4. ANTSOINA NY SIDEBAR (Tsy maintsy milahatra amin'ny setup eo ambony)
    render_sidebar()

    # 5. NOTIFICATIONS (Mba hanamarinana raha mandeha)
    if has_pro_access:
        st.success(f"🌟 Access Level: {user_plan}")
    else:
        st.info(f"💡 Access Level: {user_plan}")

    # --- 4. ROUTING LOGIC (PAGE SELECTION) ---

    # 1. Alao ny email sy ny plan avy ao amin'ny session_state (ETO NY FIX)
    user_email = st.session_state.get("user_email", "")
    user_plan_raw = str(st.session_state.get("user_plan", "Free")).lower().strip()

    # 2. Vao manao ny fisavana ny pejy ianao
    if current_page == "Admin Panel":
        # Eto izao dia efa fantatry ny programa ny 'user_email'
        if user_email == "hermannhe18@gmail.com":
            admin_panel()
        else:
            st.error("⛔ Access Denied.")

    # --- BASIC ANALYTICS DASHBOARD ---
    elif current_page == "basic_dashboard":
        si_dashboard.main()

    # --- FANOVANA ETO: Avela hiditra ny "basic" ---
    elif current_page == "pro_dashboard" or current_page == "forex_dashboard":
        # Jereo raha misy "basic", "pro", "elite", sns.
        allowed_pro = ["basic", "pro", "elite", "premium", "vip"]
        if any(keyword in user_plan_raw for keyword in allowed_pro):
            # IZAO: Na basic aza izy dia misokatra ny Forex Dashboard
            Forex_dashboard.main()
        else:
            st.warning("🔒 This section requires at least a Basic/Pro Access.")

    elif current_page == "elite_dashboard":
        # Ny Elite kosa dia mbola mihidy ho an'ny Basic
        if any(keyword in user_plan_raw for keyword in ["elite", "premium", "vip"]):
            crypto_intelligence_dashboard.main()
        else:
            st.warning("🔒 This section requires Elite Access.")

    elif current_page == "vip_dashboard":
        if any(keyword in user_plan_raw for keyword in ["premium", "vip"]):
            base44_url.main()
        else:
            st.error("🔒 Access Restricted to VIP Members.")

# Raha nampiasa st-supabase-connection ianao
conn = st.connection("supabase", type=SupabaseConnection)

def render_sidebar():
    # --- 1. PREMIUM CUSTOM CSS ---
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {
                background-color: #05070a;
                border-right: 1px solid #1e293b;
            }
            .nav-card {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 15px;
                margin-bottom: 20px;
            }
            .notify-badge {
                display: inline-block;
                width: 8px;
                height: 8px;
                background-color: #f43f5e;
                border-radius: 50%;
                margin-right: 5px;
                box-shadow: 0 0 10px #f43f5e;
                animation: pulse 1.5s infinite;
            }
            @keyframes pulse {
                0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(244, 63, 94, 0.7); }
                70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(244, 63, 94, 0); }
                100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(244, 63, 94, 0); }
            }
        </style>
    """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        # --- 2. LOGO SECTION ---
        st.markdown(
            """
            <div style='text-align: center; padding-bottom: 20px;'>
                <h1 style='color: white; font-size: 26px; margin: 0;'>🚀 VNS <span style='color: #3b82f6;'>TERMINATOR</span></h1>
                <p style='color: #64748b; font-size: 10px; text-transform: uppercase; letter-spacing: 2px;'>Neural Intelligence Hub</p>
            </div>
        """,
            unsafe_allow_html=True,
        )

        st.divider()

        # --- 3. VARIABLE DEFINITIONS (ATAO ETO AMBONY FOANA IRETO) ---
        user_email = st.session_state.get("user_email", "Guest")
        user_plan_raw = st.session_state.get("user_plan", "Free")

        # ETO NO NAMARITANA AZY (Fix for NameError)
        user_plan_clean = str(user_plan_raw).lower().strip()
        user_plan = str(user_plan_raw).title()

        has_new_update = True

        # Famaritana ny vidiny
        prices = {"Basic": "19", "Pro": "49", "Elite": "99", "Premium": "149"}
        current_price = prices.get(user_plan, "19")

        # Invoice ID Logic
        if "last_invoice_id" not in st.session_state:
            date_str = time.strftime("%y%m%d")
            random_str = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=4)
            )
            st.session_state.last_invoice_id = f"VNS-{date_str}-{random_str}"

        invoice_id = st.session_state.last_invoice_id

        # --- 4. DISPLAY PROFILE CARD ---
        st.markdown(
            f"""
            <div class="nav-card">
                <div style='font-size: 11px; color: #64748b; text-transform: uppercase;'>Operator ID</div>
                <div style='font-weight: bold; color: white; margin-bottom: 10px;'>{user_email}</div>
                <div style='display: flex; align-items: center; justify-content: space-between;'>
                    <span style='background: #3b82f622; color: #3b82f6; padding: 2px 10px; border-radius: 20px; font-size: 11px; border: 1px solid #3b82f655;'>
                        🛡️ {user_plan.upper()}
                    </span>
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )

        # --- 5. COMMAND CENTER (NAVIGATION) ---
        st.markdown(
            "<p style='font-size: 11px; font-weight: bold; color: #64748b; margin: 15px 0 10px 5px;'>CORE COMMANDS</p>",
            unsafe_allow_html=True,
        )

        # Bokotra Analytics Dashboard (Hita foana)
        unique_key = f"btn_analytics_{st.session_state.get('user_plan', 'guest')}_{datetime.now().strftime('%M%S')}"
        if st.sidebar.button(
            "📄 ANALYTICS DASHBOARD", use_container_width=True, key=unique_key
        ):
            st.session_state.current_page = "basic_dashboard"
            st.rerun()

        # Famaritana ny Access Levels
        access_levels = {
            "PRO DASHBOARD": ["basic", "pro", "elite", "premium", "vip"],
            "ELITE DASHBOARD": ["elite", "premium", "vip"],
            "VIP DASHBOARD": ["premium", "vip"],
        }

        for label, allowed in access_levels.items():
            icon = "⚡" if "PRO" in label else "🧠" if "ELITE" in label else "≡"
            is_allowed = any(p in user_plan_clean for p in allowed)

            if is_allowed:
                if st.button(f"{icon} {label}", use_container_width=True):
                    # FIX ETO: Raha PRO DASHBOARD no tsindriny dia alefa any amin'ny forex_dashboard izy
                    if label == "PRO DASHBOARD":
                        st.session_state.current_page = "forex_dashboard"
                    else:
                        st.session_state.current_page = label.lower().replace(" ", "_")
                    st.rerun()
            else:
                st.markdown(
                    f"<div style='padding: 10px; color: #475569; font-size: 13px; opacity: 0.6;'>🔒 {label}</div>",
                    unsafe_allow_html=True,
                )

        # --- 6. DYNAMIC PREMIUM INVOICE DISPLAY (Nohavaozina ho an'ny PRO & ELITE) ---
        current_page = st.session_state.get("current_page", "basic_dashboard").lower()

        # 1. FARITANA NY TARGER (Izay planina tiana ho tratrana manaraka)
        # Raha PRO izy, ny ELITE no target. Raha ELITE, ny VIP no target.
        if "free" in user_plan_clean:
            target_price, target_label = "19", "BASIC ACCESS"
            show_invoice = True
        elif "basic" in user_plan_clean:
            target_price, target_label = "49", "PRO UPGRADE"
            show_invoice = True  # Asehoy foana ny card ho an'ny Basic
        elif "pro" in user_plan_clean:
            target_price, target_label = "99", "ELITE UPGRADE"
            show_invoice = True  # Eto no fanitsiana: Miseho ny Card ho an'ny PRO
        elif "elite" in user_plan_clean:
            target_price, target_label = "149", "VIP UPGRADE"
            show_invoice = True  # Miseho ny Card ho an'ny ELITE
        else:
            show_invoice = False  # VIP na hafa

        # 2. RENDERING NY INVOICE CARD
        if show_invoice:
            st.markdown(
                f"""
            <div style="background: linear-gradient(145deg, #0a0a0a, #151515); padding: 20px; border-radius: 18px; border: 1px solid #facc15; box-shadow: 0px 4px 25px rgba(250, 204, 21, 0.2); text-align: center; margin-bottom: 15px;">
                <div style="color:#facc15; font-size: 32px; font-weight: 800; letter-spacing: -1px;">{target_price} USDT</div>
                <div style="color:#94a3b8; font-size: 12px; margin-top: 2px; text-transform: uppercase; font-weight: bold;">{target_label}</div>
                <div style="color: #10b981; font-size: 10px; margin-top: 8px; font-weight: bold;">🔐 SECURE BLOCKCHAIN</div>
                <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.05); margin: 15px 0;">
                <div style="display: flex; justify-content: space-between; padding: 0 10px;">
                    <span style="color:#475569; font-size: 9px;">ID: {invoice_id}</span>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            # 3. NY BOKOTRA PROCEED (Ity no nanjavona teo)
            st.link_button(
                f"PROCEED TO {target_label} 🚀",
                "https://pay.vn-s-terminator.com/",
                use_container_width=True,
            )

        # --- ADMIN & LOGOUT ---
        if user_email == "hermannhe18@gmail.com":
            if st.button("⚙️ SYSTEM ADMIN", use_container_width=True, type="primary"):
                st.session_state.current_page = "Admin Panel"
                st.rerun()

        if st.button(
            "🚪 TERMINATE SESSION", use_container_width=True, type="secondary"
        ):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.logged_in = False
            st.rerun()


def auth_page(db=None):
    # --- 1. UI & BACKGROUND ---
    try:
        bin_str = get_base64_of_bin_file("vns_robot_hero.jpg")
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.4)), 
                                  url("data:image/png;base64,{bin_str}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            [data-testid="stForm"] {{
                background: rgba(15, 23, 42, 0.1) !important;
                padding: 40px !important;
                border-radius: 25px !important;
                border: 1px solid rgba(0, 240, 255, 0.15) !important;
                backdrop-filter: blur(15px);
                box-shadow: 0 20px 50px rgba(0,0,0,0.6);
            }}
            </style>
        """,
            unsafe_allow_html=True,
        )
    except Exception:
        st.markdown(
            "<style>.stApp {background-color: #0e1117;}</style>", unsafe_allow_html=True
        )

    apply_ultra_premium_ui("SYSTEM ONLINE")

    # --- 2. INITIALIZATION ---
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    # Fonctions utilitaires
    def get_password_strength(password):
        if not password:
            return "", ""
        score = 0
        if len(password) >= 8:
            score += 1
        if re.search(r"[a-z]", password) and re.search(r"[A-Z]", password):
            score += 1
        if re.search(r"\d", password):
            score += 1
        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            score += 1
        if len(password) < 6 or score < 2:
            return "🔴 Weak", "low"
        elif score == 3:
            return "🟡 Strong", "medium"
        else:
            return "🟢 Very Strong", "high"

    def generate_secure_password(length=12):
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return "".join(secrets.choice(alphabet) for i in range(length))

    # --- 3. LOGIC REGISTER ---
    if st.session_state.auth_mode == "register":
        with st.form("vns_reg_form"):
            st.markdown(
                "<h2 style='text-align:center; color:white;'>📝 REGISTRATION</h2>",
                unsafe_allow_html=True,
            )
            new_email = st.text_input("Email (Operator ID)")

            col_pass, col_gen = st.columns([3, 1])
            with col_pass:
                new_password = st.text_input("Set Password", type="password")
            with col_gen:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("🔄 Gen"):
                    st.code(generate_secure_password())
                    st.toast("Password generated!")

            strength_text, level = get_password_strength(new_password)
            if new_password:
                st.markdown(f"**Security Level:** {strength_text}")

            confirm_p = st.text_input("Confirm Password", type="password")
            accept_terms = st.checkbox("I agree to the VNS Terminator Terms of Service")
            reg_submitted = st.form_submit_button(
                "CREATE OPERATOR ID", use_container_width=True
            )

        if reg_submitted:
            if not accept_terms:
                st.error("❌ Accept terms first.")
            elif level == "low":
                st.error("❌ Password too weak.")
            elif new_password != confirm_p:
                st.error("❌ Passwords do not match.")
            elif new_email and new_password:
                uid = new_email.replace(".", "_")
                try:
                    if db.collection("users").document(uid).get().exists:
                        st.error("🚫 Already registered.")
                    else:
                        db.collection("users").document(uid).set(
                            {
                                "uid": uid,
                                "email": new_email,
                                "password": new_password,
                                "plan": "Free",
                                "created_at": firestore.SERVER_TIMESTAMP,
                            }
                        )
                        st.success("✅ Created! Please login.")
                        st.session_state.auth_mode = "login"
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

        if st.button("Back to Login"):
            st.session_state.auth_mode = "login"
            st.rerun()

    # --- 4. LOGIC LOGIN (Ito no mampipoitra ny Formulaire Login) ---
    elif st.session_state.auth_mode == "login":
        with st.form("vns_login_form"):
            st.markdown(
                "<h2 style='text-align:center; color:white;'>🔒 SYSTEM ACCESS</h2>",
                unsafe_allow_html=True,
            )
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            login_submitted = st.form_submit_button(
                "ACCESS TERMINAL", use_container_width=True
            )

        if login_submitted:
            if email and password:
                uid = email.replace(".", "_")
                user_doc = db.collection("users").document(uid).get()

                if user_doc.exists:
                    data = user_doc.to_dict()

                    if password == data.get("password"):
                        st.session_state.logged_in = True
                        st.session_state.user_email = email
                        st.session_state.user_plan = data.get("plan", "Free Access")
                        st.session_state.current_page = "basic_dashboard"

                        st.success("✅ Access Granted!")
                        st.rerun()

                    else:
                        st.error("❌ Wrong password.")
        if st.button("New Operator? Create Account"):
            st.session_state.auth_mode = "register"
            st.rerun()


# =========================================================
# GLOBAL EXECUTION CONTROL
# =========================================================


def run_app():
    # 1. Jereo raha efa tafiditra ny mpampiasa
    if not st.session_state.get("logged_in", False):
        auth_page(db)  # pejy login
    else:
        main_app()  # app principale


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    run_app()
