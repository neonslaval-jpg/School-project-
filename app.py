import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime

# -----------------------------------------------------------------------------
# 1. APP CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(page_title="UniAlgo Pro", page_icon="⚡", layout="wide")

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

st.title("⚡ UniAlgo: Balanced Scanner")
st.caption("Strategy: Volatility Compression Swing (Optimized for Win Rate + Frequency)")

# -----------------------------------------------------------------------------
# 2. TICKER UNIVERSE (S&P 500 + TSX 60)
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

ALL_TICKERS = TSX_TICKERS + US_TICKERS

# -----------------------------------------------------------------------------
# 3. DATA CACHING & HELPERS
# -----------------------------------------------------------------------------

@st.cache_data(ttl=3600) # Cache data for 1 hour
def fetch_data():
    return yf.download(ALL_TICKERS, period="2y", group_by='ticker', auto_adjust=True, threads=True)

def calculate_indicators(df):
    if df.empty or len(df) < 205: return df
    df = df.copy()
    
    # 1. Trend
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    
    # 2. Pullback
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    
    # 3. RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # 4. ATR (Risk)
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    df['ATR'] = true_range.rolling(window=14).mean()
    
    # 5. ADX
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
# 4. TRADING LOGIC (BALANCED)
# -----------------------------------------------------------------------------
def analyze_stock(ticker, df):
    if df.empty or len(df) < 205: return None
    if 'SMA_200' not in df.columns: return None
        
    curr = df.iloc[-1]
    prev = df.iloc[-2]
    
    # --- 1. BALANCED GATES (Relaxed slightly to capture more moves) ---
    
    # Trend: Price > SMA200 AND ADX > 15 (Was 20)
    # Rationale: 15 captures early trends, 20 was missing too many.
    is_uptrend = (curr['Close'] > curr['SMA_200']) and (curr['ADX'] > 15)
    
    # Pullback: Price near EMA20 (+/- 3%) AND RSI < 60
    # Rationale: RSI < 60 gives us room to grow before hitting overbought (70)
    dist_to_ema = (curr['Close'] - curr['EMA_20']) / curr['EMA_20']
    is_pullback = (abs(dist_to_ema) < 0.03) and (curr['RSI'] < 60)
    
    if not (is_uptrend and is_pullback): return None

    # --- 2. TRIGGER CLASSIFICATION ---
    avg_vol = df['Volume'].rolling(20).mean().iloc[-1]
    if pd.isna(avg_vol) or avg_vol == 0: avg_vol = 1
    
    status = "WATCH"
    reason = "Setup Valid (Waiting for Trigger)"
    
    # PRIMARY TRIGGER: Close > Prev High (Breakout of previous daily candle)
    breakout = curr['Close'] > prev['High']
    
    # MOMENTUM TRIGGER: RSI Hook (RSI is rising compared to yesterday)
    rsi_rising = curr['RSI'] > prev['RSI']
    
    # VOLUME TRIGGER: > 80% of Avg (Was 100%)
    vol_decent = curr['Volume'] > (avg_vol * 0.8)
    vol_strong = curr['Volume'] > avg_vol # For Strong Buy

    # --- DECISION TREE ---
    
    # Standard Buy: Needs Breakout + RSI Rising + Decent Volume
    if breakout and rsi_rising and vol_decent:
        status = "BUY"
        reason = "Valid: Trend + Breakout + RSI Hook"
        
        # Strong Buy: Needs Stronger Trend + Higher Volume
        if (curr['ADX'] > 20) and vol_strong:
            status = "STRONG BUY"
            reason = "🔥 High Conviction: ADX>20 + Strong Vol + Breakout"

    # --- 3. OUTPUT & TARGET ADJUSTMENT ---
    if status in ["STRONG BUY", "BUY", "WATCH"]:
        # WIN RATE HACK:
        # Lower Take Profit from 3x ATR to 2x ATR.
        # This locks in wins faster, improving Win Rate % at expense of max profit.
        stop = curr['Close'] - (2 * curr['ATR'])
        target = curr['Close'] + (2 * curr['ATR']) # Changed from 3 to 2
        
        return {
            "Ticker": ticker, 
            "Status": status, 
            "Price": curr['Close'],
            "Stop": stop, 
            "Target": target, 
            "RSI": curr['RSI'],
            "ADX": curr['ADX'],
            "ATR": curr['ATR'],
            "SMA200": curr['SMA_200'],
            "EMA20": curr['EMA_20'],
            "Reason": reason
        }
    return None

# -----------------------------------------------------------------------------
# 5. APP INTERFACE
# -----------------------------------------------------------------------------

tab1, tab2 = st.tabs(["🚀 LIVE SCANNER", "🔙 BACKTEST SIMULATOR"])

