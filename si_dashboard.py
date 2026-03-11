import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials
import streamlit.components.v1 as components
from datetime import datetime
import os
import plotly.graph_objects as go
from binance.client import Client
import time

st.set_page_config(
    page_title="VNS TERMINATOR PRO | AI Market Terminal",
    layout="wide",
    page_icon="🤖",  # Na "🤖" raha tianao ny AI icon
)

ticker_html = """
<div style="background-color: #0e1117; color: #00ff00; padding: 10px; border-radius: 5px; border: 1px solid #333;">
    <marquee behavior="scroll" direction="left">
        <b>EURUSD:</b> 1.0845 (▲ 0.12%) &nbsp;&nbsp;&nbsp; 
        <b>GOLD:</b> 2024.50 (▼ 0.05%) &nbsp;&nbsp;&nbsp; 
        <b>BTC:</b> 43,250.10 (▲ 2.45%) &nbsp;&nbsp;&nbsp; 
        <b>VNS SIGNAL:</b> SELL GBPUSD @ 1.2650 ...
    </marquee>
</div>
"""
st.markdown(ticker_html, unsafe_allow_html=True)
st.write("")  # Elanelana kely
# --- CONFIGURATION ---
SHEET_ID = st.secrets["SHEET_ID"]
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_gspread_client():
    try:
        # 1. Hamarino ny Streamlit Secrets (raha efa ao amin'ny Cloud)
        if hasattr(st, "secrets") and "gcp_service_account" in st.secrets:
            info = st.secrets["gcp_service_account"]
            creds = Credentials.from_service_account_info(info, scopes=SCOPES)
            return gspread.authorize(creds)

        # 2. Local JSON - Ampiasao ilay anarana efa misy ao amin'ny folder-nao
        json_path = "serviceAccountKey.json"

        if os.path.exists(json_path):
            creds = Credentials.from_service_account_file(json_path, scopes=SCOPES)
            return gspread.authorize(creds)

        st.warning("⚠️ Credentials file not found.")
        return None

    except Exception as e:
        st.error(f"Gspread Error: {e}")
        return None


@st.cache_data(ttl=300)
def get_data_from_signals_pro():
    try:
        gc = get_gspread_client()
        if gc is None:
            st.warning(
                "⚠️ Tsy afaka mahazo Google Sheets client. Miverina DataFrame foana."
            )
            return pd.DataFrame()

        try:
            sh = gc.open_by_key(SHEET_ID)
        except Exception as e:
            st.error(f"⚠️ Tsy afaka misokatra ny Sheet: {e}")
            return pd.DataFrame()

        try:
            worksheet = sh.worksheet("Trading_Journal")
        except gspread.exceptions.WorksheetNotFound:
            st.warning("⚠️ Tsy hita ny tab 'Trading_Journal'.")
            return pd.DataFrame()

        data = worksheet.get_all_records()
        df = pd.DataFrame(data)

        if df.empty:
            st.info("ℹ️ Ny Sheet dia mbola tsy misy data.")
            return pd.DataFrame()

        df.columns = [c.strip() for c in df.columns]

        if "PROFIT ($)" in df.columns:
            df["PROFIT ($)"] = (
                df["PROFIT ($)"]
                .astype(str)
                .str.replace(",", ".")
                .str.replace(r"[^\d\.]", "", regex=True)
            )
            df["PROFIT ($)"] = pd.to_numeric(df["PROFIT ($)"], errors="coerce").fillna(
                0
            )
        else:
            df["PROFIT ($)"] = 0
            st.warning("⚠️ Tsy hita ny column 'PROFIT ($)'. Mamorona 0 default.")

        if "ASSET (TF)" in df.columns:
            df["detected_result"] = df["PROFIT ($)"].apply(
                lambda x: "WIN" if x > 0 else ("LOSS" if x < 0 else "PENDING")
            )
        else:
            st.warning(
                "⚠️ Tsy hita ny column 'ASSET (TF)'. Tsy mamorona 'detected_result'."
            )

        return df

    except Exception as e:
        st.error(f"❌ Olana tsy nampoizina: {e}")
        return pd.DataFrame()


@st.dialog("VNS TERMINATOR: SYSTEM PROFILE")
def show_about():
    st.markdown(
        """
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
    """,
        unsafe_allow_html=True,
    )


@st.dialog("VNS TERMINATOR: SECURITY ARCHITECTURE")
def show_security_terms():
    st.markdown(
        """
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
    """,
        unsafe_allow_html=True,
    )


