import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. APP CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(page_title="UniAlgo Scanner", page_icon="📈", layout="centered")

st.markdown("""
<style>
    .trade-card {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin-bottom: 10px;
    }
    .watchlist-card {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FFC107;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 Major Market Scanner")
st.caption("S&P 100 (US) + TSX 60 (Canada) | Daily Timeframe")

# -----------------------------------------------------------------------------
# 2. TICKER UNIVERSE (Hardcoded for Stability)
# -----------------------------------------------------------------------------
# We use lists here to avoid external dependency failures on mobile

SP100_US = [
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "GOOG", "META", "TSLA", "BRK-B", "UNH",
    "JNJ", "XOM", "V", "PG", "JPM", "MA", "HD", "CVX", "MRK", "ABBV", "PEP", "KO",
    "LLY", "BAC", "AVGO", "COST", "TMO", "MCD", "CSCO", "CRM", "PFE", "ACN", "DHR",
    "LIN", "NFLX", "ABT", "AMD", "DIS", "WMT", "TXN", "NEE", "PM", "BMY", "ADBE",
    "CMCSA", "NKE", "VZ", "RTX", "UPS", "MS", "HON", "AMGN", "INTC", "UNP", "LOW",
    "QCOM", "IBM", "SPGI", "INTU", "CAT", "GS", "DE", "GE", "LMT", "PLD", "BLK",
    "EL", "SCHW", "BKNG", "AMAT", "ADI", "MDLZ", "TJX", "ADP", "MMC", "GILD", "C",
    "ISRG", "SYK", "VRTX", "TMUS", "NOW", "ZTS", "BA", "PGR", "T", "CB", "REGN",
    "SO", "MO", "CI", "BDX", "LRCX", "FISV", "EOG", "BSX", "SLB"
]

TSX60_CA = [
    "RY.TO", "TD.TO", "CNR.TO", "CP.TO", "ENB.TO", "BNS.TO", "CNQ.TO", "BMO.TO",
    "ATD.TO", "TRI.TO", "CSU.TO", "TRP.TO", "SHOP.TO", "BCE.TO", "CM.TO", "NTR.TO",
    "SU.TO", "MG.TO", "MFC.TO", "WCN.TO", "QSR.TO", "IMO.TO", "FNV.TO", "POW.TO",
    "DOL.TO", "T.TO", "RCI-B.TO", "GIB-A.TO", "WCP.TO", "SLF.TO", "AEM.TO", "NA.TO",
    "FM.TO", "FTS.TO", "CVE.TO", "K.TO", "WPM.TO", "MRU.TO", "OTEX.TO", "EMA.TO",
    "PPL.TO", "TECK-B.TO", "CAR-UN.TO", "CCO.TO", "SAP.TO", "WN.TO", "CL.TO",
    "IFC.TO", "CTC-A.TO", "AQN.TO", "GRT-UN.TO", "KEY.TO", "CAE.TO", "GIL.TO",
    "L.TO", "BIP-UN.TO", "BEP-UN.TO", "H.TO", "FSV.TO"
]

# Sidebar Controls
with st.sidebar:
    st.header("Scan Settings")
    market_choice = st.radio("Select Market:", ["All", "US (S&P 100)", "Canada (TSX 60)"])
    lookback = st.slider("Data Lookback (Years)", 1, 3, 2)
    
    # Determine which list to use
    if market_choice == "US (S&P 100)":
        TICKERS = SP100_US
    elif market_choice == "Canada (TSX 60)":
        TICKERS = TSX60_CA
    else:
        TICKERS = SP100_US + TSX60_CA

    st.write(f"Scanning **{len(TICKERS)}** stocks.")

# -----------------------------------------------------------------------------
# 3. TECHNICAL INDICATORS
# -----------------------------------------------------------------------------
def calculate_indicators(df):
    df = df.copy()
    
    # SMA 200 (Trend)
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    
    # EMA 20 (Pullback)
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    
    # RSI 14 (Momentum)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # ATR 14 (Risk)
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    df['ATR'] = true_range.rolling(window=14).mean()
    
    # ADX 14 (Trend Strength)
    plus_dm = df['High'].diff()
    minus_dm = df['Low'].diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0
    
    plus_di = 100 * (plus_dm.ewm(alpha=1/14).mean() / df['ATR'])
    minus_di = 100 * (np.abs(minus_dm).ewm(alpha=1/14).mean() / df['ATR'])
    dx = (np.abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    df['ADX'] = dx.rolling(window=14).mean()
    
    return df

# -----------------------------------------------------------------------------
# 4. STRATEGY ENGINE
# -----------------------------------------------------------------------------
def check_strategy(ticker, df):
    if len(df) < 205: return None
        
    curr = df.iloc[-1]
    prev = df.iloc[-2]
    
    # Logic Gates
    # 1. Trend: Above 200 SMA & ADX > 15
    is_uptrend = (curr['Close'] > curr['SMA_200']) and (curr['ADX'] > 15)
    
    # 2. Setup: Price near EMA 20 (within 2.5%) & RSI < 60 (Not overbought)
    dist_to_ema = (curr['Close'] - curr['EMA_20']) / curr['EMA_20']
    is_pullback = (abs(dist_to_ema) < 0.025) and (curr['RSI'] < 60)
    
    # 3. Trigger: Close > Prev High OR Green Candle
    is_trigger = (curr['Close'] > prev['High']) or (curr['Close'] > curr['Open'])
    
    # Volume check
    avg_vol = df['Volume'].rolling(20).mean().iloc[-1]
    # Handle zero volume edge cases
    vol_valid = True
    if avg_vol > 0:
        vol_valid = curr['Volume'] > (avg_vol * 0.7) # Slightly looser for demo

    status = "WAIT"
    reason = ""
    
    if is_uptrend:
        if is_pullback:
            if is_trigger and vol_valid:
                status = "BUY"
                reason = "Trend + Pullback + Trigger"
            else:
                status = "WATCH"
                reason = "Valid Setup (Waiting for Trigger)"
        else:
            status = "TREND"
    else:
        status = "AVOID"

    if status in ["BUY", "WATCH"]:
        stop = curr['Close'] - (2 * curr['ATR'])
        target = curr['Close'] + (3 * curr['ATR'])
        return {
            "Ticker": ticker, "Status": status, "Price": curr['Close'],
            "Stop": stop, "Target": target, "RSI": curr['RSI'], 
            "Reason": reason
        }
    return None

# -----------------------------------------------------------------------------
# 5. MAIN EXECUTION
# -----------------------------------------------------------------------------
if st.button("🚀 Run Large Cap Scan"):
    
    st.write(f"Fetching data for {len(TICKERS)} tickers. Please wait...")
    progress_bar = st.progress(0)
    results = []
    
    # Loop through tickers
    for i, ticker in enumerate(TICKERS):
        try:
            # Optimize: Get less history to speed up large lists
            df = yf.download(ticker, period="1y", interval="1d", progress=False, auto_adjust=True)
            
            if not df.empty:
                df = calculate_indicators(df)
                sig = check_strategy(ticker, df)
                if sig:
                    results.append(sig)
        except:
            pass
        
        # Update progress bar
        progress_bar.progress((i + 1) / len(TICKERS))
    
    progress_bar.empty()
    
    if not results:
        st.info("No signals found in this list right now.")
    else:
        st.success(f"Scan Complete: {len(results)} Opportunities")
        results.sort(key=lambda x: x['Status'])
        
        for res in results:
            css = "trade-card" if res['Status'] == "BUY" else "watchlist-card"
            emoji = "🟢" if res['Status'] == "BUY" else "👀"
            
            st.markdown(f"""
            <div class="{css}">
                <h3 style="margin:0; color:white;">{emoji} {res['Ticker']} <span style="font-size:0.7em; color:#bbb;">${res['Price']:.2f}</span></h3>
                <p style="margin:5px 0; color:#ddd;"><b>Signal:</b> {res['Status']} | <b>RSI:</b> {res['RSI']:.0f}</p>
                <p style="margin:0; color:#aaa; font-size:0.9em;">{res['Reason']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander(f"Analysis for {res['Ticker']}"):
                c1, c2 = st.columns(2)
                c1.metric("Stop Loss", f"${res['Stop']:.2f}")
                c2.metric("Target", f"${res['Target']:.2f}")
                
                # Plot
                try:
                    df_chart = yf.download(res['Ticker'], period="6mo", interval="1d", progress=False, auto_adjust=True)
                    fig = go.Figure(data=[go.Candlestick(x=df_chart.index,
                            open=df_chart['Open'], high=df_chart['High'],
                            low=df_chart['Low'], close=df_chart['Close'])])
                    fig.update_layout(height=300, margin=dict(t=0,b=0,l=0,r=0), template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                except:
                    st.write("Chart Error")

