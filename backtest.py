import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import warnings

# Suppress pandas warnings for cleaner output
warnings.filterwarnings('ignore')

# -----------------------------------------------------------------------------
# 1. TICKER UNIVERSE (Full List)
# -----------------------------------------------------------------------------
print("--- CONFIGURING UNIVERSE ---")

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
    "WST", "WY", "WYNN", "XEL", "XYL", "YUM", "ZBRA", "ZION", "ZTS", "MMM", 
    "AOS", "ABT", "ABBV", "ACN", "ADM", "ADBE", "ADP", "AES", "AFL", "A", 
    "APD", "AKAM", "ALK", "ALB", "ARE", "ALGN", "ALLE", "LNT", "ALL", "GOOGL", 
    "GOOG", "MO", "AMZN", "AMCR", "AMD", "AEE", "AAL", "AEP", "AXP", "AIG", 
    "AMT", "AWK", "AMP", "ABC", "AME", "AMGN", "APH", "ADI", "ANSS", "AON", 
    "APA", "AAPL", "AMAT", "APTV", "ACGL", "ADM", "ANET", "AJG", "AIZ", "T", 
    "ATO", "ADSK", "AZO", "AVB", "AVY", "BKR", "BALL", "BAC", "BBWI", "BAX", 
    "BDX", "WRB", "BRK-B", "BBY", "BIO", "TECH", "BIIB", "BLK", "BK", "BA", 
    "BKNG", "BWA", "BXP", "BSX", "BMY", "AVGO", "BR", "BRO", "BF-B", "CHRW", 
    "CDNS", "CZR", "CPT", "COF", "CAH", "KMX", "CCL", "CARR", "CTLT", "CAT", 
    "CBOE", "CBRE", "CDW", "CE", "CNC", "CNP", "CDAY", "CF", "CRL", "SCHW", 
    "CHTR", "CVX", "CMG", "CB", "CHD", "CI", "CINF", "CTAS", "CSCO", "C", 
    "CFG", "CLX", "CME", "CMS", "KO", "CTSH", "CL", "CMCSA", "CMA", "CAG", 
    "COP", "ED", "STZ", "COO", "CPRT", "GLW", "CTVA", "COST", "CTRA", "CCI", 
    "CSX", "CMI", "CVS", "DHI", "DHR", "DRI", "DVA", "DE", "DAL", "XRAY", 
    "DVN", "DXCM", "FANG", "DLR", "DFS", "DISH", "DIS", "DG", "DLTR", "D", 
    "DPZ", "DOV", "DOW", "DTE", "DUK", "DD", "DXC", "EMN", "ETN", "EBAY", 
    "ECL", "EIX", "EW", "EA", "EMR", "ENPH", "ETR", "EOG", "EPAM", "EQT", 
    "EFX", "EQIX", "EQR", "ESS", "EL", "ETSY", "EG", "EVRG", "ES", "EXC", 
    "EXPE", "EXPD", "EXR", "XOM", "FFIV", "FDS", "FAST", "FRT", "FDX", "FITB", 
    "FRC", "FE", "FIS", "FISV", "FLT", "FMC", "F", "FTNT", "FTV", "FBHS", 
    "FOXA", "FOX", "BEN", "FCX", "GRMN", "IT", "GEHC", "GEN", "GNRC", "GD", 
    "GE", "GIS", "GM", "GPC", "GILD", "GL", "GPN", "GS", "HAL", "HIG", 
    "HAS", "HCA", "PEAK", "HSIC", "HSY", "HES", "HPE", "HLT", "HOLX", "HD", 
    "HON", "HRL", "HST", "HWM", "HPQ", "HUM", "HBAN", "HII", "IBM", "IEX", 
    "IDXX", "ITW", "ILMN", "INCY", "IR", "INTC", "ICE", "IP", "IPG", "IFF", 
    "INTU", "ISRG", "IVZ", "INVH", "IQV", "IRM", "JBHT", "JKHY", "J", "JNJ", 
    "JCI", "JPM", "JNPR", "K", "KDP", "KEY", "KEYS", "KMB", "KIM", "KMI", 
    "KLAC", "KHC", "KR", "LHX", "LH", "LRCX", "LW", "LVS", "LDOS", "LEN", 
    "LLY", "LNC", "LIN", "LYV", "LKQ", "LMT", "L", "LOW", "LUMN", "LYB", 
    "MTB", "MRO", "MPC", "MKTX", "MAR", "MMC", "MLM", "MAS", "MA", "MTCH", 
    "MKC", "MCD", "MCK", "MDT", "MRK", "META", "MET", "MTD", "MGM", "MCHP", 
    "MU", "MSFT", "MAA", "MRNA", "MHK", "MOH", "TAP", "MDLZ", "MPWR", "MNST", 
    "MCO", "MS", "MOS", "MSI", "MSCI", "NDAQ", "NTAP", "NFLX", "NWL", "NEM", 
    "NWSA", "NWS", "NEE", "NKE", "NI", "NDSN", "NSC", "NTRS", "NOC", "NCLH", 
    "NRG", "NUE", "NVDA", "NVR", "NXPI", "ORLY", "OXY", "ODFL", "OMC", "ON", 
    "OKE", "ORCL", "OGN", "OTIS", "PCAR", "PKG", "PARA", "PH", "PAYX", "PAYC", 
    "PYPL", "PNR", "PEP", "PKI", "PFE", "PCG", "PM", "PSX", "PNW", "PXD", 
    "PNC", "POOL", "PPG", "PPL", "PFG", "PG", "PGR", "PLD", "PRU", "PEG", 
    "PTC", "PSA", "PHM", "QRVO", "PWR", "QCOM", "DGX", "RL", "RJF", "RTX", 
    "O", "REG", "REGN", "RF", "RSG", "RMD", "RHI", "ROK", "ROL", "ROP", 
    "ROST", "RCL", "SPGI", "CRM", "SBAC", "SLB", "STX", "SEE", "SRE", "NOW", 
    "SHW", "SPG", "SWKS", "SJM", "SNA", "SEDG", "SO", "LUV", "SWK", "SBUX", 
    "STT", "STE", "SYK", "SIVB", "SYF", "SNPS", "SYY", "TMUS", "TROW", "TTWO", 
    "TPR", "TRGP", "TGT", "TEL", "TDY", "TFX", "TER", "TSLA", "TXN", "TXT", 
    "TMO", "TJX", "TSCO", "TT", "TDG", "TRV", "TRMB", "TFC", "TWTR", "TYL", 
    "TSN", "USB", "UDR", "ULTA", "UAA", "UA", "UNP", "UAL", "UNH", "UPS", 
    "URI", "UHS", "VLO", "VTR", "VRSN", "VRSK", "VZ", "VRTX", "VFC", "VTRS", 
    "VICI", "V", "VNO", "VMC", "WAB", "WBA", "WMT", "WBD", "WM", "WAT", 
    "WEC", "WFC", "WELL", "WST", "WDC", "WRK", "WY", "WHR", "WMB", "WTW", 
    "GWW", "WYNN", "XEL", "XYL", "YUM", "ZBRA", "ZBH", "ZION", "ZTS"
]