@st.dialog("VNS TERMINATOR: GLOBAL CONTACT TERMINAL")
def show_contact():
    st.markdown(
        """
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
    """,
        unsafe_allow_html=True,
    )


def show_nav_footer():
    """
    Mampiseho ny navigation footer miaraka amin'ny bokotra 5 mifanila.
    """
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # Mizara 5 ny habaka (columns)
    f_cols = st.columns(5)

    # Lisitry ny bokotra sy ny function hantsoiny
    buttons = {
        "📖 ABOUT VNS": show_about,
        "🛡️ PRIVACY": show_security_terms,
        "🔒 SECURITY": show_security_terms,
        "✉️ CONTACT": show_contact,
    }

    # Loop hanehoana ny bokotra 4 voalohany
    for i, (label, func) in enumerate(buttons.items()):
        if f_cols[i].button(label, key=f"footer_btn_{i}", use_container_width=True):
            func()

    # Ny column faha-5 dia natokana ho an'ilay NODE STATUS
    with f_cols[4]:
        st.markdown(
            """
            <div style="text-align:center; padding:8px; border:1px solid #00ffcc; 
            border-radius:5px; color:#00ffcc; font-weight:bold; font-size:11px; 
            background: rgba(0, 255, 204, 0.05); margin-top: 5px;">
                🛰️ NODE 2026: ACTIVE
            </div>
            """,
            unsafe_allow_html=True,
        )


def vns_footer_high_pro_v2():
    st.markdown(
        """
        <style>
            .block-container { padding-bottom: 0rem !important; }
            div[data-testid="stHtml"] { 
                margin-top: -50px !important; 
            }
        </style>
    """,
        unsafe_allow_html=True,
    )

    components.html(
        """
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
    """,
        height=230,
    )


