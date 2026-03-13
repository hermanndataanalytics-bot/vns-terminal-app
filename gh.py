import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from google import genai
import time

st.set_page_config(page_title="Trading Signals Dashboard", layout="wide")
st.title("📊 Professional Trading Signals Dashboard")

# === API KEY Gemini ===
api_key = st.secrets.get("FOREX_GENAI_KEY")
if not api_key:
    st.error("❌ API key not found in st.secrets")
else:
    client = genai.Client(api_key=api_key.strip())
    st.success("✅ Gemini GenAI Connected")

# === Multiple tickers input ===
tickers_input = st.text_input("Enter tickers (comma-separated):", "AAPL,MSFT,GOOGL")
tickers = [t.strip().upper() for t in tickers_input.split(",")]

# === Parameters for signals ===
ma_short = st.slider("MA Short Period", 5, 20, 10)
ma_long = st.slider("MA Long Period", 20, 50, 20)
rsi_period = st.slider("RSI Period", 5, 30, 14)

# === Process each ticker ===
for ticker in tickers:
    st.subheader(f"📈 {ticker}")
    
    # Download historical data
    df = yf.download(ticker, period="1mo", interval="1h")
    if df.empty:
        st.warning("No data found")
        continue
    
    # === Calculate signals ===
    df['MA_short'] = df['Close'].rolling(ma_short).mean()
    df['MA_long'] = df['Close'].rolling(ma_long).mean()
    
    # Simple MA Crossover
    df['Signal'] = 0
    df.loc[df['MA_short'] > df['MA_long'], 'Signal'] = 1  # Buy
    df.loc[df['MA_short'] < df['MA_long'], 'Signal'] = -1  # Sell
    
    # Optional: RSI
    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(rsi_period).mean()
    avg_loss = loss.rolling(rsi_period).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # === Display last 10 rows ===
    st.dataframe(df[['Close','MA_short','MA_long','RSI','Signal']].tail(10))
    
    # === Chart with signals ===
    plt.figure(figsize=(10,4))
    plt.plot(df['Close'], label='Close')
    plt.plot(df['MA_short'], label=f'MA{ma_short}')
    plt.plot(df['MA_long'], label=f'MA{ma_long}')
    buys = df[df['Signal']==1]['Close']
    sells = df[df['Signal']==-1]['Close']
    plt.scatter(buys.index, buys.values, marker='^', color='g', label='Buy')
    plt.scatter(sells.index, sells.values, marker='v', color='r', label='Sell')
    plt.legend()
    st.pyplot(plt)
    
    # === AI Explanation for last signal ===
    last_signal = df['Signal'].iloc[-1]
    signal_text = "Buy" if last_signal==1 else "Sell" if last_signal==-1 else "Hold"
    prompt = f"Explain this trading signal ({signal_text}) for {ticker} in simple words."
    
    st.subheader("🤖 AI Explanation")
    output_box = st.empty()
    explanation = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    ).text
    
    # Pseudo-streaming
    text_so_far = ""
    for word in explanation.split():
        text_so_far += word + " "
        output_box.text(text_so_far)
        time.sleep(0.03)
    
    st.download_button(
        label=f"📄 Download Explanation for {ticker}",
        data=explanation,
        file_name=f"{ticker}_signal_explanation.txt",
        mime="text/plain"
    )
