
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

# -----------------------------------------------------------------------------
# 1. APP CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(page_title="UniAlgo Maximum", page_icon="⚡", layout="wide")

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

st.title("⚡ Algo Scanner (Batch Mode)")
st.caption("Processes stocks in chunks to prevent memory crashes on mobile.")

# -----------------------------------------------------------------------------
# 2. TICKER SOURCES (Dynamic & Manual)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("Universe Settings")
    
    # Preset Lists
    use_sp500 = st.checkbox("Include S&P 500 (US)", value=True)
    use_tsx = st.checkbox("Include TSX 60 (Canada)", value=True)
    
    # Custom Input for massive lists
    st.markdown("### Add Custom Tickers")
    custom_text = st.text_area("Paste list here (comma or space separated)", height=100)
    
    # Batch Size Control
    chunk_size = st.slider("Batch Size (Lower = Safer)", 100, 500, 300)

def get_tickers():
    tickers = []
    
    # 1. Hardcoded Fallback (TSX 60) - Reliable
    if use_tsx:
        tsx_tickers = [
            "RY.TO", "TD.TO", "CNR.TO", "CP.TO", "ENB.TO", "BNS.TO", "CNQ.TO", "BMO.TO",
            "ATD.TO", "TRI.TO", "CSU.TO", "TRP.TO", "SHOP.TO", "BCE.TO", "CM.TO", "NTR.TO",
            "SU.TO", "MG.TO", "MFC.TO", "WCN.TO", "QSR.TO", "IMO.TO", "FNV.TO", "POW.TO",
            "DOL.TO", "T.TO", "RCI-B.TO", "GIB-A.TO", "WCP.TO", "SLF.TO", "AEM.TO", "NA.TO",
            "FM.TO", "FTS.TO", "CVE.TO", "K.TO", "WPM.TO", "MRU.TO", "OTEX.TO", "EMA.TO"
        ]
        tickers.extend(tsx_tickers)

    # 2. Dynamic Fetch (S&P 500) - Tries to fetch from web, falls back if fails
    if use_sp500:
        try:
            # Efficiently read S&P 500 from Wikipedia
            payload = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
            sp500_tickers = payload[0]['Symbol'].values.tolist()
            # Fix formatting (BRK.B -> BRK-B)
            sp500_tickers = [x.replace('.', '-') for x in sp500_tickers]
            tickers.extend(sp500_tickers)
        except:
            st.error("Could not fetch S&P 500 from Wikipedia. Using limited backup.")
            # Backup list of top 20 US stocks
            tickers.extend(["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META"])

    # 3. Custom User Input
    if custom_text:
        # Clean string: replace newlines/commas with spaces, then split
        cleaned = custom_text.replace(",", " ").replace("\n", " ")
        custom_list = [t.strip().upper() for t in cleaned.split(" ") if t.strip()]
        tickers.extend(custom_list)
        
    return list(set(tickers)) # Remove duplicates

# -----------------------------------------------------------------------------
# 3. STRATEGY LOGIC
# -----------------------------------------------------------------------------
def analyze_dataframe(ticker, df):
    # Strategy Logic (Same as before)
    if len(df) < 205: return None
    curr = df.iloc[-1]
    prev = df.iloc[-2]
    
    # Indicators
    sma200 = df['Close'].rolling(200).mean().iloc[-1]
    ema20 = df['Close'].ewm(span=20).mean().iloc[-1]
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs)).iloc[-1]
    
    # ATR & ADX logic omitted for brevity in batch processing, 
    # using simplified Volatility check
    atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
    
    # --- GATES ---
    is_uptrend = (curr['Close'] > sma200)
    
    # Pullback: Price within 3% of EMA20
    dist = (curr['Close'] - ema20) / ema20
    is_pullback = (abs(dist) < 0.03) and (rsi < 60)
    
    is_trigger = (curr['Close'] > prev['High'])
    
    status = None
    if is_uptrend and is_pullback:
        if is_trigger:
            status = "BUY"
            reason = "Trend + Pullback + Trigger"
        else:
            status = "WATCH"
            reason = "Waiting for Trigger"
            
    if status:
        return {
            "Ticker": ticker, "Status": status, "Price": curr['Close'],
            "Stop": curr['Close'] - (2*atr), "Target": curr['Close'] + (3*atr),
            "Reason": reason
        }
    return None

# -----------------------------------------------------------------------------
# 4. BATCH PROCESSOR
# -----------------------------------------------------------------------------
if st.button("🚀 Run Mega-Scan"):
    
    all_tickers = get_tickers()
    total_stocks = len(all_tickers)
    
    st.write(f"Preparing to scan {total_stocks} stocks in batches of {chunk_size}...")
    master_progress = st.progress(0)
    results = []
    
    # CHUNKING LOGIC
    # Range(start, stop, step) -> 0, 300, 600...
    for i in range(0, total_stocks, chunk_size):
        
        # 1. Slice the list
        batch = all_tickers[i : i + chunk_size]
        st.caption(f"Processing Batch {i} to {i+len(batch)}...")
        
        try:
            # 2. Download Batch (Fast)
            data = yf.download(batch, period="1y", group_by='ticker', progress=False, threads=True, auto_adjust=True)
            
            # 3. Process Batch
            for ticker in batch:
                try:
                    # Handle MultiIndex vs Single Index
                    if len(batch) > 1:
                        df = data[ticker].dropna()
                    else:
                        df = data.dropna() # If only 1 stock in list
                        
                    if not df.empty:
                        sig = analyze_dataframe(ticker, df)
                        if sig: results.append(sig)
                except:
                    continue
                    
        except Exception as e:
            st.error(f"Batch failed: {e}")
            
        # Update Progress
        master_progress.progress(min((i + chunk_size) / total_stocks, 1.0))
        
        # 4. Memory Management: Pause briefly to let API cool down
        time.sleep(1)

    master_progress.empty()
    
    # --- RESULTS ---
    if results:
        st.success(f"Scan Complete! Found {len(results)} setups.")
        results.sort(key=lambda x: x['Status'])
        
        # Grid Display
        c1, c2 = st.columns(2)
        for idx, res in enumerate(results):
            css = "trade-card" if res['Status'] == "BUY" else "watchlist-card"
            html = f"""
            <div class="{css}">
                <b>{res['Status']} {res['Ticker']}</b><br>
                <span style="color:#ccc">${res['Price']:.2f}</span>
            </div>
            """
            with (c1 if idx % 2 == 0 else c2):
                st.markdown(html, unsafe_allow_html=True)
                with st.expander("Details"):
                    st.write(f"Stop: {res['Stop']:.2f}")
                    st.write(f"Target: {res['Target']:.2f}")
    else:
        st.warning("No setups found.")