UNIVERSE = TSX_TICKERS + US_TICKERS

# -----------------------------------------------------------------------------
# 2. INDICATOR LOGIC (EXACT MATCH TO APP.PY)
# -----------------------------------------------------------------------------
def calculate_indicators(df):
    if df.empty or len(df) < 205: return df
    df = df.copy()
    
    # 1. Trend Filter: SMA 200
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    
    # 2. Pullback Zone: EMA 20
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    
    # 3. Momentum: RSI 14
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # 4. Risk Mgmt: ATR 14
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    df['ATR'] = true_range.rolling(window=14).mean()
    
    # 5. Trend Strength: ADX 14
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
# 3. BACKTEST ENGINE
# -----------------------------------------------------------------------------
def run_backtest():
    print(f"--- STARTING BACKTEST ON {len(UNIVERSE)} STOCKS ---")
    print("Fetching historical data (This may take 1-2 minutes)...")
    
    try:
        # BATCH DOWNLOAD for speed
        # We need more history than the scanner to simulate 10 days ago + 200 day SMA
        data = yf.download(UNIVERSE, period="2y", group_by='ticker', auto_adjust=True, threads=True)
    except Exception as e:
        print(f"Download Error: {e}")
        return

    print("Data Downloaded. Processing Strategy...")
    trades = []
    
    # Counter for progress
    count = 0
    
    for ticker in UNIVERSE:
        count += 1
        if count % 50 == 0: print(f"Processed {count}/{len(UNIVERSE)}...")
        
        try:
            # Handle MultiIndex
            if len(UNIVERSE) == 1: df = data.dropna()
            else: df = data[ticker].dropna()
            
            # Need enough data for 200 SMA + previous 10 days
            if len(df) < 220: continue
            
            df = calculate_indicators(df)
            
            # SIMULATE THE LAST 10 DAYS
            # Iterating from 10 days ago (-10) to yesterday (-1)
            for i in range(-10, -1): 
                curr = df.iloc[i]
                prev = df.iloc[i-1]
                future_prices = df.iloc[i+1:] # Future data relative to loop
                
                # --- STRATEGY RULES ---
                # 1. Base Gates
                is_uptrend = (curr['Close'] > curr['SMA_200']) and (curr['ADX'] > 15)
                dist_to_ema = (curr['Close'] - curr['EMA_20']) / curr['EMA_20']
                is_pullback = (abs(dist_to_ema) < 0.03) and (curr['RSI'] < 60)
                
                # 2. Trigger Logic
                avg_vol = df['Volume'].rolling(20).mean().iloc[i]
                if pd.isna(avg_vol) or avg_vol == 0: avg_vol = 1
                
                basic_trigger = (curr['Close'] > curr['Open']) or (curr['Close'] > prev['High'])
                basic_vol = curr['Volume'] > (avg_vol * 0.7)
                
                # We only track "STRONG BUY" for this backtest to prove high conviction
                strong_trend = curr['ADX'] > 25
                strong_trigger = curr['Close'] > prev['High']
                strong_vol = curr['Volume'] > avg_vol
                
                if is_uptrend and is_pullback and basic_trigger and basic_vol and strong_trend and strong_trigger and strong_vol:
                    
                    # RECORD TRADE
                    entry_price = curr['Close']
                    entry_date = df.index[i].date()
                    current_price = df.iloc[-1]['Close']
                    
                    # Risk Mgmt
                    stop_loss = entry_price - (2 * curr['ATR'])
                    target = entry_price + (3 * curr['ATR'])
                    
                    outcome = "OPEN"
                    exit_price = current_price
                    
                    # Check if Stopped or Target Hit
                    for date, row in future_prices.iterrows():
                        if row['Low'] < stop_loss:
                            outcome = "STOPPED"
                            exit_price = stop_loss
                            break
                        if row['High'] > target:
                            outcome = "TARGET"
                            exit_price = target
                            break
                    
                    pnl_pct = (exit_price - entry_price) / entry_price
                    
                    trades.append({
                        "Ticker": ticker,
                        "Entry Date": entry_date,
                        "Entry Price": round(entry_price, 2),
                        "Exit Price": round(exit_price, 2),
                        "Outcome": outcome,
                        "P&L %": round(pnl_pct * 100, 2)
                    })
                    
        except Exception as e:
            continue

    # -------------------------------------------------------------------------
    # 4. REPORTING
    # -------------------------------------------------------------------------
    print("\n" + "="*60)
    print(f"BACKTEST RESULTS (Strong Buys - Last 10 Days)")
    print("="*60)
    
    if not trades:
        print("No STRONG BUY signals found in the last 10 days.")
    else:
        results_df = pd.DataFrame(trades)
        # Sort by Date
        results_df = results_df.sort_values(by="Entry Date")
        
        print(results_df.to_string(index=False))
        
        print("-" * 60)
        avg_return = results_df['P&L %'].mean()
        win_rate = len(results_df[results_df['P&L %'] > 0]) / len(results_df) * 100
        
        print(f"Total Signals: {len(trades)}")
        print(f"Average Return (Unrealized): {avg_return:.2f}%")
        print(f"Win Rate: {win_rate:.1f}%")
        print("="*60)

if __name__ == "__main__":
    run_backtest()
