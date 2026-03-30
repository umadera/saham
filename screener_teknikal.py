import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import time

# --- FUNGSI KALKULASI INDIKATOR TEKNIKAL PANDAS ---
def calculate_rsi(data, periods=14):
    close_delta = data['Close'].diff()
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)
    ma_up = up.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
    ma_down = down.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
    rsi = ma_up / ma_down
    rsi = 100 - (100 / (1 + rsi))
    return rsi

def calculate_macd(data, fast=12, slow=26, signal=9):
    exp1 = data['Close'].ewm(span=fast, adjust=False).mean()
    exp2 = data['Close'].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line

# --- FUNGSI UTAMA HALAMAN TEKNIKAL ---
def jalankan_teknikal():
    st.title("📊 Screener Teknikal Pro ⚡")
    st.markdown("Memindai saham berdasarkan indikator teknikal: **RSI, Moving Average (MA5 & MA20), MACD, dan Volume Breakout**.")

    with st.container():
        col1, col2 = st.columns([1, 2])
        with col1:
            pilihan_indeks = st.selectbox("Pilih Indeks / Kategori:", ["LQ45 (Saham Likuid)", "IDX30 (Bluechip)", "Watchlist Custom"])
        with col2:
            if pilihan_indeks == "Watchlist Custom":
                saham_input = st.text_input("Ketik Kode Saham (Pisahkan dengan koma):", "BBCA, BREN, CUAN, AMMN, GOTO")
            else:
                st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)
                st.info("Sistem akan menarik data 6 bulan terakhir untuk kalkulasi teknikal.")

    if st.button("🚀 Mulai Scanning Teknikal", use_container_width=True):
        if pilihan_indeks == "Watchlist Custom":
            tickers_to_scan = [t.strip().upper() for t in saham_input.split(',') if t.strip()]
        elif pilihan_indeks == "LQ45 (Saham Likuid)":
            tickers_to_scan = [t.strip() for t in "ACES, ADRO, AKRA, AMMN, AMRT, ANTM, ARTO, ASII, BBCA, BBNI, BBRI, BBTN, BFIN, BMRI, BRIS, BRPT, BUKA, CPIN, EMTK, ESSA, EXCL, GOTO, HRUM, ICBP, INCO, INDF, INKP, INTP, ITMG, KLBF, MAPI, MBMA, MDKA, MEDC, MTEL, PGAS, PGEO, PTBA, SIDO, SMGR, SRTG, TLKM, TOWR, UNTR, UNVR".split(",")]
        elif pilihan_indeks == "IDX30 (Bluechip)":
            tickers_to_scan = [t.strip() for t in "ADRO, AKRA, AMMN, AMRT, ANTM, ARTO, ASII, BBCA, BBNI, BBRI, BMRI, BRPT, BUKA, CPIN, ESSA, EXCL, GOTO, HRUM, ICBP, INDF, INKP, INTP, ITMG, KLBF, MDKA, MEDC, PGAS, PTBA, TLKM, UNTR".split(",")]

        if not tickers_to_scan:
            st.warning("Masukkan minimal 1 kode saham.")
            st.stop()

        progress_bar = st.progress(0, text="Mengunduh data pasar (Yahoo Finance)...")
        hasil_teknikal = []

        for i, ticker in enumerate(tickers_to_scan):
            progress_bar.progress((i) / len(tickers_to_scan), text=f"Mengkalkulasi {ticker} ({i+1}/{len(tickers_to_scan)})...")
            try:
                # Mengambil data 6 bulan terakhir untuk kalkulasi MA dan MACD yang akurat
                df = yf.Ticker(f"{ticker}.JK").history(period="6mo")
                if not df.empty and len(df) > 30:
                    df['RSI'] = calculate_rsi(df)
                    df['MACD'], df['Signal'] = calculate_macd(df)
                    df['MA5'] = df['Close'].rolling(window=5).mean()
                    df['MA20'] = df['Close'].rolling(window=20).mean()
                    df['Vol_MA5'] = df['Volume'].rolling(window=5).mean()

                    # Data hari terakhir
                    last = df.iloc[-1]
                    prev = df.iloc[-2]

                    current_price = last['Close']
                    rsi_val = last['RSI']
                    
                    # Logika Sinyal Trend MA
                    if current_price > last['MA5'] and last['MA5'] > last['MA20']:
                        trend_status = "🚀 UPTREND"
                    elif last['MA5'] > last['MA20'] and prev['MA5'] <= prev['MA20']:
                        trend_status = "🔥 GOLDEN CROSS"
                    elif current_price < last['MA5'] and last['MA5'] < last['MA20']:
                        trend_status = "🩸 DOWNTREND"
                    else:
                        trend_status = "⚖️ SIDEWAYS"

                    # Logika Sinyal RSI
                    if rsi_val < 30:
                        rsi_status = "🟢 OVERSOLD (Pantau)"
                    elif rsi_val > 70:
                        rsi_status = "🔴 OVERBOUGHT (Rentan)"
                    else:
                        rsi_status = "🟡 NEUTRAL"

                    # Logika Volume Breakout (Volume hari ini > 1.5x rata-rata 5 hari)
                    vol_surge = "💥 ADA LONJAKAN" if last['Volume'] > (last['Vol_MA5'] * 1.5) else "Normal"

                    # Logika MACD
                    macd_status = "📈 Bullish" if last['MACD'] > last['Signal'] else "📉 Bearish"

                    hasil_teknikal.append({
                        "Saham": ticker,
                        "Harga Terakhir": f"Rp {current_price:,.0f}",
                        "RSI (14)": f"{rsi_val:.1f} ({rsi_status})",
                        "Trend (MA5 & MA20)": trend_status,
                        "MACD": macd_status,
                        "Volume Surge": vol_surge
                    })
            except Exception as e:
                pass
            time.sleep(0.1) # Delay aman

        progress_bar.progress(100, text="✅ Scanning Selesai!")
        time.sleep(0.5)
        progress_bar.empty()

        if hasil_teknikal:
            df_hasil = pd.DataFrame(hasil_teknikal)
            
            # --- PEWARNAAN TABEL TEKNIKAL ---
            def color_technical(val):
                if isinstance(val, str):
                    if "OVERSOLD" in val or "UPTREND" in val or "GOLDEN CROSS" in val or "Bullish" in val or "LONJAKAN" in val:
                        return 'color: #2ecc71; font-weight: bold;'
                    elif "OVERBOUGHT" in val or "DOWNTREND" in val or "Bearish" in val:
                        return 'color: #e74c3c; font-weight: bold;'
                return ''

            st.success("🎯 **HASIL SCREENING TEKNIKAL:**")
            
            # Menerapkan warna ke dataframe
            styler = df_hasil.style.applymap(color_technical, subset=['RSI (14)', 'Trend (MA5 & MA20)', 'MACD', 'Volume Surge'])
            st.dataframe(styler, use_container_width=True, hide_index=True)
            
            st.markdown("""
            **💡 Panduan Membaca Sinyal Teknikal:**
            * **RSI Oversold:** Harga sudah turun terlalu dalam, potensi teknikal *rebound* (pantulan).
            * **Golden Cross / Uptrend:** Saham sedang berada dalam fase akumulasi harga naik.
            * **Volume Surge:** Terdapat ledakan volume transaksi hari ini dibanding rata-rata minggu lalu (ada *Big Money* yang beraksi).
            """)
        else:
            st.warning("Tidak ada data teknikal yang dapat dianalisa.")