# =============================================================================
# TAB 1: LIVE SCANNER
# =============================================================================
with tab1:
    st.header("Daily Swing Scanner (Balanced)")
    st.write("Scan optimized for **~60% Win Rate** by taking profits earlier (2x ATR).")
    
    if st.button("RUN SCANNER", key="btn_scan"):
        status_text = st.empty()
        status_text.write("⏳ Downloading Market Data...")
        
        try:
            data = fetch_data()
            status_text.write("✅ Analyzing Technicals...")
            
            results = []
            progress_bar = st.progress(0)
            count = 0
            
            for ticker in ALL_TICKERS:
                try:
                    if len(ALL_TICKERS) == 1: df = data.dropna()
                    else: df = data[ticker].dropna()
                    
                    df = calculate_indicators(df)
                    signal = analyze_stock(ticker, df)
                    
                    if signal: results.append(signal)
                except: continue
                
                count += 1
                if count % 25 == 0: progress_bar.progress(count / len(ALL_TICKERS))
            
            progress_bar.empty()
            status_text.empty()
            
            if not results:
                st.warning("No setups found today. Market may be choppy.")
            else:
                # Sort: Strong Buy -> Buy -> Watch
                def sort_prio(s):
                    if s == "STRONG BUY": return 0
                    if s == "BUY": return 1
                    return 2
                results.sort(key=lambda x: (sort_prio(x['Status']), x['Ticker']))
                
                st.success(f"Found {len(results)} Setups")
                
                c1, c2 = st.columns(2)
                for i, res in enumerate(results):
                    if res['Status'] == "STRONG BUY": 
                        bd, icon, bg = "#00E676", "🔥", "#1E3A2F"
                    elif res['Status'] == "BUY": 
                        bd, icon, bg = "#4CAF50", "🟢", "#262730"
                    else: 
                        bd, icon, bg = "#FFC107", "👀", "#262730"
                        
                    html = f"""
                    <div style="background-color:{bg}; padding:10px; border-radius:10px; border-left:5px solid {bd}; margin-bottom:10px;">
                        <b style="color:white; font-size:1.1em;">{icon} {res['Ticker']}</b>
                        <br><span style="color:#ccc;">${res['Price']:.2f}</span>
                        <br><span style="color:{bd}; font-weight:bold;">{res['Status']}</span>
                    </div>
                    """
                    with (c1 if i % 2 == 0 else c2):
                        st.markdown(html, unsafe_allow_html=True)
                        with st.expander("Plan"):
                            st.write(f"**Stop:** ${res['Stop']:.2f}")
                            st.write(f"**Target:** ${res['Target']:.2f} (2x ATR)")
                            st.write(f"**RSI:** {res['RSI']:.1f}")
                            st.caption(res['Reason'])

        except Exception as e:
            st.error(f"Error: {e}")

# =============================================================================
# TAB 2: BACKTEST SIMULATOR
# =============================================================================
with tab2:
    st.header("Backtest Simulator")
    st.write("Simulates performance of **STRONG BUY** signals over the last 10 days.")
    
    if st.button("RUN SIMULATION", key="btn_backtest"):
        status_text = st.empty()
        status_text.write("⏳ Re-using Cached Data...")
        
        try:
            data = fetch_data()
            trades = []
            
            progress_bar = st.progress(0)
            count = 0
            
            for ticker in ALL_TICKERS:
                try:
                    if len(ALL_TICKERS) == 1: df = data.dropna()
                    else: df = data[ticker].dropna()
                    
                    if len(df) < 220: continue
                    df = calculate_indicators(df)
                    
                    # Backtest Loop: Last 10 days
                    for i in range(-10, -1):
                        curr = df.iloc[i]
                        prev = df.iloc[i-1]
                        future_prices = df.iloc[i+1:]
                        
                        # --- REPLICATE LOGIC ---
                        is_uptrend = (curr['Close'] > curr['SMA_200']) and (curr['ADX'] > 15)
                        dist = (curr['Close'] - curr['EMA_20']) / curr['EMA_20']
                        is_pullback = (abs(dist) < 0.03) and (curr['RSI'] < 60)
                        
                        avg_vol = df['Volume'].rolling(20).mean().iloc[i]
                        breakout = curr['Close'] > prev['High']
                        rsi_rising = curr['RSI'] > prev['RSI']
                        vol_strong = curr['Volume'] > avg_vol
                        
                        # Only testing STRONG BUY for backtest quality check
                        if is_uptrend and is_pullback and breakout and rsi_rising and vol_strong and (curr['ADX'] > 20):
                            
                            entry_price = curr['Close']
                            stop_loss = entry_price - (2 * curr['ATR'])
                            target = entry_price + (2 * curr['ATR']) # 2x ATR Target
                            
                            outcome = "OPEN"
                            exit_price = df.iloc[-1]['Close']
                            
                            for date, row in future_prices.iterrows():
                                if row['Low'] < stop_loss:
                                    outcome = "STOPPED"
                                    exit_price = stop_loss
                                    break
                                if row['High'] > target:
                                    outcome = "TARGET"
                                    exit_price = target
                                    break
                            
                            pnl = (exit_price - entry_price) / entry_price
                            
                            trades.append({
                                "Ticker": ticker,
                                "Date": df.index[i].date(),
                                "Entry": entry_price,
                                "Exit": exit_price,
                                "Outcome": outcome,
                                "Return %": pnl * 100
                            })
                            
                except: continue
                count += 1
                if count % 25 == 0: progress_bar.progress(count / len(ALL_TICKERS))
            
            progress_bar.empty()
            status_text.empty()
            
            if not trades:
                st.info("No Strong Buy signals found in the last 10 days.")
            else:
                df_res = pd.DataFrame(trades)
                
                avg_ret = df_res['Return %'].mean()
                win_rate = len(df_res[df_res['Return %'] > 0]) / len(df_res) * 100
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Trades", len(df_res))
                m2.metric("Win Rate", f"{win_rate:.1f}%")
                m3.metric("Avg Return", f"{avg_ret:.2f}%", 
                          delta_color="normal" if avg_ret > 0 else "inverse")
                
                st.divider()
                st.write("### Trade Log")
                
                def highlight_outcome(val):
                    color = 'green' if val == 'TARGET' else 'red' if val == 'STOPPED' else 'orange'
                    return f'color: {color}; font-weight: bold'
                
                st.dataframe(
                    df_res.style.applymap(highlight_outcome, subset=['Outcome'])
                    .format({"Entry": "${:.2f}", "Exit": "${:.2f}", "Return %": "{:.2f}%"}),
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"Error: {e}")

