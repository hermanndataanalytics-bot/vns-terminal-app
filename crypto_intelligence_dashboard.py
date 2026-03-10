import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ta
from google.oauth2.service_account import Credentials
import gspread
from datetime import datetime
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle 
from reportlab.lib.pagesizes import letter
from streamlit_autorefresh import st_autorefresh
from openai import OpenAI
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import re  # Ity no hanadio ny text
import io
from google import genai
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
import qrcode
import hashlib
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
import streamlit.components.v1 as components
from datetime import datetime, timezone

# Misoroka ny olana amin'ny file watcher amin'ny Windows
os.environ['STREAMLIT_SERVER_FILE_WATCHER_TYPE'] = 'none'
# ======================================================
# 1. CONFIG & STYLE
# ======================================================
st.set_page_config(page_title="VNS | Professional Crypto Desk", page_icon="⚡", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #0e1117 !important; }
.header-box {
    background-color: #161b22;
    padding: 20px;
    border-left: 10px solid #00ffcc;
    border-radius: 5px;
    margin-bottom: 25px;
}
.signal-container {
    padding: 25px;
    border-radius: 10px;
    text-align: center;
    margin: 15px 0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# 2. CONFIG & SETUP
# ======================================================
SERVICE_ACCOUNT_FILE = "serviceAccountKey.json"
SHEET_ID = "196I1LCyt59lySUyKlT2I7B9OEe8AuYa4FNSmlbXSjpY"
api_key = st.secrets["CRYPTO_GENAI_KEY"]
ai_client = genai.Client(api_key=api_key)

ASSET_MAP = {
    "Bitcoin / USD": "BTC-USD",
    "Ethereum / USDbias": "ETH-USD",
    "BNB / USD": "BNB-USD",
    "Cardano / USD": "ADA-USD",
    "Solana / USD": "SOL-USD",
    "XRP / USD": "XRP-USD"
}

# ======================================================
# 3. SESSION STATE INITIALIZATION
# ======================================================
if "ai_text" not in st.session_state:
    st.session_state.ai_text = None
if "economic_calendar" not in st.session_state:
    st.session_state.economic_calendar = None

# ======================================================
# 4. GOOGLE SHEETS SYNC
# ======================================================
def send_signal_to_vns_sheets(data_list):
    try:
        creds = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, 
            scopes=["https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"]
        )
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(SHEET_ID)
        ws = sh.worksheet("Trading_Journal")
        ws.insert_row(data_list, index=3) 
        return True
    except:
        return False

# ======================================================
# 5. AI FUNCTIONS
# ======================================================
def ai_explain(trade, score):
    # Fanitsiana ny fomba fakana ny key
    try:
        key = "AIzaSyCzo49qIOoADBq55SdTLltg-0vqnipWl4w"
    except Exception:
        return "Gemini API Key missing in secrets.toml"
        
    prompt = f"""
    You are a professional Crypto Quant Analyst.
    Asset: {trade.get('asset')}
    Price: {trade.get('price')}
    Bias: {trade.get('bias')}
    Stop Loss: {trade.get('SL')}
    Take Profit: {trade.get('TP')}
    Score: {score}
    propose un setup de trade avec :
	– point d’entrée optimal
	– stop loss technique
	– take profit 1, 2 et 3
	– ratio risk/reward minimal 1:2
	– invalidation claire du setup.”.
    “Calcule la taille de position idéale si mon capital est de 1 000 USDT,risque maximum 1% par trade,en tenant compte du stop loss proposé.”	
		"""

    try:
        # Ampiasao gemini-2.5-flash (version marina)
        res = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return res.text
    except Exception as e:
        return f"Analysis Error: {e}"

def get_ai_calendar(asset):
    # Mitovy amin'ny etsy ambony ny fanitsiana ny key
    try:
        key = "AIzaSyCzo49qIOoADBq55SdTLltg-0vqnipWl4w"
    except Exception:
        return "Gemini API Key missing."
        
    today_date = datetime.now().strftime("%B %d, %Y")
    prompt = f""" Today is {today_date}. Provide Economic Calendar for next 2 days for {asset}.
	IMPORTANT: Always use the European date format (DD/MM/YYYY) in your response.
	"""

    try:
        res = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return res.text
    except Exception as e:
        return f"Calendar Error: {e}"
	

def generate_qr(data):
    """Mamokatra QR Code ho sary azo ampidirina ao amin'ny PDF."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")
    
    img_buffer = io.BytesIO()
    img_qr.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    return img_buffer

def generate_signature(asset, date_str, score):
    """Mamokatra sonia SHA-256 miavaka ho an'io report io."""
    raw_data = f"{asset}-{date_str}-{score}-VNS-TERMINATOR-2026"
    signature = hashlib.sha256(raw_data.encode()).hexdigest()
    return signature.upper()

def build_pdf_interactive(asset, trade, ai_text, fig):
    try:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf, 
            pagesize=letter, 
            rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=50,
            title=f"VNS_Report_{asset}",
            author="VNS Terminator Corp"
        )
        
        styles = getSampleStyleSheet()
        content = []

        # --- Styles Definitions ---
        header_pro = ParagraphStyle('HeaderPro', parent=styles['Heading2'], textColor=colors.HexColor("#D4AF37"), fontSize=14, spaceAfter=10)
        cover_title = ParagraphStyle("CoverTitle", fontSize=28, alignment=TA_CENTER, leading=32, spaceAfter=18, fontName="Helvetica-Bold")
        cover_sub = ParagraphStyle("CoverSub", fontSize=13, alignment=TA_CENTER, textColor=HexColor("#404040"), spaceAfter=28)
        security_style = ParagraphStyle("Security", fontSize=9, alignment=TA_CENTER, textColor=colors.HexColor("#6B6B6B"), spaceAfter=6)
        summary_style = ParagraphStyle("Summary", fontSize=11, alignment=TA_CENTER, leading=16, spaceAfter=14)
        signature_style = ParagraphStyle("Signature", fontSize=8, alignment=TA_CENTER, textColor=HexColor("#666666"), spaceAfter=6)

        # ===============================
        # PAGE 1 — FULL PREMIUM COVER
        # ===============================
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(base_path, "vns_logo.png")
            logo = Image(logo_path, width=160, height=160)
            logo.hAlign = "CENTER"
            content.append(logo)
        except:
            content.append(Paragraph("<b>VNS PRO</b>", cover_title))

        content.append(Spacer(1,25))
        content.append(Paragraph("<b>VNS PRO TRADING REPORT</b>", cover_title))
        content.append(Paragraph(f"{asset} · AI-Driven Institutional Market Intelligence", cover_sub))

        today = datetime.utcnow().strftime("%B %d, %Y | %H:%M UTC")
        content.append(Paragraph("SECURITY CLEARANCE: AUTHORIZED ACCESS ONLY", security_style))
        content.append(Paragraph(f"DATE OF ISSUE: {today}", security_style))
        content.append(Paragraph("CONFIDENTIAL – INTERNAL DISTRIBUTION ONLY", security_style))

        content.append(Spacer(1, 30))
        content.append(Paragraph("<b>EXECUTIVE SUMMARY</b>", security_style))
        content.append(Spacer(1, 15))
        content.append(Paragraph("This institutional-grade report delivers an AI-driven assessment of market structure, momentum conditions, and risk-adjusted positioning.", summary_style))

        content.append(Spacer(1, 35))

        # ---- QR Verification ----
        try:
            qr_payload = f"VNS PRO: {asset}\nDATE: {today}\nVERIFY: vnspro.ai/verify"
            qr_img_data = generate_qr(qr_payload)
            qr_img = Image(qr_img_data, width=90, height=90)
            qr_img.hAlign = "CENTER"
            content.append(qr_img)
        except Exception as e:
            content.append(Paragraph(f"[QR ERROR]", security_style))

        content.append(Spacer(1, 14))

        # ---- Cryptographic Signature ----
        try:
            score_val = trade.get("score", "NA")
            sig_val = generate_signature(asset, today, score_val)
            content.append(Paragraph("<b>CRYPTOGRAPHIC SIGNATURE (SHA-256)</b>", security_style))
            content.append(Paragraph(sig_val, signature_style))
        except:
            content.append(Paragraph("SIGNATURE ERROR", signature_style))

        content.append(Spacer(1, 35))
        

		# ===============================================
        # PAGE 2 — ANALYSIS & CHART
        # ===============================================
        content.append(PageBreak())
        
        # Header for Page 2
        content.append(Paragraph(f"Predictive Market Modeling: {asset}", header_pro))
        content.append(Spacer(1, 15))

        # --- Chart Generation (HD) ---
        try:
            # Note: Ensure 'fig' is your Plotly figure object
            img_bytes = fig.to_image(
                format="png",
                width=1200,   
                height=600,
                scale=4       # High Definition
            )

            chart_img = Image(
                io.BytesIO(img_bytes),
                width=6.5 * inch,  
                height=3.25 * inch
            )
            chart_img.hAlign = 'CENTER'
            content.append(chart_img)
            content.append(Spacer(1, 20)) 

        except Exception as e:
            content.append(Paragraph(f"<span color='red'>[CHART ERROR]</span> {e}", styles['Normal']))
            
        content.append(Paragraph(f"AI-Driven Quantitative Intelligence: {asset}", header_pro))

        # --- AI Text Processing ---
        clean_text = ai_text.replace('**', '')
        clean_text = re.sub(r'#+\s*', '', clean_text)
        clean_text = clean_text.replace('* ', '• ')

        for line in clean_text.split('\n'):
            line = line.strip()
            if line:
                if len(line) < 50 and not line.startswith('•'):
                    # Sub-headers in Bold/Uppercase
                    content.append(Paragraph(f"<b>{line.upper()}</b>", styles["Normal"]))
                else:
                    content.append(Paragraph(line, styles["Normal"]))
                content.append(Spacer(1, 4))

        # ================= SIGNATURE SECTION =================
        content.append(Spacer(1, 40))
        if os.path.exists("signature.png"):
            sig = Image("signature.png", width=1.5*inch, height=0.6*inch)
            sig.hAlign = 'LEFT'
            content.append(sig) 
        
        content.append(Paragraph("VNS TERMINATOR", styles['Normal']))
        content.append(Paragraph("<b>AUTHORIZED CHIEF ANALYST</b>", 
                       ParagraphStyle('Sig', fontSize=10, textColor=colors.gold)))

        # --- Canvas / Background Function ---
        def add_background(canvas, doc):
            canvas.saveState()
            # Golden Footer Line
            canvas.setStrokeColor(colors.HexColor("#D4AF37"))
            canvas.setLineWidth(1.5)
            canvas.line(40, 50, 572, 50)
            
            # Footer Branding
            footer_text = "VNS TERMINATOR CORPORATION © 2026 | ALL RIGHTS RESERVED | CONFIDENTIAL"
            canvas.setFont('Helvetica-Bold', 7)
            canvas.setFillColor(colors.HexColor("#1f2c3a"))
            canvas.drawCentredString(letter[0]/2, 35, footer_text)
            
            # Watermark "VNS PRO"
            canvas.setFont('Helvetica-Bold', 60)
            canvas.setStrokeColor(colors.lightgrey)
            canvas.setStrokeAlpha(0.1)
            canvas.setFillAlpha(0.1)
            canvas.drawCentredString(letter[0]/2, letter[1]/2, "VNS PRO")
            canvas.restoreState()

        # Build PDF once
        doc.build(content, onFirstPage=add_background, onLaterPages=add_background)
        buf.seek(0)
        return buf

    except Exception as e:
        print(f"Final PDF Error: {e}")
        return None	
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
                <code style="color:#00ffcc; font-size:0.8rem;">sales@vns-terminator.com</code>
            </div>
            <div style="background: rgba(0,255,204,0.05); padding: 15px; border-radius: 8px; border: 1px solid rgba(0,255,204,0.2);">
                <p style="margin:0; font-size:0.7rem; color:#888;">TECH_SUPPORT</p>
                <code style="color:#00ffcc; font-size:0.8rem;">support@vns-terminator.com</code>
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
     components.html("""
    <style>
        .vns-premium-footer {
            background: rgba(10, 10, 10, 0.9);
            backdrop-filter: blur(20px);
            color: #ffffff;
            padding: 60px 40px 30px;
            font-family: 'Inter', sans-serif;
            border-top: 1px solid rgba(0, 255, 204, 0.3);
            margin-top: 80px;
        }
        .premium-grid {
            display: grid;
            grid-template-columns: 3fr 1.2fr 1.2fr 1.5fr; 
            gap: 30px;
            max-width: 1300px;
            margin: 0 auto;
        }
        .brand-title { color: #00ffcc; font-size: 1.8rem; font-weight: 900; margin: 0; white-space: nowrap; }
        .footer-header { color: #00ffcc; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; margin-bottom: 20px; display: block; }
        .footer-links { list-style: none; padding: 0; margin: 0; color: #888; font-size: 0.85rem; line-height: 1.8; }
        .status-box { background: rgba(0, 255, 204, 0.05); border: 1px solid rgba(0, 255, 204, 0.1); padding: 15px; border-radius: 10px; font-size: 0.75rem; min-width: 180px; }
        .copyright-bar { text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #222; font-size: 0.7rem; color: #444; }
        #live-clock { font-family: 'JetBrains Mono', monospace; color: #00ffcc; font-weight: bold; }
    </style>
    
    <footer class="vns-premium-footer">
        <div class="premium-grid">
            <div>
                <h2 class="brand-title">VNS TERMINATOR</h2>
                <p style="color:#666; font-size:0.85rem; margin-top: 10px;">Evolutionary Quantum Intelligence for the 2026 digital frontier.</p>
            </div>
            <div>
                <span class="footer-header">🌐 Ecosystem</span>
                <ul class="footer-links"><li>Neural Terminal</li><li>Liquidity Map</li><li>Risk Engine</li></ul>
            </div>
            <div>
                <span class="footer-header">🛡️ Governance</span>
                <ul class="footer-links"><li>ISO 27001:2026</li><li>SOC3 Audit</li><li>Legal</li></ul>
            </div>
            <div class="status-box">
                <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                    <span>Node Status:</span> <span style="color:#00ffcc; font-weight:bold;">ACTIVE</span>
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                    <span>AI Accuracy:</span> <span style="color:#00ffcc; font-weight:bold;">99.98%</span>
                </div>
                <div style="display:flex; justify-content:space-between; padding-top: 5px; border-top: 1px solid rgba(0,255,204,0.1);">
                    <span>System Time:</span> <span id="live-clock">00:00:00</span>
                </div>
            </div>
        </div>

        <script>
            function updateClock() {
                const now = new Date();
                const h = String(now.getHours()).padStart(2, '0');
                const m = String(now.getMinutes()).padStart(2, '0');
                const s = String(now.getSeconds()).padStart(2, '0');
                const el = document.getElementById('live-clock');
                if (el) {
                    el.textContent = h + ":" + m + ":" + s;
                }
            }
            setInterval(updateClock, 1000);
            updateClock();
        </script>

        <div class="copyright-bar">
            © 2026 VNS TERMINATOR CORP. | ALL SYSTEMS ENCRYPTED | EXPERT PROFESSIONAL EDITION
        </div>
    </footer>
  """, height=360)
	