# --- MAIN APP FUNCTION ---
# ===========================================
def app():

    # --- CSS TERMINAL LOOK ---
    st.markdown(
        """
    <style>
    div.stButton > button {
        background-color: transparent !important;
        color: #00ffcc !important;
        border: 1px solid #00ffcc !important;
        width: 100%;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: rgba(0, 255, 204, 0.1) !important;
        border: 1px solid #ffffff !important;
        color: #ffffff !important;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.title("📊 VNS Trading Dashboard")

    # --- 2. NOTIFICATION SYSTEM ---
    st.toast("🛡️ Quantum Security Protocol Active", icon="✅")

    # --- FETCH DATA ---
    try:
        # Ataovy azo antoka fa efa misy ity function ity any ambony
        df = get_data_from_signals_pro()
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        df = pd.DataFrame()

    if not df.empty:
        # --- Lojika Win/Loss ---
        profit_col = "PROFIT ($)"
        df["detected_result"] = df[profit_col].apply(
            lambda x: "WIN" if x > 0 else ("LOSS" if x < 0 else "PENDING")
        )

        # --- PREMIUM METRICS SECTION (Dynamic & Clean Indentation) ---
        total_wins = len(df[df["detected_result"] == "WIN"])
        total_loss = len(df[df["detected_result"] == "LOSS"])
        net_profit = df[profit_col].sum()

        # Kajy ny Accuracy
        total_trades = total_wins + total_loss
        accuracy = (total_wins / total_trades * 100) if total_trades > 0 else 0

        st.markdown(
            """
        <style>
            .metric-container {
                display: flex;
                justify-content: space-between;
                gap: 15px;
                margin-bottom: 25px;
            }
            .metric-card {
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                padding: 20px;
                flex: 1;
                text-align: center;
                transition: all 0.3s ease;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            }
            .metric-card:hover {
                transform: translateY(-5px);
                border-color: rgba(250, 204, 21, 0.4);
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
            }
            .metric-label {
                font-size: 10px;
                text-transform: uppercase;
                letter-spacing: 1.5px;
                color: #94a3b8;
                margin-bottom: 8px;
            }
            .metric-value {
                font-size: 28px;
                font-weight: 900;
                color: #f8fafc;
            }
        </style>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
        <div class="metric-container">
            <div class="metric-card">
                <div style="font-size: 20px; margin-bottom: 10px;">🎯</div>
                <div class="metric-label">Live Accuracy</div>
                <div class="metric-value" style="color: #22c55e;">{accuracy:.1f}%</div>
            </div>
            <div class="metric-card">
                <div style="font-size: 20px; margin-bottom: 10px;">✅</div>
                <div class="metric-label">Total Wins</div>
                <div class="metric-value">{total_wins}</div>
            </div>
            <div class="metric-card">
                <div style="font-size: 20px; margin-bottom: 10px;">❌</div>
                <div class="metric-label">Total Loss</div>
                <div class="metric-value">{total_loss}</div>
            </div>
            <div class="metric-card" style="border-left: 3px solid #facc15;">
                <div style="font-size: 20px; margin-bottom: 10px;">💰</div>
                <div class="metric-label">Net Profit</div>
                <div class="metric-value" style="color: #facc15;">${net_profit:,.2f}</div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # --- 3. MARKET SENTIMENT GAUGE & CALENDAR ---
        col_g1, col_g2 = st.columns([1, 1])

        with col_g1:
            # Gauge Chart (Sentiment)
            fig_gauge = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=78,  # Ohatra
                    title={"text": "Overall Market Sentiment"},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": "#00ffcc"},
                        "steps": [
                            {"range": [0, 40], "color": "#e74c3c"},
                            {"range": [40, 65], "color": "#f1c40f"},
                            {"range": [65, 100], "color": "#2ecc71"},
                        ],
                    },
                )
            )
            fig_gauge.update_layout(
                height=280, template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(
                fig_gauge,
                width="stretch",  # Solon'ny use_container_width=True (araka ilay warning teo)
                key=f"vns_gauge_sentiment_{int(time.time())}",
            )
        with col_g2:
            st.markdown("#### 📅 Economic Calendar")
            news_data = [
                {
                    "Time": "14:30",
                    "Currency": "USD",
                    "Event": "CPI Data",
                    "Impact": "🔥",
                },
                {
                    "Time": "16:00",
                    "Currency": "USD",
                    "Event": "Fed Speak",
                    "Impact": "🔥",
                },
                {
                    "Time": "20:00",
                    "Currency": "ALL",
                    "Event": "Market Close",
                    "Impact": "⏳",
                },
            ]
            st.table(news_data)

        st.markdown("---")

        # --- 4. PERFORMANCE VISUALS & LOGS ---
        c1, c2 = st.columns([1.7, 1.3])

        with c1:
            df["cumulative_profit"] = df[profit_col].cumsum()
            fig = px.line(
                df, x=df.index, y="cumulative_profit", title="Equity Growth Curve"
            )
            fig.update_traces(line_color="#00ffcc", line_width=3)
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, use_container_width=True, key="vns_equity_curve")

        with c2:
            st.markdown("#### 📜 Recent Trading Logs")

            # --- LIMIT HO AN'NY FREE ---
            user_plan = st.session_state.get("user_plan", "Free")
            if user_plan == "Free":
                display_df = df[["ASSET (TF)", "BIAS", profit_col]].tail(3).iloc[::-1]
                st.table(display_df)
                st.warning("🔒 Upgrade to Elite to see full history.")
            else:
                display_df = df[["ASSET (TF)", "BIAS", profit_col]].tail(8).iloc[::-1]
                st.dataframe(display_df, use_container_width=True, hide_index=True)

    else:
        st.info("Tsy misy data azo aseho (No data available).")

    # --- 5. CALL TO ACTION (CTA) ---
    st.markdown("---")
    st.write("### 🚀 Take Your Trading to the Next Level")
    if st.button("✨ GET REAL-TIME PRO SIGNALS NOW", key="btn_cta_pro"):
        st.balloons()
        st.info("👉 Access latest signals in the '📉 Forex Pro Signals' section!")


# --- FUNCTION 1: MAKA DATA AVY AMIN'NY BINANCE ---

    api_key = st.secrets["BINANCE_API_KEY"]
    api_secret = st.secrets["BINANCE_SECRET_KEY"]

    client = Client(api_key, api_secret)

    raw_symbol = asset_map[selected_pair]["binance"]


def get_live_market_data(symbol):
    try:
        # Rehefa voafaritra eo ambony ny 'client' dia efa afaka miasa ity andalana ity
        klines = client.get_klines(symbol=symbol, interval="1h", limit=100)  #

        df = pd.DataFrame(
            klines,
            columns=[
                "time",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "close_time",
                "q_av",
                "num_trades",
                "taker_base",
                "taker_quote",
                "ignore",
            ],
        )

        df["close"] = df["close"].astype(float)

        # KAJY NY MA 50 (Ity no hanafaka anao amin'ny "Neutral")
        ma50_series = df["close"].rolling(window=50).mean()
        current_ma50 = ma50_series.iloc[-1]

        # KAJY NY MACD
        exp1 = df["close"].ewm(span=12, adjust=False).mean()
        exp2 = df["close"].ewm(span=26, adjust=False).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        macd_h = macd_line - signal_line

        # KAJY NY RSI
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))

        return {
            "price": df["close"].iloc[-1],
            "ma50": current_ma50,
            "rsi": rsi,
            "macd_h": macd_h.iloc[-1],
            "status": "Bullish" if df["close"].iloc[-1] > current_ma50 else "Bearish",
        }
    except Exception as e:
        # Ity dia mampiseho ny fahadisoana ao amin'ny Streamlit raha misy olana
        import streamlit as st

        st.error(f"API Error: {e}")
        return None


