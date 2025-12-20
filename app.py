import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. APP CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(page_title="UniAlgo Trader", page_icon="📈", layout="centered")

# CSS for Mobile-Friendly Cards
st.markdown("""
<style>
    .trade-card {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50; /* Green for Buy */
        margin-bottom: 10px;
    }
    .watchlist-card {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FFC107; /* Yellow for Watch */
        margin-bottom: 10px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 Algo Scanner")
st.caption("Medium-Term Swing Strategy | Daily Candles")

# -----------------------------------------------------------------------------
# 2. SIDEBAR SETTINGS & UNIVERSE
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("Settings")
    lookback = st.slider("Lookback (Years)", 1, 3, 2)
    
    st.subheader("Stock Universe")
    # Default includes US Tech, Blue Chips, and Canadian Big Caps
    default_tickers = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "JPM", "V", "COST", # US
        "RY.TO", "TD.TO", "SHOP.TO", "CNR.TO", "ENB.TO", "BMO.TO", "ATD.TO"  # TSX
    ]
    
    tickers_input = st.text_area(
        "Edit Tickers (comma separated)", 
        value=", ".join(default_tickers), 
        height=200
    )
    # Process ticker list
    TICKERS = [x.strip().upper() for x in tickers_input.split(",") if x.strip()]

# -----------------------------------------------------------------------------
# 3. INDICATOR CALCULATIONS
# -----------------------------------------------------------------------------
def calculate_indicators(df):
    df = df.copy()
    
    # Simple Moving Average (200) - Trend Filter
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    
    # Exponential Moving Average (20) - Pullback Support
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    
    # RSI (14) - Momentum
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # ATR (14) - Volatility for Stops
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    df['ATR'] = true_range.rolling(window=14).mean()
    
    # ADX (14) - Trend Strength (Simplified calculation)
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
# 4. TRADING LOGIC
# -----------------------------------------------------------------------------
def check_strategy(ticker, df):
    # Need enough data
    if len(df) < 205: 
        return None
        
    curr = df.iloc[-1]
    prev = df.iloc[-2]
    
    # --- 1. FILTER: Long Term Trend ---
    # Price > 200 SMA AND ADX > 15 (Trend exists)
    is_uptrend = (curr['Close'] > curr['SMA_200']) and (curr['ADX'] > 15)
    
    # --- 2. SETUP: Pullback to Value ---
    # Price is close to EMA 20 (within 2.5%) AND RSI is not Overbought (>60)
    dist_to_ema = (curr['Close'] - curr['EMA_20']) / curr['EMA_20']
    is_pullback = (abs(dist_to_ema) < 0.025) and (curr['RSI'] < 60)
    
    # --- 3. TRIGGER: Momentum Shift ---
    # Price closes higher than previous high OR Green Candle
    is_trigger = (curr['Close'] > prev['High']) or (curr['Close'] > curr['Open'])
    
    # Volume Check (Current vol > 80% of 20-day avg)
    avg_vol = df['Volume'].rolling(20).mean().iloc[-1]
    vol_valid = curr['Volume'] > (avg_vol * 0.8)

    # --- DECISION ---
    status = "WAIT"
    reason = "No setup"
    
    if is_uptrend:
        if is_pullback:
            if is_trigger and vol_valid:
                status = "BUY"
                reason = "Trend + Pullback + Trigger"
            else:
                status = "WATCH"
                reason = "Setup Valid (Waiting for Trigger)"
        else:
            status = "TREND" # Strong trend but no pullback
    else:
        status = "AVOID"

    # Only return actionable items
    if status in ["BUY", "WATCH"]:
        stop_loss = curr['Close'] - (2 * curr['ATR'])
        take_profit = curr['Close'] + (3 * curr['ATR'])
        
        return {
            "Ticker": ticker,
            "Status": status,
            "Price": float(curr['Close']),
            "Stop": float(stop_loss),
            "Target": float(take_profit),
            "RSI": float(curr['RSI']),
            "ADX": float(curr['ADX']),
            "Reason": reason
        }
    return None

# -----------------------------------------------------------------------------
# 5. UI EXECUTION
# -----------------------------------------------------------------------------
if st.button("🚀 Run Live Scan"):
    
    st.write("Scanning market data...")
    progress_bar = st.progress(0)
    
    results = []
    
    for i, ticker in enumerate(TICKERS):
        try:
            # Download data
            df = yf.download(ticker, period=f"{lookback}y", interval="1d", progress=False, auto_adjust=True)
            
            if not df.empty:
                df = calculate_indicators(df)
                signal = check_strategy(ticker, df)
                if signal:
                    results.append(signal)
        except Exception as e:
            # Silently fail on bad tickers to keep app running
            pass
            
        # Update progress
        progress_bar.progress((i + 1) / len(TICKERS))
    
    progress_bar.empty()
    
    # --- DISPLAY RESULTS ---
    if not results:
        st.info("No trades found matching strict criteria right now.")
    else:
        # Sort BUYs first
        results.sort(key=lambda x: x['Status']) 
        
        st.success(f"Found {len(results)} potential setups!")
        
        for res in results:
            # Determine card style
            if res['Status'] == "BUY":
                css_class = "trade-card"
                icon = "🟢" 
                action_text = "READY TO ENTER"
            else:
                css_class = "watchlist-card"
                icon = "👀"
                action_text = "ADD TO WATCHLIST"
            
            # Draw Card
            st.markdown(f"""
            <div class="{css_class}">
                <h3 style="margin:0; color:white;">{icon} {res['Ticker']} <span style="font-size:0.7em; color:#ddd;">${res['Price']:.2f}</span></h3>
                <p style="margin:5px 0 0 0; color:#eee; font-weight:bold;">{action_text}</p>
                <p style="margin:0; color:#bbb; font-size:0.9em;">{res['Reason']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Details Expander
            with st.expander(f"See Plan for {res['Ticker']}"):
                c1, c2, c3 = st.columns(3)
                c1.metric("Stop Loss", f"${res['Stop']:.2f}")
                c2.metric("Target", f"${res['Target']:.2f}")
                c3.metric("RSI", f"{res['RSI']:.0f}")
                
                # Simple Plotly Chart
                try:
                    df_chart = yf.download(res['Ticker'], period="6mo", interval="1d", progress=False, auto_adjust=True)
                    fig = go.Figure(data=[go.Candlestick(
                        x=df_chart.index,
                        open=df_chart['Open'], high=df_chart['High'],
                        low=df_chart['Low'], close=df_chart['Close']
                    )])
                    fig.update_layout(
                        height=300, 
                        margin=dict(l=0,r=0,t=0,b=0), 
                        template="plotly_dark",
                        xaxis_rangeslider_visible=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except:
                    st.write("Chart unavailable")
