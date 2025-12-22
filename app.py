import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

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
</style>
""", unsafe_allow_html=True)

st.title("⚡ 500-Stock Market Scanner")
st.caption("Universities: S&P 500 (US) + TSX 60 (Canada) | Logic: Volatility Compression Swing")

# -----------------------------------------------------------------------------
# 2. TICKER UNIVERSE
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
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "TSLA", "BRK-B", "UNH", "JNJ",
    "XOM", "V", "PG", "JPM", "MA", "HD", "CVX", "MRK", "ABBV", "PEP", "KO", "LLY",
    "BAC", "AVGO", "COST", "TMO", "MCD", "CSCO", "CRM", "PFE", "ACN", "DHR", "LIN",
    "NFLX", "ABT", "AMD", "DIS", "WMT", "TXN", "NEE", "PM", "BMY", "ADBE", "CMCSA",
    "NKE", "VZ", "RTX", "UPS", "MS", "HON", "AMGN", "INTC", "UNP", "LOW", "QCOM",
    "IBM", "SPGI", "INTU", "CAT", "GS", "DE", "GE", "LMT", "PLD", "BLK", "EL",
    "SCHW", "BKNG", "AMAT", "ADI", "MDLZ", "TJX", "ADP", "MMC", "GILD", "C", "ISRG",
    "SYK", "VRTX", "TMUS", "NOW", "ZTS", "BA", "PGR", "T", "CB", "REGN", "SO", "MO",
    "CI", "BDX", "LRCX", "FISV", "EOG", "BSX", "SLB", "ITW", "CL", "APD", "ATVI",
    "CSX", "CCI", "ETN", "HUM", "WM", "NOC", "TGT", "FDX", "NSC", "GD", "ICE", "SHW",
    "MCO", "USB", "GM", "KLAC", "MCK", "PNC", "EMR", "ORCL", "F", "AON", "ECL",
    "MDT", "HCA", "FCX", "NXPI", "MAR", "ROP", "PSX", "APH", "PCAR", "COF", "VLO",
    "MNST", "SNPS", "MSI", "AIG", "OXY", "ROST", "DXCM", "AZO", "MET", "AEP", "TRV",
    "SRE", "TEL", "D", "PSA", "IDXX", "PH", "KMB", "JCI", "CHTR", "ALL", "CTAS",
    "WMB", "AFL", "ADSK", "PAYX", "EXC", "DLR", "BIIB", "O", "STZ", "FIS", "EW",
    "EA", "GPN", "HLT", "CMG", "XEL", "ELV", "CTVA", "KR", "YUM", "KMI", "WBA",
    "PRU", "SYY", "DVN", "LHX", "CNC", "NEM", "CMI", "OTIS", "VRSK", "DD", "HPQ",
    "FAST", "CSGP", "WEC", "SBAC", "HES", "ANET", "KEYS", "DLTR", "CPRT", "ROK",
    "PEG", "AMP", "BKR", "PPG", "ES", "ED", "AWK", "APTV", "GLW", "MTD", "ULTA",
    "EFX", "TROW", "HSY", "EIX", "CBRE", "ARE", "VRSN", "EBAY", "ZBH", "ALB",
    "TSCO", "DFS", "HIG", "WBD", "FE", "AME", "MTB", "OKE", "IFF", "WY", "KHC",
    "RMD", "BAX", "STT", "CDW", "HAL", "ETR", "GWW", "AJG", "RJF", "DAL", "IR",
    "FANG", "ON", "MCHP", "LYB", "VTR", "LUV", "NVR", "WTW", "IT", "DHI", "TSN",
    "HBAN", "XYL", "FSLR", "GPC", "VICI", "WAB", "CINF", "DOV", "MLM", "GRMN",
    "EXR", "OMC", "BBY", "HPE", "TTWO", "CNP", "VMC", "CAG", "TER", "INGR", "KEY",
    "RF", "CMS", "PFG", "STE", "WAT", "CF", "NTAP", "AES", "FMC", "TYL", "DGX",
    "PKI", "EXPD", "IEX", "AVY", "CBOE", "DRI", "MKC", "ATO", "TXT", "SJM", "BWA",
    "HOLX", "ABMD", "COO", "JBHT", "ESS", "WST", "LNT", "MAA", "NDSN", "AKAM",
    "DG", "POOL", "TRMB", "ALGN", "CE", "MAS", "SNA", "SWK", "UDR", "HST", "K",
    "INCY", "MGM", "O", "PHM", "PKG", "RL", "ROL", "SWKS", "UHS", "URI", "VFC",
    "WHR", "WRB", "XRAY", "ZION", "A", "AAL", "AAP", "AES", "ALK", "APA", "BXP",
    "CPB", "CRL", "DISH", "DVA", "EMN", "EVRG", "FFIV", "FRT", "GNRC", "HAS",
    "HSIC", "IP", "IPG", "IVZ", "JNPR", "KMX", "LKQ", "LNC", "LVS", "MHK", "MOH",
    "MOS", "NCLH", "NI", "NRG", "NWS", "NWSA", "OGN", "PARA", "PEAK", "PNR", "PNW",
    "PVH", "QRVO", "RCL", "REG", "RHI", "SEE", "SIVB", "SPG", "TPR", "UAA", "UA"
]

ALL_TICKERS = TSX_TICKERS + US_TICKERS

# -----------------------------------------------------------------------------
# 3. HELPER: INDICATORS
# -----------------------------------------------------------------------------
def calculate_indicators(df):
    if df.empty or len(df) < 205: return df
    df = df.copy()
    
    # Trend
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    # Pullback
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    # ATR (Risk)
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    df['ATR'] = true_range.rolling(window=14).mean()
    # ADX (Strength)
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
# 4. TRADING LOGIC (Strong Buy vs Buy)
# -----------------------------------------------------------------------------
def analyze_stock(ticker, df):
    if df.empty or len(df) < 205: return None
    if 'SMA_200' not in df.columns: return None
        
    curr = df.iloc[-1]
    prev = df.iloc[-2]
    
    # 1. Base Gates
    is_uptrend = (curr['Close'] > curr['SMA_200']) and (curr['ADX'] > 15)
    dist_to_ema = (curr['Close'] - curr['EMA_20']) / curr['EMA_20']
    is_pullback = (abs(dist_to_ema) < 0.03) and (curr['RSI'] < 60)
    
    if not (is_uptrend and is_pullback): return None

    # 2. Classification
    avg_vol = df['Volume'].rolling(20).mean().iloc[-1]
    if pd.isna(avg_vol) or avg_vol == 0: avg_vol = 1
    
    status = "WATCH"
    reason = "Setup Valid (Waiting for Trigger)"
    
    basic_trigger = (curr['Close'] > curr['Open']) or (curr['Close'] > prev['High'])
    basic_vol = curr['Volume'] > (avg_vol * 0.7)
    
    if basic_trigger and basic_vol:
        status = "BUY"
        reason = "Standard: Trend + Pullback + Reversal"

        # Strong Buy Logic
        strong_trend = curr['ADX'] > 25
        strong_trigger = curr['Close'] > prev['High']
        strong_vol = curr['Volume'] > avg_vol
        
        if strong_trend and strong_trigger and strong_vol:
            status = "STRONG BUY"
            reason = "🔥 High Conviction: Strong Trend + Vol Spike"

    if status in ["STRONG BUY", "BUY", "WATCH"]:
        stop = curr['Close'] - (2 * curr['ATR'])
        target = curr['Close'] + (3 * curr['ATR'])
        return {
            "Ticker": ticker, "Status": status, "Price": curr['Close'],
            "Stop": stop, "Target": target, "RSI": curr['RSI'],
            "ADX": curr['ADX'], "ATR": curr['ATR'],
            "SMA200": curr['SMA_200'], "EMA20": curr['EMA_20'],
            "Reason": reason
        }
    return None

# -----------------------------------------------------------------------------
# 5. MAIN EXECUTION
# -----------------------------------------------------------------------------
if st.button("🚀 SCAN 500 STOCKS"):
    
    status_area = st.empty()
    status_area.write(f"⚠️ Downloading data for {len(ALL_TICKERS)} stocks... (approx 45s)")
    
    try:
        data = yf.download(ALL_TICKERS, period="2y", group_by='ticker', auto_adjust=True, threads=True)
        status_area.write("✅ Data received. Analyzing...")
        
        results = []
        progress_bar = st.progress(0)
        count = 0
        total = len(ALL_TICKERS)
        
        for ticker in ALL_TICKERS:
            try:
                if len(ALL_TICKERS) == 1: df = data.dropna()
                else: df = data[ticker].dropna()
                
                df = calculate_indicators(df)
                signal = analyze_stock(ticker, df)
                if signal: results.append(signal)
            except: continue
            
            count += 1
            if count % 10 == 0: progress_bar.progress(count / total)
        
        progress_bar.empty()
        status_area.empty()
        
        if not results:
            st.info("No setups found. Market may be choppy.")
        else:
            st.success(f"Found {len(results)} Opportunities!")
            
            # --- SORTING LOGIC HERE ---
            # 0 = Top, 1 = Middle, 2 = Bottom
            def sort_priority(status):
                if status == "STRONG BUY": return 0
                if status == "BUY": return 1
                return 2
            
            # Sort by Priority, then by Ticker Name
            results.sort(key=lambda x: (sort_priority(x['Status']), x['Ticker']))
            
            col1, col2 = st.columns(2)
            
            for i, res in enumerate(results):
                if res['Status'] == "STRONG BUY":
                    border_color = "#00E676" # Neon Green
                    emoji = "🔥"
                    bg_color = "#1E3A2F" 
                elif res['Status'] == "BUY":
                    border_color = "#4CAF50" # Green
                    emoji = "🟢"
                    bg_color = "#262730"
                else:
                    border_color = "#FFC107" # Yellow
                    emoji = "👀"
                    bg_color = "#262730"
                
                html_card = f"""
                <div style="background-color: {bg_color}; padding: 15px; border-radius: 10px; border-left: 5px solid {border_color}; margin-bottom: 10px;">
                    <h4 style="margin:0; color:white;">{emoji} {res['Ticker']}</h4>
                    <p style="margin:0; color:#ddd; font-size:0.9em;">${res['Price']:.2f}</p>
                    <p style="margin:5px 0; color:#eee; font-weight:bold; font-size:0.8em;">{res['Status']}</p>
                </div>
                """
                
                with (col1 if i % 2 == 0 else col2):
                    st.markdown(html_card, unsafe_allow_html=True)
                    with st.expander("Show Data"):
                        st.markdown("**🛑 Plan**")
                        st.write(f"Stop: ${res['Stop']:.2f}")
                        st.write(f"Target: ${res['Target']:.2f}")
                        st.caption(res['Reason'])
                        st.markdown("---")
                        st.markdown("**📊 Stats**")
                        st.write(f"RSI: {res['RSI']:.1f}")
                        st.write(f"ADX: {res['ADX']:.1f}")
                        try:
                            df_chart = yf.download(res['Ticker'], period="6mo", interval="1d", progress=False, auto_adjust=True)
                            fig = go.Figure(data=[go.Candlestick(x=df_chart.index,
                                    open=df_chart['Open'], high=df_chart['High'],
                                    low=df_chart['Low'], close=df_chart['Close'])])
                            fig.update_layout(height=200, margin=dict(t=0,b=0,l=0,r=0), template="plotly_dark")
                            st.plotly_chart(fig, use_container_width=True)
                        except: pass

    except Exception as e:
        st.error(f"Error: {e}")
