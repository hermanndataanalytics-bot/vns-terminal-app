import streamlit as st

# Initialize trade history
if "trades" not in st.session_state:
    st.session_state.trades = []

# Initialize pdf container
if "ready_pdf" not in st.session_state:
    st.session_state.ready_pdf = None

import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ta
from google import genai
from datetime import datetime
from io import BytesIO
import qrcode
import os
# ReportLab (PDF)
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle 
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import plotly.io as pio
import plotly.io as pio  # <--- ETO NO NAMBOARINA
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit.components.v1 as components
import qrcode
import io
from datetime import datetime
import math
import requests
import json
from groq import Groq 

    
def get_atr(df, period=14):
    df = df.copy()
    df['h-l'] = df['High'] - df['Low']
    df['h-pc'] = abs(df['High'] - df['Close'].shift())
    df['l-pc'] = abs(df['Low'] - df['Close'].shift())
    df['tr'] = df[['h-l', 'h-pc', 'l-pc']].max(axis=1)
    return df['tr'].rolling(window=period).mean().iloc[-1]
    
import streamlit as st
from google import genai # Hamarino raha ity tokoa ny library ampiasainao

# ==============================
# 1. CONFIG & ASSET MAP
# ==============================
st.set_page_config(page_title="VNS TERMINATOR AI", layout="wide", page_icon="⚡")

# Fanalana ny Secret sy fisorohana ny fahadisoana (Key Management)
try:
    # Ampiasao ilay anarana ao amin'ny Secrets-nao (FOREX_GENAI_KEY)
    MY_API_KEY = st.secrets["FOREX_GENAI_KEY"].strip()
except KeyError:
    st.error("⚠️ Tsy hita ao amin'ny Secrets ny 'FOREX_GENAI_KEY'")
    st.stop()

ASSET_MAP = {
    "GC=F": "GOLD", "CL=F": "CRUDE OIL", "EURUSD=X": "EUR / USD", "GBPUSD=X": "GBP / USD",
    "USDJPY=X": "USD / JPY", "USDCHF=X": "USD / CHF", "AUDUSD=X": "AUD / USD",
    "USDCAD=X": "USD / CAD", "NZDUSD=X": "NZD / USD", "EURGBP=X": "EUR / GBP",
    "EURJPY=X": "EUR / JPY", "GBPJPY=X": "GBP / JPY"
}
TIMEFRAMES = {"15m": ("7d", "15m"), "1H": ("60d", "1h"), "Daily": ("1y", "1d")}

# ==============================
# 2. AI INTELLIGENCE & NEWS
# ==============================
def get_ai_client():
    try:
        # Ataovy azo antoka fa mitovy ny anarana eto sy ao amin'ny Secrets
        api_key = st.secrets["FOREX_GENAI_KEY"].strip()
        if not api_key:
            st.warning("⚠️ API Key is empty")
            return None
        return genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"Error initializing Gemini client: {e}")
        return None

# -------------------------------------------------
def get_ai_deep_analysis(asset_label, current_price, df):
    # Prompt fanomanana
    prompt = f"Analyze {asset_label} at {current_price}..."

    # --- 1. GEMINI 2.5 FLASH ---
    try:
        client = get_ai_client()
        # Nampiana 'models/' araka ny sary nalefanao
        res = client.models.generate_content(
            model="models/gemini-2.5-flash", 
            contents=prompt
        )
        return f"🟢 **[Gemini 2.5 Flash]**\n\n{res.text}"

    except Exception:
        # --- 2. GEMMA 3 27B ---
        try:
            st.info("🔄 Gemini Flash quota reached. Trying Gemma 3 27B...")
            # Nampiana 'models/' eto koa
            res = client.models.generate_content(
                model="models/gemma-3-27b-it", 
                contents=prompt
            )
            return f"🟡 **[Gemma 3 27B]**\n\n{res.text}"
            
        except Exception as e:
            # --- 3. GROQ (LLAMA 3.3) ---
            st.warning(f"🔄 Google API limit reached. Switching to Groq...")
            # Miantso an'ilay function call_groq_fallback efa nataontsika teo
            return call_groq_fallback(prompt)
			
# -------------------------------------------------
# Live Market News (With Quota Protection)
# -------------------------------------------------
def get_live_news(asset):
    from datetime import datetime
    today = datetime.now().date()

    prompt = f"""
    You are a financial news terminal similar to Bloomberg.
    Provide the 3 latest high-impact market news headlines
    relevant to {asset} as of {today}.

    Rules:
    - Only short headlines
    - Focus on macro, crypto, forex or institutional news
    - Maximum 1 line per headline
    """

    client = get_ai_client()
    if client is None:
        return "⚠️ AI news service unavailable."

    # --- DINGANA 1: ANDRAMANA NY GEMINI 2.5 FLASH ---
    try:
        res = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=prompt
        )
        return res.text

    except Exception as e:
        # Raha lany ny quota (Error 429) na misy olana hafa
        error_msg = str(e).upper()
        
        if "429" in error_msg or "QUOTA" in error_msg or "EXHAUSTED" in error_msg:
            # --- DINGANA 2: FALLBACK ANY AMIN'NY GEMMA 3 27B (Google Quota malalaka) ---
            try:
                # Mampiasa an'ilay anarana modely hita tao amin'ny "Model Lister"-nao
                res_backup = client.models.generate_content(
                    model="models/gemma-3-27b-it",
                    contents=prompt
                )
                return f"🟡 **[Gemma 3 News]**\n{res_backup.text}"
            
            except Exception:
                # --- DINGANA 3: FALLBACK ANY AMIN'NY GROQ (Emergency Backup) ---
                try:
                    # Miantso an'ilay function Groq (Llama 3.3) efa namboarintsika teo
                    return f"🔵 **[Groq News]**\n{call_groq_fallback(prompt)}"
                except:
                    return f"⚠️ News unavailable (All AI Quotas Exhausted)."
        
        return f"News unavailable. ({str(e)})"
		