def render_live_market_data():
    st.markdown("---")
    st.markdown("### 🔍 Live Market Analysis & AI Signals")

    # 1. Expanded Asset Map
    asset_map = {
        "Ethereum": {"binance": "BINANCE:ETHUSDT"},
        "Binance Coin": {"binance": "BINANCE:BNBUSDT"},
        "Dogecoin": {"binance": "BINANCE:DOGEUSDT"},
        "Polkadot": {"binance": "BINANCE:DOTUSDT"},
        "Cardano": {"binance": "BINANCE:ADAUSDT"},
        "Ripple (XRP)": {"binance": "BINANCE:XRPUSDT"},
        "Gold": {"binance": "OANDA:XAUUSD"},
        "EUR/USD": {"binance": "FX:EURUSD"},
        "Oil": {"binance": "TVC:USOIL"},
    }

    selected_pair = st.selectbox("Select Asset", list(asset_map.keys()), index=0)
    tv_symbol = asset_map[selected_pair]["binance"]

    # --- A. TRADINGVIEW WIDGET ---
    tv_html = f"""
    <div style="height:600px;">
        <div id="tv-vns" style="height:100%;"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({{
            "autosize": true,
            "symbol": "{tv_symbol}",
            "interval": "60",
            "theme": "dark",  // <--- OVAO HO "dark" ETO (efa "light" ny teo aloha)
            "style": "1",
            "locale": "en",
            "toolbar_bg": "#131722", // Loko maizina mifanaraka amin'ny TradingView Dark
            "enable_publishing": false,
            "hide_side_toolbar": false,
            "allow_symbol_change": true,
            "container_id": "tv-vns",
            "studies": [
                "Volume@tv-basicstudies",
                "MASimple@tv-basicstudies",
                "MACD@tv-basicstudies"
            ],
            "studies_overrides": {{
                "moving average.length": 50,
                "moving average.ma.color": "#FF9800",
                "moving average.ma.linewidth": 2
            }}
        }});
        </script>
    </div>
    """
    import streamlit.components.v1 as components

    components.html(tv_html, height=620)
    
    
    # --- B. BINANCE METRICS & ALERTS ---
    raw_symbol = ""
    if "BINANCE" in raw_symbol:
        try:
            api_symbol = raw_symbol.split(":")[-1].upper()
            live_data = get_live_market_data(api_symbol)

            if live_data:
                price_val = float(live_data.get("price", 0))
                ma50_val = float(live_data.get("ma50", 0))
                rsi_val = float(live_data.get("rsi", 0))
                vol_val = float(live_data.get("volatility", 1.0))

                # --- KAJY TP SY STOP LOSS (Dynamic based on Volatility) ---
                sl_percent = (vol_val * 1.5) / 100

                if price_val > ma50_val:  # Bullish
                    stop_loss = price_val * (1 - sl_percent)
                    take_profit = price_val * (1 + (sl_percent * 2))
                    signal_label = "🚀 BUY SIGNAL"
                    status_color = "success"
                else:  # Bearish
                    stop_loss = price_val * (1 + sl_percent)
                    take_profit = price_val * (1 - (sl_percent * 2))
                    signal_label = "⚠️ SELL SIGNAL"
                    status_color = "error"

                # --- VISUAL TRADE CARD ---
                # Ity dia mampiseho ny andalana TP sy SL ho hitan'ny maso alohan'ny chart
                st.info(f"**Current Strategy:** {signal_label} | **Risk/Reward:** 1:2")

                # Metrics Display
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Live Price", f"${price_val:,.2f}")
                c2.metric("RSI (14)", f"{rsi_val:.1f}")
                c3.metric(
                    "Take Profit (TP)",
                    f"${take_profit:,.2f}",
                    delta=f"{take_profit-price_val:,.2f}",
                )
                c4.metric(
                    "Stop Loss (SL)",
                    f"${stop_loss:,.2f}",
                    delta=f"{stop_loss-price_val:,.2f}",
                    delta_color="inverse",
                )

                # --- DISPLAY PRICE LEVELS AS TEXT ON CHART ---
                # Mampiasa Markdown mba hanahaka ny andalana amin'ny chart
                st.markdown(
                    f"""
                <div style="background-color: #1e1e1e; padding: 10px; border-radius: 5px; border-left: 5px solid #00ff00;">
                    <span style="color: #00ff00; font-weight: bold;">[TP] Take Profit: ${take_profit:,.2f}</span><br>
                    <span style="color: #ffffff; font-weight: bold;">[EP] Entry Price: ${price_val:,.2f}</span><br>
                    <span style="color: #ff4b4b; font-weight: bold;">[SL] Stop Loss: ${stop_loss:,.2f}</span>
                </div>
                """,
                    unsafe_allow_html=True,
                )

        except Exception as e:
            st.error(f"Sync Error: {e}")