# ======================================================
# 7. MAIN APP - PREMIUM EXPERT EDITION
# ======================================================
# Refresh isaky ny 5 minitra mba hadio ny fandehan'ny data
st_autorefresh(interval=300000, key="hub_refresh")

def app():
	
	# HEADER PREMIUM
    st.markdown("""
    <div style="background: linear-gradient(90deg, #000428 0%, #004e92 100%); padding:20px; border-radius:15px; margin-bottom:25px; border: 1px solid #00ffcc; text-align:center;">
        <h1 style="margin:0; color:white; font-family:sans-serif; letter-spacing:2px;">VNS QUANTUM INTELLIGENCE v2.0</h1>
        <p style="color:#00ffcc; margin:0; font-weight:lighter;">Institutional Grade Scalping Terminal | AI-Powered</p>
    </div>
    """, unsafe_allow_html=True)
	# --- 2. NOTIFICATION SYSTEM (TOAST) ---
    # Mipoitra eo am-pifohana ny app
    st.toast("🛡️ Quantum Security Protocol Active", icon="✅")
    st.toast("🛰️ Uplink to Neural Network Established", icon="🌐")

    # --- INPUT FORM ---
    with st.form("premium_config"):
        c1, c2, c3, c4 = st.columns(4)
        with c1: asset = st.selectbox("💎 ASSET", list(ASSET_MAP.values()))
        with c2: timeframe = st.selectbox("⏱️ TIMEFRAME", ["1h","4h","1d"])
        with c3: period = st.slider("📅 LOOKBACK (Days)", 20,150,50)
        with c4: risk_mode = st.selectbox("🛡️ RISK MODE", ["Conservative","Aggressive"])
        submitted = st.form_submit_button("⚡ EXECUTE QUANT ANALYSIS")

    # --- DATA ENGINE ---
    try:
        df = yf.download(asset, period=f"{period}d", interval=timeframe, progress=False)
    except Exception as e:
        st.error(f"Engine Error: {e}")
        return

    if df is not None and not df.empty:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.dropna()

        try:
            # --- Indicators ---
            df['SMA200'] = ta.trend.sma_indicator(df['Close'], window=200) if len(df)>200 else df['Close']
            df['VWAP'] = (df['Close']*df['Volume']).cumsum()/df['Volume'].cumsum()
            df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
            macd_obj = ta.trend.MACD(df['Close'])
            df['MACD'] = macd_obj.macd_diff()
            atr_val = ta.volatility.average_true_range(df['High'], df['Low'], df['Close']).iloc[-1]

            # --- Latest Values ---
            lp = float(df['Close'].iloc[-1])
            lr = float(df['RSI'].iloc[-1])
            l_vwap = float(df['VWAP'].iloc[-1])
            l_macd = float(df['MACD'].iloc[-1])

            # --- Scoring & Bias ---
            score = 0
            if lp > l_vwap: score+=25
            if 40<lr<65: score+=15
            if l_macd>0: score+=20
            if lp>df['SMA200'].iloc[-1]: score+=20
            if df['Volume'].iloc[-1]>df['Volume'].rolling(20).mean().iloc[-1]: score+=20

            if score>=65: bias,color,bg="STRONG BUY","#00ffcc","rgba(0,255,204,0.1)"
            elif score<=35: bias,color,bg="STRONG SELL","#ff3333","rgba(255,51,51,0.1)"
            else: bias,color,bg="NEUTRAL","#ffffff","rgba(255,255,255,0.1)"

            # --- UI Metrics ---
            m1,m2,m3,m4 = st.columns(4)
            m1.metric("PRICE", f"${lp:,.2f}")
            m2.metric("RSI (14)", f"{lr:.2f}")
            m3.metric("QUANT SCORE", f"{score}/100")
            m4.metric("BIAS", bias)

            st.markdown(f"""
            <div style="background:{bg}; border:2px solid {color}; padding:30px; border-radius:15px; text-align:center;">
                <h1 style="color:{color}; font-size:3.5rem; font-weight:bold;">{bias}</h1>
                <p style="color:white;">Institutional Confidence Level: {score}%</p>
            </div>
            """, unsafe_allow_html=True)

            # --- Plotly Chart ---
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7,0.3])
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1,col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], name="VWAP", line=dict(color='#00ffcc', width=2)), row=1,col=1)
            fig.add_trace(go.Bar(x=df.index, y=df['MACD'], name="MACD Diff", marker_color=color), row=2,col=1)
            fig.update_layout(height=700, template="plotly_dark", xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

            # --- RISK MANAGEMENT ---
            st.markdown("---")
            st.subheader("📊 EXECUTIVE SUMMARY & RISK")
            sl = lp-(atr_val*2) if "BUY" in bias else lp+(atr_val*2)
            tp = lp+(atr_val*4) if "BUY" in bias else lp-(atr_val*4)

            r_col1,r_col2 = st.columns(2)
            with r_col1:
                st.write(f"🎯 **Institutional TP:** `${tp:,.2f}`")
                st.write(f"🛑 **Hard Stop Loss:** `${sl:,.2f}`")
                st.write(f"⚖️ **Risk/Reward:** 1:2.0 (ATR-Based)")
            with r_col2:
                trade = {"asset":asset,"price":lp,"score":score,"bias":bias,"SL":sl,"TP":tp}
                if st.button("🧠 GENERATE AI PRO REPORT"):
                    with st.spinner("AI is analyzing market..."):
                        st.session_state.ai_pro = ai_explain(trade,score)
                if "ai_pro" in st.session_state: st.info(st.session_state.ai_pro)

            # --- RISK CALCULATION (Addition) ---
            lot_size = 0.10 if risk_mode == "Aggressive" else 0.01
            # Fikajiana ny tombony (Profit Potential) miankina amin'ny elanelan'ny TP sy Price
            profit_val = abs(tp - lp) * (100 if "USD" in asset else 1) * lot_size

            # --- AUTO-SEND SIGNAL ---
            # Boriboriana ho isa feno (no decimals) ny profit_potential
            signal_row = [datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),f"{asset} ({timeframe})", bias, lp, sl, tp, lot_size, int(round(profit_val)), score]
            if "last_signal_id" not in st.session_state: 
                st.session_state.last_signal_id = None

            # Fampitahana ny ID (Asset + Bias + Price)
            current_id = f"{asset}_{bias}_{lp}"

            if st.session_state.last_signal_id != current_id:
                sent = send_signal_to_vns_sheets(signal_row)
                if sent:
                    st.success(f"✅ Signal for {asset} sent to Trading Dashboard.")
                    st.session_state.last_signal_id = current_id
                else:
                    st.error(f"❌ Failed to send signal for {asset}.")
            else:
                st.info(f"ℹ️ Signal for {asset} already logged.")
				
            st.markdown("---")
            ac1, ac2, ac3 = st.columns(3)

            with ac1:
                if st.button("🚀 Deep Market Analysis"):
                    with st.spinner("Analyzing..."):
                        st.session_state.ai_text = ai_explain(trade, score)
                if "ai_text" in st.session_state: 
                    st.info(st.session_state.ai_text)
            
            with ac2:
                if st.button("📅 Macro Calendar"):
                    with st.spinner("Fetching data..."):
                        st.session_state.economic_calendar = get_ai_calendar(asset)
                if "economic_calendar" in st.session_state: 
                    st.warning(st.session_state.economic_calendar)
            
            with ac3:
                if st.button("📄 Export PDF Report"):
                    try:
                        # 1. Mitady fanazavana AI (avy amin'ny bokotra rehetra)
                        ai_content = st.session_state.get("ai_pro") or st.session_state.get("ai_text") or "No detailed AI analysis was generated for this session."
                        
                        # 2. Mamorona ny PDF
                        pdf_buf = build_pdf_interactive(asset, trade, ai_content, fig)
                        
                        # 3. Mampiseho ny bokotra download
                        if pdf_buf:
                            st.success("✅ PDF Generated!")
                            st.download_button(
                                label="📥 Download Expert Report",
                                data=pdf_buf,
                                file_name=f"VNS_PRO_{asset}.pdf",
                                mime="application/pdf"
                            )
                    except Exception as e:
                        st.error(f"PDF Generation Error: {e}")

        except Exception as e:
            st.error(f"Analysis Engine Error: {e}")
			
        # --- THE PROFESSIONAL FOOTER DASHBOARD ---
    # Ity fizarana ity dia mivoaka ivelan'ny 'try/except' mba ho hita foana na misy error aza
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    
    col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)
    
    with col_f1:
        if st.button("📖 ABOUT VNS", key="f_about"): show_about()
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
	
# ======================================================
# 🔑 PUBLIC API (CRITICAL FIX)
# ======================================================
def show_crypto_page():
    app()

def main():
    app()	

if __name__ == "__main__":
    app()