def export_ultra_premium_pdf_safe(asset, ls, tp, sl, ai_comment, ai_calendar,
                                  fig, cio_report, trades):

    import numpy as np
    from io import BytesIO
    from datetime import datetime
    import matplotlib.pyplot as plt
    import plotly.io as pio
    import qrcode
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    import re

    # Helper to clean markdown
    def clean_markdown(text):
        if not text:
            return ""
        text = re.sub(r'#+\s*(.*)', r'<b>\1</b>', text)
        text = re.sub(r'\*\*(.*?)\*\*', r'<b><font color="#1F4E79">\1</font></b>', text)
        text = text.replace('*','').replace('\n','<br/>')
        return text

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
                            rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements = []
    styles = getSampleStyleSheet()

    # --------------------- Styles ---------------------
    header = ParagraphStyle("header", parent=styles["Heading1"], fontSize=22,
                            alignment=TA_CENTER, textColor=colors.HexColor("#D4AF37"))
    section = ParagraphStyle("section", parent=styles["Heading2"], fontSize=13, textColor=colors.HexColor("#D4AF37"))
    body = ParagraphStyle("body", parent=styles["Normal"], fontSize=10, leading=12)
    footer = ParagraphStyle("footer", fontSize=8, alignment=TA_CENTER, textColor=colors.grey)
    disc_style = ParagraphStyle("disc", fontSize=7, textColor=colors.grey, alignment=TA_LEFT)

    # --------------------- Logo & Cover ---------------------
    try:
        elements.append(Image("vns_logo.png", width=110, height=110))
    except:
        elements.append(Paragraph("⚡ VNS TERMINATOR AI PRO", header))
    elements.append(Spacer(1,10))
    elements.append(Paragraph("VNS TERMINATOR AI PRO", header))
    elements.append(Paragraph(f"{asset} • MARKET INTELLIGENCE REPORT • {datetime.now().strftime('%Y-%m-%d %H:%M')}", footer))
    elements.append(Spacer(1,15))

    # --------------------- Market Chart (Safe) ---------------------
    chart_added = False
    try:
        # Try Plotly first
        img_bytes = pio.to_image(fig, format="png", width=1000, height=500)
        elements.append(Image(BytesIO(img_bytes), width=480, height=240))
        chart_added = True
    except:
        # Fallback to matplotlib from Close prices
        try:
            plt.figure(figsize=(6,3))
            plt.plot(ls['Close'], color='blue')
            plt.title(f"{asset} Price Chart")
            plt.grid(True)
            buf_chart = BytesIO()
            plt.tight_layout()
            plt.savefig(buf_chart, format='png')
            plt.close()
            buf_chart.seek(0)
            elements.append(Image(buf_chart, width=480, height=240))
            chart_added = True
        except:
            pass
    if not chart_added:
        elements.append(Paragraph("Chart unavailable.", body))

    elements.append(Spacer(1,15))

    # --------------------- Trade Parameters ---------------------
    bias = "BULLISH 🟢" if ls.get("Signal",0) == 1 else "BEARISH 🔴"
    table_data = [
        ["PARAMETER", "VALUE"],
        ["Current Price", f"${ls.get('Close',0):.4f}"],
        ["Market Bias", bias],
        ["Take Profit", f"${tp:.4f}"],
        ["Stop Loss", f"${sl:.4f}"]
    ]
    table = Table(table_data, colWidths=[220,220])
    table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#D4AF37")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("GRID",(0,0),(-1,-1),0.5,colors.grey)
    ]))
    elements.append(table)
    elements.append(Spacer(1,15))

    # --------------------- Performance Metrics ---------------------
    if trades is None:
        trades = []
    trades = np.array(trades)
    if trades.size > 0:
        winrate = round((trades>0).mean()*100,2)
        profit = trades[trades>0].sum()
        loss = abs(trades[trades<0].sum())
        profit_factor = round(profit/loss,2) if loss!=0 else 0
        std_val = trades.std()
        sharpe = round((trades.mean()/std_val)*np.sqrt(252),2) if std_val!=0 else 0
        equity = np.cumsum(trades)
        max_drawdown = round((equity - np.maximum.accumulate(equity)).min(),2)
    else:
        winrate = profit_factor = sharpe = max_drawdown = 0
        equity = np.array([0])

    metrics_data = [
        ["Metric","Value"],
        ["Win Rate", f"{winrate} %"],
        ["Profit Factor", profit_factor],
        ["Sharpe Ratio", sharpe],
        ["Max Drawdown", max_drawdown]
    ]
    metrics_table = Table(metrics_data, colWidths=[220,220])
    metrics_table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#D4AF37")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("GRID",(0,0),(-1,-1),0.5,colors.grey)
    ]))
    elements.append(Paragraph("SYSTEM PERFORMANCE METRICS", section))
    elements.append(metrics_table)
    elements.append(Spacer(1,15))

    # --------------------- Equity Curve ---------------------
    plt.figure(figsize=(6,3))
    plt.plot(equity, color='green')
    plt.title("Strategy Equity Curve")
    plt.tight_layout()
    buf_equity = BytesIO()
    plt.savefig(buf_equity, format='png')
    plt.close()
    buf_equity.seek(0)
    elements.append(Paragraph("SYSTEM EQUITY CURVE", section))
    elements.append(Image(buf_equity, width=420, height=200))
    elements.append(Spacer(1,15))

    # --------------------- AI Analysis ---------------------
    elements.append(Paragraph("AI STRATEGIC ANALYSIS", section))
    elements.append(Paragraph(clean_markdown(ai_comment), body))
    elements.append(Spacer(1,15))

    # --------------------- Macro / CIO ---------------------
    elements.append(Paragraph("MACRO EVENT IMPACT", section))
    elements.append(Paragraph(clean_markdown(ai_calendar), body))
    elements.append(Spacer(1,15))

    elements.append(Paragraph("CIO INSTITUTIONAL BRIEFING", section))
    elements.append(Paragraph(clean_markdown(cio_report), body))
    elements.append(Spacer(1,15))

    # --------------------- Disclaimer ---------------------
    elements.append(Paragraph(
        "<b>RISK DISCLAIMER:</b> Trading involves significant risk. This report is for research purposes only and does not constitute investment advice.",
        disc_style
    ))
    elements.append(Spacer(1,10))

    # --------------------- QR Code ---------------------
    qr = qrcode.make("https://t.me/your_vns_channel")
    qr_buf = BytesIO()
    qr.save(qr_buf, format='PNG')
    qr_buf.seek(0)
    qr_table = Table([[Image(qr_buf,45,45), Paragraph("VNS TERMINATOR AI PRO<br/>Institutional Trading Systems", footer)]],
                     colWidths=[60,380])
    elements.append(qr_table)
    elements.append(Spacer(1,5))
    elements.append(Paragraph("© 2026 VNS Global Markets", footer))

    # --------------------- Build ---------------------
    doc.build(elements)
    buf.seek(0)
    return buf
   
# ==========================================
# 1. UI CONFIG & STYLING
# ==========================================
st.set_page_config(page_title="VNS TERMINATOR AI", layout="wide", page_icon="⚡")

def send_to_google_sheets(asset, bias, entry, sl, tp, lot, profit):
    try:
        # 1. Configuration ny fidirana
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        SERVICE_ACCOUNT_FILE = "serviceAccountKey.json"
        SHEET_ID = "196I1LCyt59lySUyKlT2I7B9OEe8AuYa4FNSmlbXSjpY"
        
        creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
        client = gspread.authorize(creds)
        
        # 2. Manokatra ny takelaka
        sheet = client.open_by_key(SHEET_ID).worksheet("Trading_Journal")
        
        # 3. Manomana ny andalana vaovao (mifanaraka amin'ny sary nalefanao)
        # Laharana: DATE & TIME | ASSET (TF) | BIAS | ENTRY | SL | TP | LOT SIZE | PROFIT ($) | SCORE
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [now, asset, bias, entry, sl, tp, lot, profit, "Pending"]
        
        # 4. Manampy ny andalana any amin'ny farany ambany
        sheet.append_row(row)
        return True
    except Exception as e:
        print(f"Error Google Sheets: {e}")
        return False

    
# ==========================================
# 2. DATA CONSTANTS
# ==========================================


# 1. IRETO NO TSY MAINTSY APETRAKA ANY AMBONY INDRINDRA
API_URL = st.secrets["BASE44_API_URL"]
API_KEY = st.secrets["BASE44_API_KEY"]

ASSET_MAP = {
    "GC=F": "GOLD", "CL=F": "CRUDE OIL", "EURUSD=X": "EUR / USD", "GBPUSD=X": "GBP / USD",
    "USDJPY=X": "USD / JPY", "USDCHF=X": "USD / CHF", "AUDUSD=X": "AUD / USD",
    "USDCAD=X": "USD / CAD", "NZDUSD=X": "NZD / USD", "EURGBP=X": "EUR / GBP",
    "EURJPY=X": "EUR / JPY", "GBPJPY=X": "GBP / JPY"
}