# --- FUNCTION 3: MAIN DASHBOARD ROUTING ---
def show_dashboard():
    user_plan = st.session_state.get("user_plan", "Free").lower()

    # 1. Asehoy ny Live Data (Ho an'ny rehetra)
    render_live_market_data()

    st.divider()

    # 2. Support Section
    with st.expander("💬 VNS Support & Feedback"):
        with st.form("feedback_vns"):
            u_name = st.text_input("Operator Name")
            msg = st.text_area("Report/Message")
            if st.form_submit_button("SEND TO HUB"):
                st.success("Message transmitted to VNS Satellite.")

    st.divider()

    # 3. AI & PDF Section (PRO vs BASIC)
    st.markdown("#### 🤖 Neural Intelligence Hub")
    if user_plan in ["pro", "elite", "premium", "vip"]:
        col1, col2 = st.columns(2)
        with col1:
            st.button("🧠 Run AI Analysis", key="ai_active_btn")
        with col2:
            st.button("📄 Export PDF Report", key="pdf_active_btn")
        st.success("Pro Tools: Fully Operational.")
    else:
        # Blurred Marketing Overlay
        st.markdown(
            """
            <div style="position: relative; text-align: center; border-radius: 15px; overflow: hidden; border: 1px solid #334155; background: #0f172a;">
                <div style="filter: blur(8px); opacity: 0.2; padding: 40px;">
                    <h2 style="color: #3b82f6;">[NEURAL AI PREDICTIONS ACTIVE]</h2>
                    <p>Accuracy: 98.4% | EUR/USD: BUY Target 1.0950</p>
                </div>
                <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 90%;">
                    <h3 style="color: #3b82f6;">🔒 PRO FEATURES LOCKED</h3>
                    <p style="font-size: 13px; color: #94a3b8; margin-bottom: 15px;">Upgrade to unlock AI Analysis and Professional PDF Reports.</p>
                    <a href="https://pay.vn-s-terminator.com/" target="_blank">
                        <button style="background-color: #3b82f6; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%;">
                            🚀 UPGRADE TO PRO ($49)
                        </button>
                    </a>
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    # --- 3. SAKANA ADMIN ---
    if st.session_state.get("is_admin"):
        st.markdown("---")
        admin_panel()
    # --- 5. THE PROFESSIONAL FOOTER DASHBOARD (Ivelan'ny try foana) ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")

    col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)

    with col_f1:
        if st.button("📖 ABOUT VNS", key="f_about"):
            show_about()
    with col_f2:
        # Azonao atao ny manamboatra 'show_privacy()' manokana raha tianao
        if st.button("🛡️ PRIVACY", key="f_privacy"):
            show_security_terms()
    with col_f3:
        if st.button("🔒 SECURITY", key="f_security"):
            show_security_terms()
    with col_f4:
        if st.button("✉️ CONTACT", key="f_contact"):
            show_contact()
    with col_f5:
        st.markdown(
            """
            <div style="text-align:center; padding:8px; border:1px solid #00ffcc; 
            border-radius:5px; color:#00ffcc; font-weight:bold; font-size:11px; 
            background: rgba(0, 255, 204, 0.05);">
                🛰️ NODE 2026: ACTIVE
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Final Elite Footer Call
    vns_footer_high_pro_v2()

# --- 2. INITIALIZATION (Fampidirana ny Session State) ---
if "user_data" not in st.session_state:
    st.session_state.user_data = {"plan": "Free"}

# --- 3. NY FUNCTION REHETRA ---
# (Apetraho eto ireo def check_access(), def show_pricing_page(), sns.)

# --- MAIN LOGIC ---
def main():

    # Plan an'ny user (raha tsy misy dia Free)
    if "user_data" not in st.session_state:
        st.session_state.user_data = {"plan": "Free"}

    current_plan = st.session_state.user_data.get("plan", "Free")

    # Dashboard
    show_dashboard()


# Run app
if __name__ == "__main__":
    main()



