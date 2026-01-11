import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime

# -----------------------------------------------------------------------------
# 1. APP CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(page_title="UniAlgo Ultimate", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    .stExpander {
        background-color: #262730;
        border-radius: 10px;
    }
    .metric-card {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #444;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ UniAlgo: Multi-Timeframe System")
st.caption("Daily Swing | Weekly Investing | **NEW: Deep Value (TSX/TSX.V)**")

# -----------------------------------------------------------------------------
# 2. TICKER UNIVERSE (S&P 500 + TSX 60 + TSX VENTURE)
# -----------------------------------------------------------------------------

TSX_TICKERS = [
    "RY.TO", "TD.TO", "CNR.TO", "CP.TO", "ENB.TO", "BNS.TO", "CNQ.TO", "BMO.TO",
    "ATD.TO", "TRI.TO", "CSU.TO", "TRP.TO", "SHOP.TO", "BCE.TO", "CM.TO", "NTR.TO",
    "SU.TO", "MG.TO", "MFC.TO", "WCN.TO", "QSR.TO", "IMO.TO", "FNV.TO", "POW.TO",
    "DOL.TO", "T.TO", "RCI-B.TO", "GIB-A.TO", "WCP.TO", "SLF.TO", "AEM.TO", "NA.TO",
    "FM.TO", "FTS.TO", "CVE.TO", "K.TO", "WPM.TO", "MRU.TO", "OTEX.TO", "EMA.TO",
    "PPL.TO", "TECK-B.TO", "CAR-UN.TO", "CCO.TO", "SAP.TO", "WN.TO", "CL.TO",
    "IFC.TO", "CTC-A.TO", "AQN.TO", "GRT-UN.TO", "KEY.TO", "CAE.TO", "GIL.TO",
    "L.TO", "BIP-UN.TO", "BEP-UN.TO", "H.TO", "FSV.TO"
]

# Major TSX Venture Stocks (Manual Selection for speed)
TSXV_TICKERS = [
    "HIVE.V", "BITF.V", "TOI.V", "FOM.V", "NFG.V", "SKE.V", "ISO.V", "LI.V", 
    "PMET.V", "EU.V", "VZLA.V", "NFG.V", "RECO.V", "GBR.V", "VPT.V", "FD.V"
]

US_TICKERS = [
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "GOOG", "TSLA", "BRK-B", "UNH", 
    "JNJ", "XOM", "V", "PG", "MA", "JPM", "HD", "CVX", "MRK", "ABBV", "PEP", "KO", 
    "LLY", "BAC", "AVGO", "COST", "TMO", "MCD", "CSCO", "CRM", "PFE", "ACN", "DHR", 
    "LIN", "NFLX", "ABT", "AMD", "DIS", "WMT", "TXN", "NEE", "PM", "BMY", "ADBE", 
    "CMCSA", "NKE", "VZ", "RTX", "UPS", "MS", "HON", "AMGN", "INTC", "UNP", "LOW", 
    "QCOM", "IBM", "SPGI", "INTU", "CAT", "GS", "DE", "GE", "LMT", "PLD", "BLK", 
    "EL", "SCHW", "BKNG", "AMAT", "ADI", "MDLZ", "TJX", "ADP", "MMC", "GILD", "C", 
    "ISRG", "SYK", "VRTX", "TMUS", "NOW", "ZTS", "BA", "PGR", "T", "CB", "REGN", 
    "SO", "MO", "CI", "BDX", "LRCX", "FISV", "EOG", "BSX", "SLB", "ITW", "CL", 
    "APD", "ATVI", "CSX", "CCI", "ETN", "HUM", "WM", "NOC", "TGT", "FDX", "NSC", 
    "GD", "ICE", "SHW", "MCO", "USB", "GM", "KLAC", "MCK", "PNC", "EMR", "ORCL", 
    "F", "AON", "ECL", "MDT", "HCA", "FCX", "NXPI", "MAR", "ROP", "PSX", "APH", 
    "PCAR", "COF", "VLO", "MNST", "SNPS", "MSI", "AIG", "OXY", "ROST", "DXCM", 
    "AZO", "MET", "AEP", "TRV", "SRE", "TEL", "D", "PSA", "IDXX", "PH", "KMB", 
    "JCI", "CHTR", "ALL", "CTAS", "WMB", "AFL", "ADSK", "PAYX", "EXC", "DLR", 
    "BIIB", "O", "STZ", "FIS", "EW", "EA", "GPN", "HLT", "CMG", "XEL", "ELV", 
    "CTVA", "KR", "YUM", "KMI", "WBA", "PRU", "SYY", "DVN", "LHX", "CNC", "NEM", 
    "CMI", "OTIS", "VRSK", "DD", "HPQ", "FAST", "CSGP", "WEC", "SBAC", "HES", 
    "ANET", "KEYS", "DLTR", "CPRT", "ROK", "PEG", "AMP", "BKR", "PPG", "ES", 
    "ED", "AWK", "APTV", "GLW", "MTD", "ULTA", "EFX", "TROW", "HSY", "EIX", 
    "CBRE", "ARE", "VRSN", "EBAY", "ZBH", "ALB", "TSCO", "DFS", "HIG", "WBD", 
    "FE", "AME", "MTB", "OKE", "IFF", "WY", "KHC", "RMD", "BAX", "STT", "CDW", 
    "HAL", "ETR", "GWW", "AJG", "RJF", "DAL", "IR", "FANG", "ON", "MCHP", 
    "LYB", "VTR", "LUV", "NVR", "WTW", "IT", "DHI", "TSN", "HBAN", "XYL", 
    "FSLR", "GPC", "VICI", "WAB", "CINF", "DOV", "MLM", "GRMN", "EXR", "OMC", 
    "BBY", "HPE", "TTWO", "CNP", "VMC", "CAG", "TER", "INGR", "KEY", "RF", 
    "CMS", "PFG", "STE", "WAT", "CF", "NTAP", "AES", "FMC", "TYL", "DGX", 
    "PKI", "EXPD", "IEX", "AVY", "CBOE", "DRI", "MKC", "ATO", "TXT", "SJM", 
    "BWA", "HOLX", "ABMD", "COO", "JBHT", "ESS", "WST", "LNT", "MAA", "NDSN", 
    "AKAM", "DG", "POOL", "TRMB", "ALGN", "CE", "MAS", "SNA", "SWK", "UDR", 
    "HST", "K", "INCY", "MGM", "O", "PHM", "PKG", "RL", "ROL", "SWKS", "UHS", 
    "URI", "VFC", "WHR", "WRB", "XRAY", "ZION", "A", "AAL", "AAP", "AES", 
    "ALK", "APA", "BXP", "CPB", "CRL", "DISH", "DVA", "EMN", "EVRG", "FFIV", 
    "FRT", "GNRC", "HAS", "HSIC", "IP", "IPG", "IVZ", "JNPR", "KMX", "LKQ", 
    "LNC", "LVS", "MHK", "MOH", "MOS", "NCLH", "NI", "NRG", "NWS", "NWSA", 
    "OGN", "PARA", "PEAK", "PNR", "PNW", "PVH", "QRVO", "RCL", "REG", "RHI", 
    "SEE", "SIVB", "SPG", "TPR", "UAA", "UA", "UAL", "UDR", "UHS", "ULTA", 
    "UNM", "URI", "USB", "VFC", "VICI", "VNO", "VRSK", "VTRS", "WAB", "WAT", 
    "WBA", "WBD", "WDC", "WEC", "WELL", "WFC", "WHR", "WMB", "WRB", "WRK", 
    "WST", "WY", "WYNN", "XEL", "XYL", "YUM", "ZBRA", "ZBH", "ZION", "ZTS"
]

ALL_TICKERS = TSX_TICKERS + TSXV_TICKERS + US_TICKERS

# -----------------------------------------------------------------------------
# 3. DATA & INDICATORS
# -----------------------------------------------------------------------------

@st.cache_data(ttl=3600)
def fetch_data():
    return yf.download(ALL_TICKERS, period="2y", group_by='ticker', auto_adjust=True, threads=True)

# DAILY INDICATORS
def calculate_daily_indicators(df):
    if df.empty or len(df) < 205: return df
    df = df.copy()
    
    # Moving Averages
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    
    # 52 Week High (For Deep Value Logic)
    df['52W_High'] = df['Close'].rolling(window=252).max()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # ATR & ADX
    high_low = df['High'] - df['Low']
    true_range = np.maximum(high_low, np.abs(df['High'] - df['Close'].shift()))
    df['ATR'] = true_range.rolling(window=14).mean()
    df['ADX'] = df['ATR'].rolling(14).mean() 
    return df

# WEEKLY INDICATORS
def convert_and_calculate_weekly(df_daily):
    if df_daily.empty: return None
    df_weekly = df_daily.resample('W-FRI').agg({
        'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
    }).dropna()
    
    if len(df_weekly) < 60: return None
    
    df_weekly['SMA_50'] = df_weekly['Close'].rolling(window=50).mean()
    df_weekly['EMA_20'] = df_weekly['Close'].ewm(span=20, adjust=False).mean()
    
    delta = df_weekly['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df_weekly['RSI'] = 100 - (100 / (1 + rs))
    
    high_low = df_weekly['High'] - df_weekly['Low']
    true_range = np.maximum(high_low, np.abs(df_weekly['High'] - df_weekly['Close'].shift()))
    df_weekly['ATR'] = true_range.rolling(14).mean()
    
    return df_weekly

# -----------------------------------------------------------------------------
# 4. LOGIC ENGINES
# -----------------------------------------------------------------------------

# DAILY SWING LOGIC
def analyze_daily_balanced(ticker, df):
    if df.empty or len(df) < 205: return None
    curr = df.iloc[-1]
    prev = df.iloc[-2]
    
    is_uptrend = (curr['Close'] > curr['SMA_200']) and (curr['ADX'] > 15)
    dist = (curr['Close'] - curr['EMA_20']) / curr['EMA_20']
    is_pullback = (abs(dist) < 0.03) and (curr['RSI'] < 60)
    
    if not (is_uptrend and is_pullback): return None

    avg_vol = df['Volume'].rolling(20).mean().iloc[-1]
    if pd.isna(avg_vol) or avg_vol == 0: avg_vol = 1
    
    breakout = curr['Close'] > prev['High']
    vol_ok = curr['Volume'] > (avg_vol * 0.8)
    vol_strong = curr['Volume'] > avg_vol
    
    status = "WATCH"
    reason = "Setup Valid"
    
    if breakout and vol_ok:
        status = "BUY"
        reason = "Valid Swing (2x ATR Target)"
        if (curr['ADX'] > 20) and vol_strong:
            status = "STRONG BUY"
            reason = "🔥 High Conviction Swing"
            
    if status != "WATCH":
        stop = curr['Close'] - (2 * curr['ATR'])
        target = curr['Close'] + (2 * curr['ATR'])
        return {
            "Ticker": ticker, "Status": status, "Price": curr['Close'],
            "Stop": stop, "Target": target, "RSI": curr['RSI'], "Reason": reason
        }
    return None

# WEEKLY INVESTING LOGIC
def analyze_weekly(ticker, df_w):
    if df_w is None: return None
    curr = df_w.iloc[-1]
    prev = df_w.iloc[-2]
    
    is_uptrend = curr['Close'] > curr['SMA_50']
    dist = (curr['Close'] - curr['EMA_20']) / curr['EMA_20']
    is_value = (abs(dist) < 0.03)
    
    if not (is_uptrend and is_value): return None
    
    trigger = curr['Close'] > prev['High']
    
    if trigger:
        stop = curr['Close'] - (2.5 * curr['ATR'])
        target = curr['Close'] + (4 * curr['ATR'])
        return {
            "Ticker": ticker, "Status": "LONG TERM BUY", "Price": curr['Close'],
            "Stop": stop, "Target": target, "RSI": curr['RSI'], "Reason": "Weekly Trend Continuation"
        }
    return None

# --- NEW: DEEP VALUE / BOTTOM FISHING LOGIC ---
def analyze_deep_value(ticker, df):
    if df.empty or len(df) < 205: return None
    curr = df.iloc[-1]
    prev = df.iloc[-2]
    
    # 1. OVERALL WEAKNESS: RSI < 45
    if curr['RSI'] >= 45: return None
    
    # 2. MARKET CAP PROXY (Liquidity Check)
    # We use (Price * Volume) > $500k to filter out dead penny stocks
    # Real market cap checking is too slow for 500 stocks on Streamlit
    daily_liquidity = curr['Close'] * curr['Volume']
    if daily_liquidity < 500000: return None
    
    # 3. BUY MOMENTUM STARTING
    # Green Candle (Close > Open) AND Volume > 20 Day Avg
    avg_vol = df['Volume'].rolling(20).mean().iloc[-1]
    is_green = curr['Close'] > curr['Open']
    has_momentum = (curr['Volume'] > avg_vol) and is_green
    
    if not has_momentum: return None
    
    # 4. ROCKET FLAG (Deep Discount)
    # Trading at least 30% below 52-Week High (Price < 0.70 * High)
    high_52 = curr['52W_High']
    discount = (high_52 - curr['Close']) / high_52
    is_deep_value = discount >= 0.30 
    
    status = "REVERSAL"
    reason = "RSI < 45 + Vol Buy Signal"
    
    if is_deep_value:
        status = "ROCKET REVERSAL"
        reason = "🚀 Deep Discount (>30% off High) + Momentum"
        
    stop = curr['Low'] - (1 * curr['ATR']) # Tighter stop for knife catching
    target = curr['Close'] + (3 * curr['ATR']) # Reversion target
    
    return {
        "Ticker": ticker, "Status": status, "Price": curr['Close'],
        "Stop": stop, "Target": target, "RSI": curr['RSI'], "Reason": reason,
        "Discount": discount * 100
    }

# -----------------------------------------------------------------------------
# 5. UI TABS
# -----------------------------------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs(["🚀 DAILY SWING", "📅 WEEKLY INVESTING", "🔙 BACKTEST", "💎 BOTTOM FISHING"])

# === TAB 1: DAILY SCANNER ===
with tab1:
    st.header("Daily Swing Scanner")
    st.write("Optimized for **~60% Win Rate** (Targets 2x ATR).")
    
    if st.button("RUN DAILY SCAN", key="scan_d"):
        st.write("⏳ Downloading...")
        data = fetch_data()
        results = []
        prog = st.progress(0)
        
        for i, ticker in enumerate(ALL_TICKERS):
            try:
                if len(ALL_TICKERS)==1: df=data.dropna()
                else: df=data[ticker].dropna()
                df = calculate_daily_indicators(df)
                sig = analyze_daily_balanced(ticker, df)
                if sig: results.append(sig)
            except: pass
            if i % 25 == 0: prog.progress((i+1)/len(ALL_TICKERS))
            
        prog.empty()
        
        if not results: st.info("No Daily Setups.")
        else:
            results.sort(key=lambda x: (0 if x['Status']=="STRONG BUY" else 1, x['Ticker']))
            c1, c2 = st.columns(2)
            for i, res in enumerate(results):
                bd = "#00E676" if res['Status']=="STRONG BUY" else "#4CAF50"
                icon = "🔥" if res['Status']=="STRONG BUY" else "🟢"
                html = f"""<div style="background-color:#262730; padding:10px; border-left:5px solid {bd}; margin-bottom:10px;">
                <b style="color:white;">{icon} {res['Ticker']}</b><br><span style="color:#ccc">${res['Price']:.2f}</span><br><b style="color:{bd}">{res['Status']}</b></div>"""
                with (c1 if i%2==0 else c2):
                    st.markdown(html, unsafe_allow_html=True)
                    with st.expander("Plan"):
                        st.write(f"Stop: ${res['Stop']:.2f}")
                        st.write(f"Target: ${res['Target']:.2f}")

# === TAB 2: WEEKLY SCANNER ===
with tab2:
    st.header("Weekly Investing Scanner")
    st.write("Long-term holds. Uses **Weekly Candles**.")
    
    if st.button("RUN WEEKLY SCAN", key="scan_w"):
        st.write("⏳ Processing Weekly Data...")
        data = fetch_data()
        results = []
        prog = st.progress(0)
        
        for i, ticker in enumerate(ALL_TICKERS):
            try:
                if len(ALL_TICKERS)==1: df=data.dropna()
                else: df=data[ticker].dropna()
                df_w = convert_and_calculate_weekly(df)
                sig = analyze_weekly(ticker, df_w)
                if sig: results.append(sig)
            except: pass
            if i % 25 == 0: prog.progress((i+1)/len(ALL_TICKERS))
            
        prog.empty()
        
        if not results: st.info("No Weekly Setups.")
        else:
            c1, c2 = st.columns(2)
            for i, res in enumerate(results):
                html = f"""<div style="background-color:#1E2a38; padding:10px; border-left:5px solid #2196F3; margin-bottom:10px;">
                <b style="color:white;">🗓️ {res['Ticker']}</b><br><span style="color:#ccc">${res['Price']:.2f}</span><br><b style="color:#2196F3">{res['Status']}</b></div>"""
                with (c1 if i%2==0 else c2):
                    st.markdown(html, unsafe_allow_html=True)
                    with st.expander("Investment Plan"):
                        st.write(f"Stop: ${res['Stop']:.2f}")
                        st.write(f"Target: ${res['Target']:.2f}")

# === TAB 3: BACKTEST ===
with tab3:
    st.header("Backtest Simulator (Daily)")
    st.write("Simulates Daily 'Strong Buys' from last 10 days.")
    
    if st.button("RUN SIMULATION", key="sim"):
        st.write("⏳ calculating...")
        data = fetch_data()
        trades = []
        prog = st.progress(0)
        
        for i, ticker in enumerate(ALL_TICKERS):
            try:
                if len(ALL_TICKERS)==1: df=data.dropna()
                else: df=data[ticker].dropna()
                df = calculate_daily_indicators(df)
                
                for j in range(-10, -1):
                    curr = df.iloc[j]
                    prev = df.iloc[j-1]
                    future = df.iloc[j+1:]
                    
                    uptrend = (curr['Close'] > curr['SMA_200']) and (curr['ADX'] > 15)
                    pullback = (abs((curr['Close']-curr['EMA_20'])/curr['EMA_20']) < 0.03)
                    trigger = (curr['Close'] > prev['High']) and (curr['Volume'] > df['Volume'].rolling(20).mean().iloc[j] * 0.8)
                    
                    if uptrend and pullback and trigger:
                        entry = curr['Close']
                        stop = entry - (2*curr['ATR'])
                        target = entry + (2*curr['ATR'])
                        outcome="OPEN"; exit_p=df.iloc[-1]['Close']
                        
                        for _, row in future.iterrows():
                            if row['Low'] < stop: outcome="STOPPED"; exit_p=stop; break
                            if row['High'] > target: outcome="TARGET"; exit_p=target; break
                        
                        trades.append({"Ticker":ticker, "Entry":entry, "Exit":exit_p, "Outcome":outcome, "Return %":