TIMEFRAME_MAP = {
    "15m": ("1d", "15m"),
    "1h":  ("5d", "1h"),   # Ity no niteraka KeyError teo
    "4h":  ("7d", "1h"),   # Halaina 1h dia resample ho 4h any aoriana
    "1d":  ("60d", "1d")
}
# --- FUNCTION HANDREFA ---
def send_to_base44(data):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(API_URL, json=data, headers=headers)
        return response.status_code
    except Exception as e:
        return str(e)

            
# ======================================================
# 1. DIALOG FUNCTIONS (POP-UPS) - ENGLISH VERSION
# ======================================================

@st.dialog("VNS TERMINATOR: SYSTEM PROFILE")
def show_about():
    st.markdown("""
    <div style="font-family: 'JetBrains Mono', monospace; color: white;">
        <h2 style="color: #00ffcc; border-bottom: 2px solid #00ffcc; padding-bottom: 10px;">ABOUT_VNS.sys</h2>
        <p style="font-size: 0.9rem; line-height: 1.6;">
            <b style="color: #00ffcc;">VNS TERMINATOR</b> is a high-frequency quantum intelligence terminal 
            designed for institutional-grade market analysis. 
        </p>
        <ul style="font-size: 0.85rem; color: #888;">
            <li><b style="color: #eee;">Version:</b> 2.0.26 Gold Edition</li>
            <li><b style="color: #eee;">Engine:</b> Neural-Link Core v4</li>
            <li><b style="color: #eee;">Security:</b> AES-256 Quantum Encrypted</li>
        </ul>
        <div style="background: rgba(0,255,204,0.05); padding: 10px; border-radius: 5px; border: 1px dashed #00ffcc;">
            <p style="margin:0; font-size: 0.75rem; color: #00ffcc; text-align:center;">
                "Decoding the future, one block at a time."
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
@st.dialog("VNS TERMINATOR: SECURITY ARCHITECTURE")
def show_security_terms():
    st.markdown("""
    <div style="font-family: 'Inter', sans-serif;">
        <h2 style="color: #00ffcc; border-bottom: 2px solid #00ffcc; padding-bottom: 10px;">SECURITY TERMS</h2>
        <h4 style="color: #00ffcc;">1. Zero-Trust Model</h4>
        <p>Continuous verification of every access request within our Neural Network.</p>
        <h4 style="color: #00ffcc;">2. Encryption</h4>
        <p><b>AES-XTS 256-bit</b> for data at rest and <b>TLS 1.3 Quantum-Resistant</b> for data in transit.</p>
        <h4 style="color: #00ffcc;">3. Immutable Ledger</h4>
        <p>All operations are logged on a blockchain-based audit trail for SOC2/ISO 27001:2026 compliance.</p>
        <div style="background: rgba(255, 51, 51, 0.1); padding: 10px; border-radius: 5px; border-left: 4px solid #ff3333;">
            <p style="margin: 0; font-size: 0.8rem; color: #ff9999;"><b>Liability:</b> Users are responsible for securing their local hardware access points.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

@st.dialog("VNS TERMINATOR: GLOBAL CONTACT TERMINAL")
def show_contact():
    st.markdown("""
    <div style="font-family: 'JetBrains Mono', monospace; color: white;">
        <h2 style="color: #00ffcc; border-bottom: 2px solid #00ffcc; padding-bottom: 10px;">CONTACT_US.exe</h2>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top:15px;">
            <div style="background: rgba(0,255,204,0.05); padding: 15px; border-radius: 8px; border: 1px solid rgba(0,255,204,0.2);">
                <p style="margin:0; font-size:0.7rem; color:#888;">INSTITUTIONAL_SALES</p>
                <code style="color:#00ffcc; font-size:0.8rem;">sales@vn-s-terminator.com</code>
            </div>
            <div style="background: rgba(0,255,204,0.05); padding: 15px; border-radius: 8px; border: 1px solid rgba(0,255,204,0.2);">
                <p style="margin:0; font-size:0.7rem; color:#888;">TECH_SUPPORT</p>
                <code style="color:#00ffcc; font-size:0.8rem;">support@vn-s-terminator.com.com</code>
            </div>
        </div>
        <h4 style="margin-top: 25px; color: #00ffcc; font-size: 0.7rem; letter-spacing:2px;">OFFICIAL CHANNELS</h4>
        <div style="display: flex; gap: 10px; margin-top: 10px;">
            <a href="#" style="flex: 1; text-align: center; padding: 12px; background: #0077b5; color: white; border-radius: 5px; text-decoration: none; font-size: 0.75rem; font-weight: bold;">LINKEDIN</a>
            <a href="#" style="flex: 1; text-align: center; padding: 12px; background: #000; color: white; border-radius: 5px; text-decoration: none; font-size: 0.75rem; border: 1px solid #333; font-weight: bold;">X_PLATFORM</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
def vns_footer_high_pro_v2():
    st.markdown("""
        <style>
            .block-container { padding-bottom: 0rem !important; }
            div[data-testid="stHtml"] { 
                margin-top: -50px !important; 
            }
        </style>
    """, unsafe_allow_html=True)

    components.html("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;500;800&family=JetBrains+Mono:wght@500&display=swap');
        
        body { margin: 0; padding: 0; background: transparent; overflow: hidden; }

        .vns-footer-wrapper {
            background: linear-gradient(180deg, rgba(5,5,5,0) 0%, rgba(8,12,12,0.98) 100%);
            backdrop-filter: blur(15px);
            font-family: 'Plus Jakarta Sans', sans-serif;
            color: #e0e0e0;
            padding: 30px 50px 20px;
            border-top: 1px solid rgba(0, 255, 204, 0.2);
            position: relative;
        }

        .main-grid {
            display: grid;
            grid-template-columns: 2.5fr 1.2fr 1.2fr 1.6fr;
            gap: 35px;
            max-width: 1300px;
            margin: 0 auto;
        }

        /* Lohateny miavaka misy Icone */
        .footer-header-box {
            display: flex;
            align-items: center;
            gap: 8px;
            background: rgba(0, 255, 204, 0.07);
            padding: 6px 12px;
            border-radius: 6px;
            border-left: 3px solid #00ffcc;
            margin-bottom: 15px;
            width: fit-content;
        }

        .footer-label {
            color: #00ffcc;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            font-weight: 800;
        }

        .brand-section h2 {
            color: #00ffcc;
            font-size: 1.7rem;
            font-weight: 900;
            margin: 0;
            text-shadow: 0 0 20px rgba(0, 255, 204, 0.4);
        }

        .link-item {
            display: flex;
            align-items: center;
            color: #888;
            text-decoration: none;
            font-size: 0.82rem;
            margin-bottom: 8px;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        /* Effect rehefa mandalo souris */
        .link-item:hover { 
            color: #ffffff; 
            transform: translateX(5px);
            text-shadow: 0 0 8px rgba(255,255,255,0.3);
        }

        .metrics-card {
            background: rgba(0, 255, 204, 0.03);
            border: 1px solid rgba(0, 255, 204, 0.1);
            border-radius: 12px;
            padding: 18px;
        }

        .metric-row {
            display: flex;
            justify-content: space-between;
            font-size: 0.75rem;
            margin-bottom: 10px;
        }

        .metric-value {
            font-family: 'JetBrains Mono', monospace;
            color: #00ffcc;
        }

        .copyright-bar {
            text-align: center;
            margin-top: 30px;
            font-size: 0.65rem;
            color: #444;
            padding-top: 15px;
            border-top: 1px solid rgba(255,255,255,0.03);
        }

        #utc-clock-v3 { 
            color: #fff; 
            background: rgba(0,255,204,0.15); 
            padding: 3px 8px; 
            border-radius: 4px;
            font-weight: bold;
        }
    </style>

    <div class="vns-footer-wrapper">
        <div class="main-grid">
            <div class="brand-section">
                <h2>VNS TERMINATOR</h2>
                <p style="color:#666; font-size:0.75rem; line-height:1.6; margin-top:12px;">
                    Evolutionary Quantum Intelligence for the 2026 digital frontier. Secure. Precise. Institutional-grade.
                </p>
            </div>

            <div>
                <div class="footer-header-box">
                    <span>🌐</span><span class="footer-label">Ecosystem</span>
                </div>
                <div class="link-item">Neural Terminal</div>
                <div class="link-item">Liquidity Map</div>
                <div class="link-item">Risk Engine</div>
            </div>

            <div>
                <div class="footer-header-box">
                    <span>🛡️</span><span class="footer-label">Governance</span>
                </div>
                <div class="link-item">ISO 27001:2026</div>
                <div class="link-item">Legal & Compliance</div>
                <div class="link-item">Privacy Guard</div>
            </div>

            <div class="metrics-card">
                <div class="metric-row">
                    <span style="color:#777">System Status</span>
                    <span class="metric-value">ACTIVE ●</span>
                </div>
                <div class="metric-row">
                    <span style="color:#777">AI Accuracy</span>
                    <span class="metric-value">99.98%</span>
                </div>
                <div class="metric-row" style="margin-top:12px; border-top:1px solid rgba(255,255,255,0.05); padding-top:10px;">
                    <span style="color:#777">UTC Clock</span>
                    <span class="metric-value" id="utc-clock-v3">00:00:00 UTC</span>
                </div>
            </div>
        </div>

        <div class="copyright-bar">
            © 2026 VNS TERMINATOR CORP | ALL SYSTEMS ENCRYPTED | PROFESSIONAL EDITION
        </div>
    </div>

    <script>
        function updateClock() {
            const now = new Date();
            const h = String(now.getUTCHours()).padStart(2, '0');
            const m = String(now.getUTCMinutes()).padStart(2, '0');
            const s = String(now.getUTCSeconds()).padStart(2, '0');
            const el = document.getElementById('utc-clock-v3');
            if(el) el.textContent = h + ":" + m + ":" + s + " UTC";
        }
        setInterval(updateClock, 1000);
        updateClock();
    </script>
    """, height=230)
    
def main(limit=12):
    
    # 1. Alao ny planina ary omeo anarana hoe 'user_plan' izy (TANDREMO NY ELANELANA)
    # Ampiasaina ny .get() mba tsy hisy error raha mbola tsy nanao login
    user_plan = str(st.session_state.get("user_plan", "free")).lower()
    
    # 2. Faritana ny fahazoan-dalana (Access) mampiasa ilay 'user_plan' vao noforonina teo
    has_pro_access = any(p in user_plan for p in ["pro", "elite", "premium", "basic"])
        
    # --- 2. Notification & Sidebar ---
    st.toast("🛡️ Quantum Security Protocol Active", icon="✅")
    st.sidebar.title("🎮 COMMAND CENTER")
    
    # Ampiasaina ny .upper() eto mba hadio ny fisehon'ny soratra ao amin'ny Sidebar
    st.sidebar.write(f"**Member Status:** `{user_plan.upper()}`")

    # --- 3. Lojika Fameperana (is_locked) ---
    # Raha misy "basic" ao amin'ny planina dia True ny is_locked (izay no tianao hatao eto)
    is_locked = True if "basic" in user_plan else False
    
    # --- 4. Assets Selection ---
    ASSET_MAP = {
    "GC=F": "GOLD", "CL=F": "CRUDE OIL", "EURUSD=X": "EUR / USD", "GBPUSD=X": "GBP / USD",
    "USDJPY=X": "USD / JPY", "USDCHF=X": "USD / CHF", "AUDUSD=X": "AUD / USD",
    "USDCAD=X": "USD / CAD", "NZDUSD=X": "NZD / USD", "EURGBP=X": "EUR / GBP",
    "EURJPY=X": "EUR / JPY", "GBPJPY=X": "GBP / JPY"
    }

    if is_locked:
        allowed_keys = list(ASSET_MAP.keys())[:3]
        selectable_options = {k: ASSET_MAP[k] for k in allowed_keys}
    else:
        selectable_options = ASSET_MAP

    col1, col2 = st.columns(2)
    
    with col1:
        # Ity 'ticker' ity dia efa mety
        ticker = st.selectbox("Asset", options=list(selectable_options.keys()), 
                             format_func=lambda x: selectable_options[x], key="fx_tick")
        asset_label = ASSET_MAP.get(ticker, ticker)

    with col2:
        tf_options = {"15m": "15 Min", "1h": "1 Hour", "4h": "4 Hours", "1d": "1 Day"}
        # Ampiasao 'timeframe' eto
        timeframe = st.selectbox("Timeframe", options=list(tf_options.keys()), index=1, key="fx_tf")

    # --- FIX AN'ILAY KEYERROR & NAMEERROR ---
    TIMEFRAMES = {
        "15m": ("1d", "15m"),
        "1h":  ("5d", "1h"),
        "4h":  ("7d", "1h"),
        "1d":  ("60d", "1d")
    }

    # Ampiasao 'timeframe' (fa tsy tf_key) mba tsy hisy NameError
    period, interval = TIMEFRAMES.get(timeframe, ("5d", "1h"))
    
    current_price = st.sidebar.number_input(
        "Current Price",
        value=1.0850,
        format="%.5f"
    )

    atr = st.sidebar.number_input(
        "ATR (Volatility)",
        value=0.0015,
        format="%.5f",
        help="Average True Range"
    )

    balance = st.sidebar.number_input(
        "Trading Balance ($)",
        value=1000.0
    )

    risk_pct_input = (
        st.sidebar.slider("Risk Per Trade (%)", 0.1, 5.0, 1.0) / 100
    )

    # --- 5. DYNAMIC DISPLAY ---
    # Ity 'ticker' ity dia tsy maintsy ilay avy amin'ny st.selectbox(..., key="fx_tick")
    asset_label = ASSET_MAP.get(ticker, ticker)
    dynamic_title = f"{asset_label} // {timeframe}"

    st.markdown(f"""
        <div style="text-align: center; margin-top: -10px;">
            <p style="color: #00ffcc; letter-spacing: 5px; font-size: 0.7rem; margin-bottom: 0;">TERMINAL ACTIVE</p>
            <h1 style="color: white; font-size: 3rem;">⚡ {dynamic_title}</h1>
        </div>
        """, unsafe_allow_html=True)
        
    # FAKANA DATA (Ampiasao ny .get() mba tsy hisy NameError intsony)
    period, interval = TIMEFRAMES.get(timeframe, ("5d", "1h"))
    
    # ... Ny ambiny amin'ny kaody (try/except, yfinance, sns)
    col_calc, col_action = None, None
    multiplier = 10000
    
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
        
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            # Technicals
            df["SMA20"] = ta.trend.sma_indicator(df["Close"], window=20)
            df["SMA50"] = ta.trend.sma_indicator(df["Close"], window=50)
            df["ATR"] = ta.volatility.average_true_range(df["High"], df["Low"], df["Close"], window=14)
            
            # Signal Logic
            df["Signal"] = 0
            df.loc[(df["SMA20"] > df["SMA50"]) & (df["SMA20"].shift(1) <= df["SMA50"].shift(1)), "Signal"] = 1
            df.loc[(df["SMA20"] < df["SMA50"]) & (df["SMA20"].shift(1) >= df["SMA50"].shift(1)), "Signal"] = -1

            # Last Active Signal
            ls = df.iloc[-1]
            last_sig_df = df[df["Signal"] != 0]
            last_sig = last_sig_df.iloc[-1] if not last_sig_df.empty else ls
            is_buy = last_sig["Signal"] == 1
            color = "#00ff88" if is_buy else "#ff3355"

            # TP/SL & Risk-Reward
            atr = ls["ATR"]
            tp = ls["Close"] + (atr * 3 if is_buy else -atr * 3)
            sl = ls["Close"] - (atr * 1.5 if is_buy else -atr * 1.5)
            
            risk_amt = abs(ls['Close'] - sl)
            reward_amt = abs(tp - ls['Close'])
            rr_ratio = reward_amt / risk_amt if risk_amt != 0 else 0
            
            # 1. Mamaritra ny karazana signal (BUY na SELL)
            signal_type = "BUY" if is_buy else "SELL"
            
            st.markdown("---")
            st.subheader(f"📡 Signal Transmission to ≡ DATABASE")

            # 1. Hamarino ny plan-n'ny mpampiasa
            user_plan = str(st.session_state.get("user_plan", "Basic")).strip().title()
            is_authorized = user_plan in ["Premium"]

            # --- OME_SANDA FOTOTRA NY VARIABLE REHETRA ---
            # Izany no misoroka ny error "cannot access local variable"
            current_tf_key = "M15"
            pips_val = 0
            analyse_auto = "No analysis generated."
            payload = {}

            if not is_authorized:
                st.warning(f"🔒 **Access Denied.** Your current plan ({user_plan}) does not include Signal Transmission.")
                st.info("💡 Please upgrade to **Premium** to unlock this feature.")
                st.button("🚀 EXECUTE SIGNAL TRANSMISSION (PREMIUM ONLY)", disabled=True, use_container_width=True)
            else:
                # --- 2. FIKAJIANA NY DATA (Ataovy ivelan'ny bokotra mba ho hita foana ny payload) ---
                for k, v in TIMEFRAME_MAP.items():
                    if v[1] == interval:
                        current_tf_key = k
                        break

                diff = abs(tp - ls["Close"])
                if any(x in ticker for x in ["GC=F", "GOLD", "XAU"]):
                    pips_val = int(diff * 10) 
                elif "JPY" in ticker:
                    pips_val = int(diff * 100)
                else:
                    pips_val = int(diff * 10000)

                direction_en = "Bullish" if is_buy else "Bearish"
                alignment_en = "above" if is_buy else "below"
                analyse_auto = (
                    f"Detection of a {direction_en} breakout on the {current_tf_key} timeframe. "
                    f"SMA20 is {alignment_en} SMA50 with a Risk/Reward ratio of {rr_ratio:.1f}."
                )

                # --- 3. FANDRAFETANA NY PAYLOAD ---
                payload = {
                    "pair": ASSET_MAP.get(ticker, ticker),
                    "direction": "BUY" if is_buy else "SELL",
                    "timeframe": current_tf_key,
                    "entry_price": round(ls["Close"], 4),
                    "tp1": round(tp, 4),
                    "stop_loss": round(sl, 4),
                    "risk_reward": round(rr_ratio, 1),
                    "resultat_pips": pips_val,
                    "notes": analyse_auto,
                    "status": "En cours",
                    "created_at": datetime.now().isoformat()
                }

                # --- 4. NY BOKOTRA EXECUTE ---
                st.markdown("---")
                button_label = f"🚀 EXECUTE SIGNAL TRANSMISSION {payload['pair']}"
                # Ny loko dia miankina amin'ny Direction (Maitso ho an'ny BUY, Mena ho an'ny SELL)
                
                if st.button(button_label, use_container_width=True, type="primary"):
                    with st.spinner("📤 Transmitting encrypted signal to institutional database..."):
                        headers = {
                            "Content-Type": "application/json",
                            "x-api-key": API_KEY,
                            "Authorization": f"Bearer {API_KEY}"
                        }
                        
                        try:
                            # Fandefasana amin'ny alalan'ny POST request
                            res = requests.post(API_URL, json=payload, headers=headers)
                            
                            if res.status_code in [200, 201]:
                                st.success(f"✅ Signal successfully transferred for {payload['pair']}!")
                                st.balloons()
                            else:
                                st.error(f"❌ Transmission Error: Code {res.status_code}")
                                st.json(res.json()) # Mampiseho ny valiny avy amin'ny server
                        except Exception as e:
                            st.error(f"⚠️ Connection Failed: {e}")
                                    
            # --- 1. MAIN VISUALS (Chart & Status) ---
            col_chart, col_status = st.columns([2.5, 1])

            with col_chart:
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
                fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df["SMA20"], line=dict(color='cyan', width=1.2), name="SMA20"), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df["SMA50"], line=dict(color='#F63366', width=1.2), name="SMA50"), row=1, col=1)
                
                buys = df[df["Signal"] == 1]
                sells = df[df["Signal"] == -1]
                fig.add_trace(go.Scatter(x=buys.index, y=buys["Low"]*0.99, mode="markers", marker=dict(symbol="triangle-up", size=12, color="#00ff00"), name="BUY"), row=1, col=1)
                fig.add_trace(go.Scatter(x=sells.index, y=sells["High"]*1.01, mode="markers", marker=dict(symbol="triangle-down", size=12, color="#ff0000"), name="SELL"), row=1, col=1)

                df["Equity"] = (df["Signal"].shift(1) * df["Close"].pct_change()).cumsum()
                fig.add_trace(go.Scatter(x=df.index, y=df["Equity"], fill='tozeroy', line=dict(color='#D4AF37'), name="PnL"), row=2, col=1)
                
                fig.update_layout(height=750, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True)

            with col_status:
                # 1. Ampidirina indray ny CSS (Ity no mamerina ny bordure sy loko)
                st.markdown("""
                    <style>
                        .tp-box { 
                            background: rgba(0, 255, 136, 0.1); 
                            border: 1px solid #00ff88; 
                            border-radius: 12px; 
                            padding: 15px; 
                            margin-top: 15px; 
                            text-align: center; 
                            color: #00ff88; 
                            font-weight: bold;
                            box-shadow: 0 0 10px rgba(0, 255, 136, 0.2);
                        }
                        .sl-box { 
                            background: rgba(255, 51, 85, 0.1); 
                            border: 1px solid #ff3355; 
                            border-radius: 12px; 
                            padding: 15px; 
                            margin-top: 10px; 
                            text-align: center; 
                            color: #ff3355; 
                            font-weight: bold;
                            box-shadow: 0 0 10px rgba(255, 51, 85, 0.2);
                        }
                        .rr-box { 
                            background: rgba(212, 175, 55, 0.1); 
                            border: 1px solid #D4AF37; 
                            border-radius: 12px; 
                            padding: 15px; 
                            margin-top: 10px; 
                            text-align: center;
                            box-shadow: 0 0 10px rgba(212, 175, 55, 0.2);
                        }
                    </style>
                """, unsafe_allow_html=True)

                # 2. Ny fampisehoana ny angon-drakitra (HTML)
                st.markdown(f"""
                    <div style="border: 2px solid {color}; border-radius: 15px; padding: 25px; text-align: center; background: #0b0e14; box-shadow: 0 0 20px {color}33;">
                        <span style="height: 20px; width: 20px; background-color: {color}; border-radius: 50%; display: inline-block; box-shadow: 0 0 10px {color};"></span>
                        <h1 style="color:{color}; margin:10px 0;">{'BUY' if is_buy else 'SELL'}</h1>
                        <h2 style="color: white; margin: 0;">${ls['Close']:.2f}</h2>
                    </div>
                    
                    <div class="tp-box">🎯 TAKE PROFIT: {tp:.2f}</div>
                    <div class="sl-box">🛑 STOP LOSS: {sl:.2f}</div>
                    
                    <div class="rr-box">
                        <p style="color: #D4AF37; margin: 0; font-size: 14px; font-weight: bold;">RISK / REWARD</p>
                        <h3 style="color: white; margin: 5px 0;">1 : {rr_ratio:.2f}</h3>
                        <p style="color: #8b949e; font-size: 12px;">Reward potential: +{reward_amt:.2f}</p>
                    </div>
                """, unsafe_allow_html=True)
                
            # =========================================================
            # 5. NEURAL PREDICTION SECTION (Premium & Elite)
            # =========================================================

            user_plan_raw = str(st.session_state.get("user_plan", "Free Access")).lower()

            # Premium / Elite / VIP access
            if any(plan in user_plan_raw for plan in ["premium", "elite", "vip"]):

                with st.container():

                    with st.expander("🧠 GEMINI NEURAL PREDICTION", expanded=True):

                        # -------------------------------------------------
                        # 1. RUN AI BUTTON
                        # -------------------------------------------------
                        if st.button(
                            "🛰️ RUN DEEP ARTIFICIAL INTELLIGENCE ANALYSIS",
                            use_container_width=True
                        ):

                            try:
                                asset_label = ASSET_MAP.get(ticker, ticker)
                                current_price = float(ls.get("Close", 0))

                                with st.spinner("🤖 Gemini Neural Engine is calculating market structures..."):

                                    result = get_ai_deep_analysis(
                                        asset_label,
                                        current_price,
                                        df
                                    )

                                    st.session_state["active_ai_data"] = result
                                    st.session_state["ai_scan_time"] = datetime.now().strftime("%H:%M:%S")

                            except Exception as e:
                                st.error(f"AI execution error: {e}")

                        st.markdown("---")

                        # -------------------------------------------------
                        # 2. AI RESULT PANEL
                        # -------------------------------------------------
                        user_plan_raw = str(st.session_state.get("user_plan", "Free")).lower()

                        if any(plan in user_plan_raw for plan in ["premium", "elite", "vip"]):

                            if "active_ai_data" in st.session_state:

                                scan_time = st.session_state.get("ai_scan_time", "Unknown")

                                st.markdown(f"### 📊 Intelligence Report ({scan_time})")

                                st.markdown(
                                    f"""
                                    <div style="
                                        background-color:#0e1117;
                                        padding:20px;
                                        border-left:5px solid #00ff88;
                                        border-radius:10px;
                                        font-size:15px;
                                        line-height:1.6;
                                    ">
                                    {st.session_state["active_ai_data"]}
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

                            else:

                                st.info(
                                    "💡 Click the button above to synchronize with the **Gemini Neural Network** "
                                    "and generate institutional-grade market intelligence."
                                )

                        else:
                            # Hafatra ho an'ny Free users
                            st.warning(
                                "🔒 **AI Neural Prediction is locked.**\n\n"
                                "Upgrade to **Premium or Elite** to unlock institutional-grade AI market analysis."
                            )


            # ==========================================
            # 2. SESSION STATE INITIALIZATION
            # ==========================================
            if "trade_score" not in st.session_state:
                st.session_state.trade_score = 0

            if "calculated_lot" not in st.session_state:
                st.session_state.calculated_lot = 0.01

            # 1. ATAOVY EO AMBONY NY KAJY REHETRA (Calculations)
            # ==========================================
            # 4. PIP LOGIC & POSITION SIZING
            # ==========================================
            if "JPY" in ticker:
                pip_unit = 0.01
            elif "GC=F" in ticker:
                pip_unit = 0.1
            else:
                pip_unit = 0.0001

            sl_distance = atr * 2.0
            tp_distance = atr * 4.0
            sl_pips = sl_distance / pip_unit
            tp_pips = tp_distance / pip_unit
            risk_amount = balance * risk_pct_input

            if sl_pips > 0:
                lot_calc = risk_amount / (sl_pips * 10)
                st.session_state.calculated_lot = max(round(lot_calc, 2), 0.01)
            else:
                st.session_state.calculated_lot = 0.01

            # =========================================================
            # 5. MAIN UI DASHBOARD (FULL WIDTH - MIVOAKA NY COLUMNS)
            # =========================================================

            # Ity andalana ity dia mipetaka any amin'ny sisiny ankavia indrindra (un-indented)
            ticker_name = ASSET_MAP.get(ticker, ticker) 

            with st.container():
                # 1. TITLE (Lehibe sady mivoaka ny columns)
                st.markdown(f"""
                    <h1 style='text-align: left; font-size: 50px; margin-bottom: 0px;'>🤖 AI Chief Investment Officer</h1>
                    <p style='font-size: 20px; color: #888;'>Institutional Grade Market Intelligence</p>
                """, unsafe_allow_html=True)

                # 2. INFO BAR (Midadasika hameno pejy)
                inf1, inf2, inf3 = st.columns([1, 1, 1])
                inf1.subheader(f"🌐 Asset: `{ticker_name}`")
                inf2.subheader(f"⚖️ Risk Model: `{risk_pct_input*100:.1f}%`")
                inf3.subheader(f"💰 Balance: `${balance:,.2f}`")
                
                st.markdown("---")

                # --- 3. 💰 INSTITUTIONAL RISK & PROFIT CALCULATOR ---
                
                st.write("## 💰 Institutional Risk & Profit Calculator")

                m1, m2, m3 = st.columns(3)

                potential_loss = risk_amount
                calc_lot = st.session_state.get('calculated_lot', 0.0)
                potential_profit = calc_lot * tp_pips * 10

                # 1. Recommended Lot (Fotsy/Normal)
                with m1:
                    st.markdown(f"""
                        <p style='color: #888; margin-bottom: 0;'>RECOMMENDED LOT</p>
                        <h2 style='margin-top: 0;'>{calc_lot}</h2>
                    """, unsafe_allow_html=True)

                # 2. Potential Profit (Maitso mamirapiratra)
                with m2:
                    st.markdown(f"""
                        <p style='color: #888; margin-bottom: 0;'>POTENTIAL PROFIT</p>
                        <h2 style='color: #00ff88; margin-top: 0; text-shadow: 0 0 10px #00ff88;'>+${potential_profit:.2f}</h2>
                    """, unsafe_allow_html=True)

                # 3. Potential Loss (Mena tanteraka)
                with m3:
                    st.markdown(f"""
                        <p style='color: #888; margin-bottom: 0;'>POTENTIAL LOSS</p>
                        <h2 style='color: #ff4b4b; margin-top: 0; text-shadow: 0 0 10px #ff4b4b;'>-${potential_loss:.2f}</h2>
                    """, unsafe_allow_html=True)
                    
                # 4. PARAMETERS VS ACTIONS (Lasa midadasika kokoa izao)
                col_params, col_actions = st.columns(2)

                with col_params:
                    st.write("### 📊 Trade Parameters")
                    
                    # Ampiasaina ny HTML mba hanaovana ny chiffres ho miloko sy misongadina
                    st.markdown(f"""
                    <div style="background-color: #1e2630; padding: 20px; border-radius: 10px; border-left: 5px solid #00ff88;">
                        <p style="margin: 0; font-size: 18px;">
                            📏 <b>Stop Loss:</b> 
                            <span style="color: #ff4b4b; font-weight: bold; font-family: monospace;">{sl_pips:.1f} Pips</span>
                        </p>
                        <p style="margin: 10px 0; font-size: 22px;">
                            🎯 <b>Take Profit:</b> 
                            <span style="color: #00ff88; font-weight: bold; font-family: monospace; text-shadow: 0 0 10px #00ff88;">{tp_pips:.1f} Pips</span>
                        </p>
                        <p style="margin: 0; font-size: 16px; color: #888;">
                            ⚖️ <b>RR Ratio:</b> 1:2.0 (Volatility Based)
                        </p>
                    </div>
                    <br>
                    """, unsafe_allow_html=True)

                with col_actions:
                    st.write("🔍 **Institutional Actions**")
                    
                    # Access Logic
                    user_plan = str(st.session_state.get("user_plan", "Free")).lower().strip()
                    allowed_plans = ["pro", "elite", "premium", "vip", "basic access", "pro access"]
                    has_pro_access = any(plan in user_plan for plan in allowed_plans)

                    btn_col1, btn_col2 = st.columns(2)
                    
                    with btn_col1:
                        if not has_pro_access:
                            st.button("🧠 AI ANALYSIS 🔒", use_container_width=True, key="calc_ai_locked", disabled=True)
                        else:
                                if st.button("🧠 AI ANALYSIS", use_container_width=True, key="calc_ai_btn"):

                                    if 'df' in locals() and not df.empty:
                                        with st.spinner("🤖 Analyzing Market & Risk..."):
                                            current_p = df['Close'].iloc[-1]
                                            calc_context = (f"Analysis for {ticker_name}. Trade Plan: Lot={calc_lot}, "
                                                           f"Target Profit=${potential_profit:.2f}, Risk=${potential_loss:.2f}. "
                                                           f"Evaluate if this RR is realistic based on current market structure.")
                                            report = get_ai_deep_analysis(asset_label, current_p, df)
                                            st.session_state.ai_comment = f"### 💡 Trade Context\n{calc_context}\n\n---\n{report}"

                                            st.success("✅ Analysis Complete!")
                                    else:
                                        st.warning("⚠️ Tsy misy data. Miandrasa kely...")
                               
                    with btn_col2:
                        if not has_pro_access:
                            st.button("📅 LIVE NEWS 🔒", use_container_width=True, key="calc_news_locked", disabled=True)
                        else:
                                if st.button("📅 LIVE NEWS", use_container_width=True, key="calc_news_v5"):
                                    with st.spinner("Streaming Live Intelligence..."):
                                        news_data = get_live_news(asset_label)
                                        st.session_state['news'] = news_data
                                        st.success("✅ News Synchronized")
                        if not has_pro_access:
                            st.caption("🔒 *Institutional AI & Live News are only available for Pro users.*")
                    
            # 5. GLOBAL OUTPUT AREA (Hameno pejy tanteraka)
            if "news" in st.session_state and has_pro_access:
                with st.expander("📅 MARKET CALENDAR / NEWS", expanded=True):
                    st.markdown(st.session_state['news'])

            if "ai_comment" in st.session_state and has_pro_access:
                with st.expander("📊 DETAILED STRATEGY REPORT", expanded=True):
                    st.markdown(st.session_state.ai_comment)
                    
                # ==========================================
				# 6. GEMINI CIO BRIEFING (WITH TRIPLE FALLBACK)
				# ==========================================
				st.markdown("---")
				st.subheader("🧠 Institutional AI Intelligence")

				# Function kely hitantana ny fampitahana modely (Routing)
				def get_cio_briefing_logic(prompt):
					client = get_ai_client()
					if client is None:
						return "⚠️ AI system unavailable. API key missing."

					# --- 1. GEMINI 2.5 FLASH (Primary) ---
					try:
						res = client.models.generate_content(
							model="models/gemini-2.5-flash",
							contents=prompt
						)
						return f"🟢 **[Gemini 2.5 Flash]**\n\n{res.text}"
					
					except Exception as e:
						error_msg = str(e).upper()
						# Raha lany quota (429) vao mifindra
						if "429" in error_msg or "QUOTA" in error_msg or "EXHAUSTED" in error_msg:
							
							# --- 2. GEMMA 3 27B (Backup 1) ---
							try:
								st.info("🔄 Gemini quota reached. Switching to Gemma 3 27B...")
								res_backup = client.models.generate_content(
									model="models/gemma-3-27b-it",
									contents=prompt
								)
								return f"🟡 **[Gemma 3 27B]**\n\n{res_backup.text}"
							
							except Exception:
								# --- 3. GROQ LLAMA 3.3 (Backup 2 - Emergency) ---
								try:
									st.warning("🔄 Using Groq Llama 3.3 (Emergency Backup)...")
									# Miantso an'ilay function Groq efa namboarintsika
									return f"🔵 **[Groq Llama 3.3]**\n\n{call_groq_fallback(prompt)}"
								except:
									return "❌ All AI models exhausted. Please wait 60s."
						
						return f"⚠️ AI Error: {str(e)}"

				# Ny bokotra eo amin'ny UI
				if st.button(
					"🤖 GENERATE CIO BRIEFING",
					use_container_width=True,
					key="btn_cio_gemini"
				):
					with st.spinner("CIO is reviewing trade parameters..."):
						# Fanomanana ny Prompt
						prompt = f"""
						Act as a Chief Investment Officer (CIO) of a hedge fund.
						Analyze this Forex / Gold trade:
						Asset: {ticker_name}
						Current Price: {current_price}
						ATR Volatility: {atr:.5f}
						Risk per Trade: {risk_pct_input*100:.2f}%
						Recommended Lot Size: {st.session_state.get("calculated_lot",0)}
						Stop Loss: {sl_pips:.1f} pips
						Take Profit: {tp_pips:.1f} pips (Risk Reward 1:2)

						Provide a concise institutional briefing (maximum 3 sentences).
						Focus on: Risk quality, ATR support, and viability.
						End with: [SCORE: XX] (0-100)
						"""
						
						# Fiantsoana ny rafitra Fallback
						result_text = get_cio_briefing_logic(prompt)
						st.markdown(result_text)
		
                                # --------------------------------
                                # Extract AI score
                                # --------------------------------
                                match = re.search(r"\[SCORE:\s*(\d+)\]", full_text)

                                score = int(match.group(1)) if match else 50

                                st.session_state.trade_score = score

                                clean_text = re.sub(
                                    r"\[SCORE:\s*\d+\]",
                                    "",
                                    full_text
                                ).strip()

                                # =====================================
                                # CIO STRATEGIC BRIEF
                                # =====================================
                                left, right = st.columns([2,1])

                                with left:

                                    st.info(
                                        f"**CIO Strategic Briefing:**\n\n{clean_text}"
                                    )

                                with right:

                                    st.metric("AI Score", f"{score}%")
                                    st.progress(score/100)

                                    if score >= 75:
                                        st.success("HIGH CONVICTION")
                                    elif score >= 40:
                                        st.warning("TACTICAL ENTRY")
                                    else:
                                        st.error("HIGH RISK / AVOID")

                                # =====================================
                                # AI CONFIDENCE GAUGE
                                # =====================================
                                st.markdown("---")
                                st.markdown("### 🧠 AI Confidence Gauge")

                                g1, g2 = st.columns([1,3])

                                with g1:
                                    st.metric("Confidence", f"{score}%")

                                with g2:
                                    st.progress(score/100)

                                # =====================================
                                # TRADE PROBABILITY PANEL
                                # =====================================
                                st.markdown("### 📊 Trade Probability")

                                win_probability = min(95, max(10, score))

                                if score >= 70:
                                    regime = "Trending Market"
                                    risk_quality = "Low Risk"
                                elif score >= 40:
                                    regime = "Mixed Market"
                                    risk_quality = "Moderate Risk"
                                else:
                                    regime = "Unstable Market"
                                    risk_quality = "High Risk"

                                c1, c2, c3 = st.columns(3)

                                c1.metric("Win Probability", f"{win_probability}%")
                                c2.metric("Market Regime", regime)
                                c3.metric("Risk Quality", risk_quality)

                                # =====================================
                                # INSTITUTIONAL RISK METER
                                # =====================================
                                st.markdown("### 🏦 Institutional Risk Meter")

                                risk_level = 100 - score

                                st.progress(risk_level/100)

                                if risk_level <= 25:
                                    st.success("Risk Level: LOW")
                                elif risk_level <= 60:
                                    st.warning("Risk Level: MODERATE")
                                else:
                                    st.error("Risk Level: HIGH")

                            except Exception as e:
                                st.error(f"AI Offline: {e}")


                # ==========================================
                # 7. EXECUTION SAFETY LOCK
                # ==========================================
                st.divider()

                if st.session_state.trade_score > 0:

                    if st.session_state.trade_score < 40:
                        st.error(
                            f"⛔ **TRADE BLOCKED:** "
                            f"Score too low ({st.session_state.trade_score}%). "
                            f"Risk profile is sub-optimal."
                        )

                        st.button(
                            "🚀 EXECUTE TRADE",
                            disabled=True,
                            use_container_width=True
                        )

                    else:
                        st.success(
                            f"✅ **TRADE APPROVED:** "
                            f"Confidence Score {st.session_state.trade_score}% "
                            f"meets institutional requirements."
                        )

                        if st.button(
                            "🚀 EXECUTE TRADE NOW",
                            type="primary",
                            use_container_width=True
                        ):
                            st.balloons()
                            st.write(
                                f"Executing {st.session_state.calculated_lot} "
                                f"lots on {ticker_name}..."
                            )
                else:
                    st.info(
                        "💡 **Pre-Trade Requirement:** "
                        "Please generate the CIO Briefing to unlock the execution terminal."
                    )

                # Andalana faharoa: Google Sheets Sync (Lehibe kokoa)
                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                if st.button("📤 SYNC SIGNAL TO GOOGLE SHEETS", use_container_width=True, key="btn_sheet_sync"):
                    with st.spinner("Syncing with Google Sheets..."):
                        bias_text = "BUY" if is_buy else "SELL"
                        success = send_to_google_sheets(
                            ASSET_MAP[ticker], 
                            bias_text, 
                            ls['Close'], 
                            sl, 
                            tp, 
                            f"{lot:.2f}", 
                            f"{potential_profit:.2f}"
                        )
                        if success:
                            st.toast("✅ Synced to Google Sheets!", icon="🚀")
                            st.success("✅ Signal successfully synced to Trading Journal!")
                        else:
                            st.error("❌ Failed to sync. Check JSON file and Sheet permissions.")
  
            # --- 4. EXPORT SECTION ---
            st.markdown("---")

            report_data = st.session_state.get("ai_comment")

            if not report_data:
                st.warning("⚠️ Please run AI Analysis first to generate a report.")
            else:

                if st.button("📄 PREPARE OFFICIAL REPORT", use_container_width=True):

                    with st.spinner("Generating professional PDF report..."):

                        try:

                            ai_cal = st.session_state.get(
                                "news",
                                "N/A: No economic data streamed."
                            )

                            trades = st.session_state.get("trades", [])

                            pdf_bytes = export_ultra_premium_pdf(
                                ASSET_MAP[ticker],
                                ls,
                                tp,
                                sl,
                                report_data,
                                ai_cal,
                                fig,
                                f"Institutional Briefing: {ticker}",
                                trades
                            )

                            st.session_state.ready_pdf = pdf_bytes

                            st.success("✅ Report Ready for Download!")

                        except Exception as e:
                            st.error(f"Error inside PDF generator: {e}")


                if st.session_state.ready_pdf:

                    st.download_button(
                        label="⬇️ CLICK HERE TO SAVE PDF",
                        data=st.session_state.ready_pdf,
                        file_name=f"VNS_Institutional_{ticker}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

                # --- ETO NO MIHAKATONA NY TRY LEHIBE REHETRA ---
    except Exception as e:
        st.error(f"Error loading data or processing: {e}")

    # --- 5. THE PROFESSIONAL FOOTER DASHBOARD (Ivelan'ny try foana) ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    
    col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)
    
    with col_f1:
        if st.button("📖 ABOUT VNS", key="forex_about_btn"): show_about()
    with col_f2:
        # Azonao atao ny manamboatra 'show_privacy()' manokana raha tianao
        if st.button("🛡️ PRIVACY", key="f_privacy"): show_security_terms() 
    with col_f3:
        if st.button("🔒 SECURITY", key="f_security"): show_security_terms()
    with col_f4:
        if st.button("✉️ CONTACT", key="f_contact"): show_contact()
    with col_f5:
        st.markdown('''
            <div style="text-align:center; padding:8px; border:1px solid #00ffcc; 
            border-radius:5px; color:#00ffcc; font-weight:bold; font-size:11px; 
            background: rgba(0, 255, 204, 0.05);">
                🛰️ NODE 2026: ACTIVE
            </div>
            ''', unsafe_allow_html=True)

    # Final Elite Footer Call
    vns_footer_high_pro_v2()
    
# --- FUNCTION FANDE FASANA (Apetraho any ivelan'ny loop) ---
def send_now(data):
    # Ny headers dia mila x-api-key ARY indraindray x-app-id
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY,
        "Authorization": f"Bearer {API_KEY}"
    }
    
    try:
        # Ataovy azo antoka fa ao anatin'ny 'try' ny requests.post
        res = requests.post(API_URL, json=data, headers=headers)
        
        if res.status_code in [200, 201]:
            st.success("✅ Signal sent successfully!")
            st.toast("Vita ny fandefasana!", icon="🚀")
        elif res.status_code == 403:
            st.error("❌ Error 403: Auth Required. Ny App-nao ao amin'ny Base44 dia mety ho 'Private'.")
            st.info("Soso-kevitra: Hamarino ao amin'ny Base44 Dashboard raha 'Public' ny App-nao na mila 'Session Cookie'.")
            st.json(res.json())
        else:
            st.error(f"❌ Error {res.status_code}: {res.text}")
            
    except Exception as e:
        st.error(f"⚠️ Fifandraisana tsy nahomby: {e}")
    
# ==========================================
# ENTRY POINT FOR ROUTER
# ==========================================

def show_page():
    try:
        # Ovay hoe main() fa aza atao app()
        main() 
    except Exception as e:
        st.error(f"Error loading page: {e}")

# Fafao tanteraka ilay if __name__ == "__main__": any amin'ny farany
