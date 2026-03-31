import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import time
import plotly.graph_objects as go

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

def calculate_vwap(df):
    df['Typical_Price'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['VWAP'] = (df['Typical_Price'] * df['Volume']).groupby(df.index.date).cumsum() / df['Volume'].groupby(df.index.date).cumsum()
    return df['VWAP']

def detect_patterns(curr, prev):
    body = abs(curr['Close'] - curr['Open'])
    hl_range = curr['High'] - curr['Low']
    
    is_doji = body <= (hl_range * 0.1) if hl_range > 0 else False
    is_bull_engulf = (prev['Close'] < prev['Open']) and (curr['Close'] > curr['Open']) and (curr['Close'] > prev['Open']) and (curr['Open'] < prev['Close'])
    
    lower_wick = curr['Open'] - curr['Low'] if curr['Close'] > curr['Open'] else curr['Close'] - curr['Low']
    upper_wick = curr['High'] - curr['Close'] if curr['Close'] > curr['Open'] else curr['High'] - curr['Open']
    is_hammer = (lower_wick > 2 * body) and (upper_wick < body) and (body > 0)
    
    if is_bull_engulf: return "🔥 Bull Engulfing"
    elif is_hammer: return "🔨 Hammer"
    elif is_doji: return "⚖️ Doji"
    else: return "-"

# 🟢 FUNGSI KHUSUS UNTUK MESIN COPET KILAT
def jalankan_mesin_copet(nama_sektor, daftar_ticker):
    st.write(f"Mencari peluang copet terbaik di **{nama_sektor}** (TF: 5 Menit)...")
    bar_instan = st.progress(0, text="Mengumpulkan data Market Real-Time...")
    hasil_instan = []

    for i, ticker in enumerate(daftar_ticker):
        bar_instan.progress((i) / len(daftar_ticker), text=f"Menganalisa momentum {ticker}...")
        try:
            df = yf.Ticker(f"{ticker}.JK").history(period="5d", interval="5m")
            if not df.empty and len(df) > 25:
                df['RSI'] = calculate_rsi(df)
                df['MACD'], df['Signal'] = calculate_macd(df)
                df['MA5'] = df['Close'].rolling(window=5).mean()
                df['MA20'] = df['Close'].rolling(window=20).mean()
                df['Vol_MA5'] = df['Volume'].rolling(window=5).mean()
                df['VWAP'] = calculate_vwap(df)

                last_c = df.iloc[-1]
                prev_c = df.iloc[-2]
                cur_price = float(last_c['Close'])
                vwap_price = float(last_c['VWAP'])
                
                score = 0
                alasan = []

                if cur_price > last_c['MA5'] and last_c['MA5'] > last_c['MA20']: 
                    score += 2; alasan.append("Uptrend")
                elif last_c['MA5'] > last_c['MA20'] and prev_c['MA5'] <= prev_c['MA20']: 
                    score += 3; alasan.append("Golden Cross")
                elif cur_price < last_c['MA5'] and last_c['MA5'] < last_c['MA20']: 
                    score -= 2
                    
                if cur_price >= vwap_price: score += 1; alasan.append("Aman di atas VWAP")
                if last_c['RSI'] < 30: score += 2; alasan.append("Oversold")
                if last_c['MACD'] > last_c['Signal']: score += 1; alasan.append("MACD Bullish")
                if last_c['Volume'] > (last_c['Vol_MA5'] * 1.5): score += 2; alasan.append("Volume Surge")
                
                pola = detect_patterns(last_c, prev_c)
                if pola != "-": score += 2; alasan.append(pola)

                support = df['Low'].tail(20).min()
                
                if score > 0: 
                    hasil_instan.append({
                        "Saham": ticker, "Harga": cur_price, "VWAP": vwap_price,
                        "Support": support, "Score": score,
                        "Alasan": " + ".join(alasan) if alasan else "Momentum Netral"
                    })
        except Exception as e:
            pass
    
    bar_instan.empty()

    if hasil_instan:
        hasil_instan.sort(key=lambda x: x['Score'], reverse=True)
        top_5 = hasil_instan[:5] # Selalu ambil 5 terbaik
        
        st.success(f"✅ **Ditemukan {len(top_5)} Saham Copet Terbaik dari {nama_sektor}:**")
        
        for rank, item in enumerate(top_5):
            plan_entry = f"HAKA" if item['Harga'] > item['VWAP'] else "BOW (Tunggu Pantulan)"
            cutloss = item['Support'] * 0.98
            target = item['Harga'] * 1.03
            
            # 🟢 FIX HTML: Dihapus semua indentasi kiri agar tidak bocor jadi Code Block
            card_html = f"""<div style="background-color: #f8fafc; border-left: 5px solid #22c55e; padding: 15px; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
<h4 style="margin-top: 0; color: #1e293b;">#{rank+1} &nbsp; <b>{item['Saham']}</b> &nbsp; <span style="font-size:14px; color:#64748b; font-weight:normal;">(Skor AI: {item['Score']}/10)</span></h4>
<div style="display:flex; justify-content:space-between; margin-top:10px; flex-wrap:wrap; gap:10px;">
<div><b>Harga:</b> Rp {item['Harga']:,.0f}</div>
<div><b>VWAP:</b> Rp {item['VWAP']:,.0f}</div>
<div><b style="color:#22c55e;">Aksi:</b> {plan_entry}</div>
<div><b style="color:#ef4444;">Cutloss:</b> < Rp {cutloss:,.0f}</div>
<div><b style="color:#3b82f6;">Target:</b> Rp {target:,.0f}</div>
</div>
<div style="margin-top:10px; font-size:13px; color:#f59e0b;"><b>Sinyal:</b> {item['Alasan']}</div>
</div>"""
            st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ Market sedang lesu. Tidak ada saham di {nama_sektor} yang memenuhi kriteria copet saat ini.")


# --- FUNGSI UTAMA HALAMAN TEKNIKAL ---
def jalankan_teknikal():
    
    if 'teknikal_data' not in st.session_state: st.session_state['teknikal_data'] = None
    if 'teknikal_date' not in st.session_state: st.session_state['teknikal_date'] = None
    if 'teknikal_tf' not in st.session_state: st.session_state['teknikal_tf'] = None
    
    # 🟢 DATABASE SEKTOR DINAMIS (Disimpan di Memori)
    if 'db_sektor' not in st.session_state:
        st.session_state['db_sektor'] = {
            "🪙 Logam & Emas": ["MDKA", "PSAB", "BRMS", "ARCI", "ANTM", "INCO", "HRUM", "MBMA", "NCKL", "TINS"],
            "⛏️ Energi & Batu Bara": ["ADRO", "PTBA", "ITMG", "BUMI", "DOID", "INDY", "BREN", "CUAN", "PGEO", "ENRG"],
            "🏥 Kesehatan & Farmasi": ["MIKA", "HEAL", "SILO", "KLBF", "SIDO", "PRDA", "CARE", "PEHA"],
            "🏦 Bank & Finansial": ["BBCA", "BBRI", "BBNI", "BMRI", "BRIS", "ARTO", "BBYB", "BBTN", "NISP", "BNGA"],
            "🛒 Konsumer & Retail": ["ICBP", "INDF", "AMRT", "MIDI", "MYOR", "UNVR", "MAPI", "ACES", "AMMN"],
            "📱 Teknologi & Digital": ["GOTO", "BUKA", "EMTK", "WIRG", "BELI", "MLPT", "WIFI"]
        }

    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e293b, #0f172a); padding: 25px 30px; border-radius: 12px; border-left: 8px solid #f59e0b; margin-bottom: 25px; box-shadow: 0 10px 15px rgba(0,0,0,0.2);">
        <h2 style="color: #ffffff; margin: 0; font-weight: 800; letter-spacing: 0.5px;">⏱️ Radar Teknikal Pro V3.0 ⚡</h2>
        <p style="color: #94a3b8; margin-top: 8px; font-size: 15px; margin-bottom: 0;">Gunakan Tab <b>Top 5 Copet Kilat</b> untuk mencari sinyal instan dari saham favorit Anda untuk di-tradingkan hari ini!</p>
    </div>
    """, unsafe_allow_html=True)

    tab_instan, tab_massal, tab_single = st.tabs(["🚀 Top 5 Copet Kilat (Instan)", "⚙️ Mass Screener (Advance)", "🔍 Bedah Chart Tunggal"])

    # ==============================================================================
    # TAB 1: TOP 5 COPET KILAT (KARTU SEKTORAL UNIK & CUSTOM)
    # ==============================================================================
    with tab_instan:
        st.markdown("### ⭐ Cari Saham Copet Terbaik Hari Ini")
        
        default_wl = st.session_state.get('watchlist', "BREN, CUAN, BRPT, AMMN, GOTO, BBCA, BMRI, TLKM, ASII, PGAS")
        
        if st.button("🚀 CARI DARI WATCHLIST FAVORIT SAYA", type="primary", use_container_width=True):
            tickers = [t.strip().upper() for t in default_wl.split(',') if t.strip()]
            if not tickers: st.error("Watchlist Anda kosong! Silakan atur daftar saham di Tab 'Mass Screener'.")
            else: jalankan_mesin_copet("Watchlist Favorit", tickers)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")

        # 🟢 BAGIAN MANAJEMEN SEKTOR (ICON KANAN ATAS)
        col_title, col_manage = st.columns([3, 1])
        with col_title:
            st.markdown("### 🗂️ Radar Copet Sektoral")
            st.write("Klik salah satu kartu di bawah untuk mencari 5 saham terbaik di sektor tersebut.")
        with col_manage:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("⚙️ Kelola & Tambah Sektor"):
                st.markdown("#### ➕ Tambah Sektor Baru")
                new_sec_name = st.text_input("Nama Sektor (Cth: 🚀 AI Tech)")
                new_sec_stocks = st.text_input("Kode Saham (Pisahkan dengan koma)")
                if st.button("💾 Simpan Sektor Baru", use_container_width=True):
                    if new_sec_name and new_sec_stocks:
                        st.session_state['db_sektor'][new_sec_name] = [s.strip().upper() for s in new_sec_stocks.split(",")]
                        st.success(f"Sektor {new_sec_name} ditambahkan!")
                
                st.markdown("---")
                st.markdown("#### 📝 Edit Sektor yang Ada")
                for sec_name, sec_stocks in list(st.session_state['db_sektor'].items()):
                    edit_stocks = st.text_input(f"Edit Saham: {sec_name}", value=", ".join(sec_stocks), key=f"edit_{sec_name}")
                    if edit_stocks != ", ".join(sec_stocks):
                        st.session_state['db_sektor'][sec_name] = [s.strip().upper() for s in edit_stocks.split(",")]
                    
                    if st.button(f"🗑️ Hapus Sektor {sec_name}", key=f"del_{sec_name}"):
                        del st.session_state['db_sektor'][sec_name]
                        st.rerun() # Memuat ulang agar kartu langsung hilang

        st.markdown("<br>", unsafe_allow_html=True)

        # 🟢 GRID KARTU SEKTOR UNIK (MENGGABUNGKAN HTML & STREAMLIT BUTTON)
        sektor_items = list(st.session_state['db_sektor'].items())
        cols = st.columns(3)
        
        for i, (nama_sektor, saham_list) in enumerate(sektor_items):
            with cols[i % 3]:
                # Desain Kartu HTML Unik (Bagian Atas)
                # Dibuat rapat rata kiri agar tidak bocor jadi Code Block
                html_kartu = f"""<div style="background: linear-gradient(135deg, #ffffff, #f1f5f9); padding: 15px; border-radius: 12px 12px 0 0; border-top: 5px solid #3b82f6; border-left: 1px solid #cbd5e1; border-right: 1px solid #cbd5e1; text-align: center; height: 110px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
<div style="font-size: 16px; font-weight: 900; color: #1e293b; margin-bottom: 8px;">{nama_sektor}</div>
<div style="font-size: 12px; color: #64748b; line-height: 1.4; font-weight: 500;">{', '.join(saham_list[:6])}{'...' if len(saham_list)>6 else ''}</div>
</div>"""
                st.markdown(html_kartu, unsafe_allow_html=True)
                
                # Tombol Streamlit Menyatu dengan Kartu (Bagian Bawah)
                if st.button(f"⚡ Scan {nama_sektor.split(' ')[0]}", key=f"btn_scan_{nama_sektor}", use_container_width=True):
                    jalankan_mesin_copet(nama_sektor, saham_list)
                
                st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)


    # ==============================================================================
    # TAB 2: MASS SCREENER ADVANCE
    # ==============================================================================
    with tab_massal:
        st.markdown("<div style='background-color: #f8fafc; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1.5, 1, 1])
        
        with col1:
            pilihan_indeks = st.selectbox("🎯 Target Screener:", ["Watchlist Custom", "LQ45 (Saham Likuid)", "IDX30 (Bluechip)"])
            if pilihan_indeks == "Watchlist Custom":
                default_wl2 = st.session_state.get('watchlist', "BBCA, BREN, CUAN, AMMN, GOTO")
                saham_input2 = st.text_area("📝 Daftar Saham (Ubah Watchlist di sini):", default_wl2, height=68, key="txt_wl2")
        
        with col2:
            timeframe_pilihan = st.selectbox("⏱️ Timeframe (TF):", ["1 Hari (Daily)", "1 Jam (60m)", "30 Menit (30m)", "15 Menit (15m)", "5 Menit (5m)"], index=0)

        with col3:
            kemarin = datetime.date.today() - datetime.timedelta(days=1)
            tanggal_input = st.date_input("📅 Tanggal (Khusus Daily):", value=(kemarin, kemarin), max_value=datetime.date.today())
            
        st.markdown("</div><br>", unsafe_allow_html=True)

        tf_map = {"1 Hari (Daily)": "1d", "1 Jam (60m)": "60m", "30 Menit (30m)": "30m", "15 Menit (15m)": "15m", "5 Menit (5m)": "5m"}
        interval_yf = tf_map[timeframe_pilihan]

        if st.button("⚙️ Mulai Mass Screening", use_container_width=True):
            if pilihan_indeks == "Watchlist Custom": 
                tickers_to_scan = [t.strip().upper() for t in saham_input2.split(',') if t.strip()]
                st.session_state['watchlist'] = saham_input2 
            elif pilihan_indeks == "LQ45 (Saham Likuid)": tickers_to_scan = [t.strip() for t in "ACES, ADRO, AKRA, AMMN, AMRT, ANTM, ARTO, ASII, BBCA, BBNI, BBRI, BBTN, BFIN, BMRI, BRIS, BRPT, BUKA, CPIN, EMTK, ESSA, EXCL, GOTO, HRUM, ICBP, INCO, INDF, INKP, INTP, ITMG, KLBF, MAPI, MBMA, MDKA, MEDC, MTEL, PGAS, PGEO, PTBA, SIDO, SMGR, SRTG, TLKM, TOWR, UNTR, UNVR".split(",")]
            elif pilihan_indeks == "IDX30 (Bluechip)": tickers_to_scan = [t.strip() for t in "ADRO, AKRA, AMMN, AMRT, ANTM, ARTO, ASII, BBCA, BBNI, BBRI, BMRI, BRPT, BUKA, CPIN, ESSA, EXCL, GOTO, HRUM, ICBP, INDF, INKP, INTP, ITMG, KLBF, MDKA, MEDC, PGAS, PTBA, TLKM, UNTR".split(",")]

            progress_bar = st.progress(0, text=f"Scanning ({timeframe_pilihan})...")
            hasil_teknikal = []

            for i, ticker in enumerate(tickers_to_scan):
                progress_bar.progress((i) / len(tickers_to_scan), text=f"Menganalisa {ticker}...")
                try:
                    if interval_yf == "1d":
                        if len(tanggal_input) == 2: start_date, end_date = tanggal_input
                        elif len(tanggal_input) == 1: start_date = end_date = tanggal_input[0]
                        df = yf.Ticker(f"{ticker}.JK").history(start=start_date - datetime.timedelta(days=90), end=end_date + datetime.timedelta(days=1), interval=interval_yf)
                        if not df.empty: df = df.loc[:end_date.strftime("%Y-%m-%d")]
                    else:
                        fetch_period = "1mo" if interval_yf in ["60m", "30m"] else "5d"
                        df = yf.Ticker(f"{ticker}.JK").history(period=fetch_period, interval=interval_yf)
                    
                    if not df.empty and len(df) > 25:
                        df['RSI'] = calculate_rsi(df)
                        df['MACD'], df['Signal'] = calculate_macd(df)
                        df['MA5'] = df['Close'].rolling(window=5).mean()
                        df['MA20'] = df['Close'].rolling(window=20).mean()
                        df['Vol_MA5'] = df['Volume'].rolling(window=5).mean()
                        df['VWAP'] = calculate_vwap(df)

                        last_c = df.iloc[-1]; prev_c = df.iloc[-2]
                        cur_price = float(last_c['Close']); rsi_val = float(last_c['RSI']); vwap_val = float(last_c['VWAP'])
                        waktu_candle = last_c.name.strftime("%d %b %H:%M") if interval_yf != "1d" else last_c.name.strftime("%d %b %Y")
                        
                        if cur_price > last_c['MA5'] and last_c['MA5'] > last_c['MA20']: trend_status = "🚀 UPTREND"
                        elif last_c['MA5'] > last_c['MA20'] and prev_c['MA5'] <= prev_c['MA20']: trend_status = "🔥 GOLDEN CROSS"
                        elif cur_price < last_c['MA5'] and last_c['MA5'] < last_c['MA20']: trend_status = "🩸 DOWNTREND"
                        elif last_c['MA5'] < last_c['MA20'] and prev_c['MA5'] >= prev_c['MA20']: trend_status = "💀 DEAD CROSS"
                        else: trend_status = "⚖️ SIDEWAYS"

                        if rsi_val < 30: rsi_status = "🟢 OVERSOLD"
                        elif rsi_val > 70: rsi_status = "🔴 OVERBOUGHT"
                        else: rsi_status = "🟡 NEUTRAL"

                        vol_surge = "💥 ADA LONJAKAN" if last_c['Volume'] > (last_c['Vol_MA5'] * 1.5) else "Normal"
                        macd_status = "📈 Bullish" if last_c['MACD'] > last_c['Signal'] else "📉 Bearish"
                        vwap_status = "✅ Di Atas VWAP" if cur_price >= vwap_val else "⚠️ Di Bawah VWAP"
                        pola_candle = detect_patterns(last_c, prev_c)

                        hasil_teknikal.append({
                            "Saham": ticker, "Waktu": waktu_candle, "Harga": f"Rp {cur_price:,.0f}", "Pola": pola_candle, 
                            "VWAP": f"Rp {vwap_val:,.0f} ({vwap_status})", "RSI": f"{rsi_val:.1f} ({rsi_status})", 
                            "Trend": trend_status, "MACD": macd_status, "Vol Surge": vol_surge
                        })
                except: pass
                time.sleep(0.1)

            progress_bar.empty()
            if hasil_teknikal:
                st.session_state['teknikal_data'] = pd.DataFrame(hasil_teknikal)
                st.session_state['teknikal_date'] = datetime.datetime.now()
                st.session_state['teknikal_tf'] = timeframe_pilihan
            else:
                st.session_state['teknikal_data'] = "KOSONG"

        if isinstance(st.session_state['teknikal_data'], pd.DataFrame):
            df_hasil = st.session_state['teknikal_data']
            
            def hitung_skor_ai(row):
                skor = 0
                if "UPTREND" in row['Trend'] or "GOLDEN CROSS" in row['Trend']: skor += 3
                if "Di Atas" in row['VWAP']: skor += 2
                if "OVERSOLD" in row['RSI']: skor += 2
                if "Bullish" in row['MACD']: skor += 1
                if "LONJAKAN" in row['Vol Surge']: skor += 2
                if "🔥" in row['Pola'] or "🔨" in row['Pola']: skor += 2
                return skor
            
            df_hasil['Skor AI'] = df_hasil.apply(hitung_skor_ai, axis=1)
            top_5_df = df_hasil.sort_values(by='Skor AI', ascending=False).head(5)

            st.markdown("#### ⭐ Top 5 Rekomendasi AI (Dari Hasil Scan Massal)")
            top_5_list = top_5_df.to_dict('records')
            
            if top_5_list:
                cols = st.columns(len(top_5_list))
                for i, item in enumerate(top_5_list):
                    with cols[i]:
                        # 🟢 FIX HTML
                        ai_card = f"""<div style="background: linear-gradient(135deg, #1e293b, #0f172a); padding: 15px 10px; border-radius: 8px; text-align: center; border-bottom: 4px solid #22c55e; box-shadow: 0 4px 6px rgba(0,0,0,0.15);">
<div style="font-size: 20px; font-weight: 900; color: #4ade80; letter-spacing: 1px;">{item['Saham']}</div>
<div style="font-size: 13px; color: #94a3b8; margin-top: 5px; font-weight: bold;">{item['Harga']}</div>
<div style="font-size: 12px; font-weight: 800; color: #facc15; margin-top: 8px; background: rgba(255,255,255,0.05); padding: 3px; border-radius: 4px;">Skor AI: {item['Skor AI']}/12</div>
</div>"""
                        st.markdown(ai_card, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            opsi_filter = st.radio("Filter Tabel Lengkap:", ["Tampilkan Semua", "Hanya Uptrend/Golden Cross", "Hanya Oversold", "Ada Lonjakan Volume"], horizontal=True)
            
            df_tampil = df_hasil.drop(columns=['Skor AI']).copy() 
            if "Uptrend" in opsi_filter: df_tampil = df_tampil[df_tampil['Trend'].str.contains("UPTREND|GOLDEN CROSS", na=False)]
            elif "Oversold" in opsi_filter: df_tampil = df_tampil[df_tampil['RSI'].str.contains("OVERSOLD", na=False)]
            elif "Volume" in opsi_filter: df_tampil = df_tampil[df_tampil['Vol Surge'].str.contains("LONJAKAN", na=False)]

            def color_tek(val):
                if isinstance(val, str):
                    if any(x in val for x in ["OVERSOLD", "UPTREND", "GOLDEN CROSS", "Bullish", "LONJAKAN", "Di Atas", "🔥", "🔨"]): return 'color: #2ecc71; font-weight: bold; background-color: rgba(46, 204, 113, 0.1);'
                    elif any(x in val for x in ["OVERBOUGHT", "DOWNTREND", "DEAD CROSS", "Bearish", "Di Bawah"]): return 'color: #e74c3c; font-weight: bold; background-color: rgba(231, 76, 60, 0.1);'
                return ''

            st.dataframe(df_tampil.style.applymap(color_tek, subset=['Pola', 'VWAP', 'RSI', 'Trend', 'MACD', 'Vol Surge']), use_container_width=True, hide_index=True)


    # ==============================================================================
    # TAB 3: BEDAH CHART TUNGGAL
    # ==============================================================================
    with tab_single:
        st.markdown("<div style='background-color: #f8fafc; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
        col_inp1, col_inp2, col_inp3 = st.columns([1.5, 2, 1])
        with col_inp1: single_ticker = st.text_input("🔍 Kode Saham:", "BREN", key="single_tek").upper()
        with col_inp2: single_tf = st.selectbox("⏱️ Timeframe Analisa:", ["1 Hari (Daily)", "1 Jam (60m)", "30 Menit (30m)", "15 Menit (15m)", "5 Menit (5m)"], index=0, key="tf_single")
        with col_inp3:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            btn_single_tek = st.button("🚀 Load Chart", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if btn_single_tek:
            if not single_ticker: st.error("Masukkan kode saham."); st.stop()

            tf_map_single = {"1 Hari (Daily)": "1d", "1 Jam (60m)": "60m", "30 Menit (30m)": "30m", "15 Menit (15m)": "15m", "5 Menit (5m)": "5m"}
            s_interval = tf_map_single[single_tf]
            
            my_bar = st.progress(50, text="Mengambil data chart interaktif...")
            
            try:
                if s_interval == "1d": df_chart = yf.Ticker(f"{single_ticker}.JK").history(period="6mo", interval="1d")
                else: df_chart = yf.Ticker(f"{single_ticker}.JK").history(period="1mo" if s_interval in ["60m", "30m"] else "5d", interval=s_interval)
                
                df_daily = yf.Ticker(f"{single_ticker}.JK").history(period="1mo", interval="1d")
                
                if df_chart.empty or len(df_chart) < 25 or df_daily.empty:
                    st.error("Data tidak ditemukan."); my_bar.empty(); st.stop()

                df_chart['RSI'] = calculate_rsi(df_chart); df_chart['MACD'], df_chart['Signal'] = calculate_macd(df_chart)
                df_chart['MA5'] = df_chart['Close'].rolling(window=5).mean(); df_chart['MA20'] = df_chart['Close'].rolling(window=20).mean()
                df_chart['Vol_MA5'] = df_chart['Volume'].rolling(window=5).mean(); df_chart['VWAP'] = calculate_vwap(df_chart)

                last_c = df_chart.iloc[-1]; prev_c = df_chart.iloc[-2]
                cur_price = float(last_c['Close']); vwap_price = float(last_c['VWAP'])

                prev_day = df_daily.iloc[-2]
                pivot = (prev_day['High'] + prev_day['Low'] + prev_day['Close']) / 3
                r1 = (pivot * 2) - prev_day['Low']; s1 = (pivot * 2) - prev_day['High']
                r2 = pivot + (prev_day['High'] - prev_day['Low']); s2 = pivot - (prev_day['High'] - prev_day['Low'])
                
                my_bar.empty()

                # --- GRAFIK CANDLESTICK + VWAP (PLOTLY) ---
                df_plot = df_chart.tail(90).reset_index() 
                if 'index' in df_plot.columns: df_plot.rename(columns={'index': 'Date'}, inplace=True)
                if 'Datetime' in df_plot.columns: df_plot.rename(columns={'Datetime': 'Date'}, inplace=True)

                fig = go.Figure()
                fig.add_trace(go.Candlestick(x=df_plot['Date'], open=df_plot['Open'], high=df_plot['High'], low=df_plot['Low'], close=df_plot['Close'], name='Candle', increasing_line_color='#26a69a', decreasing_line_color='#ef5350'))
                fig.add_trace(go.Scatter(x=df_plot['Date'], y=df_plot['MA5'], mode='lines', line=dict(color='#2962ff', width=1.5), name='MA5'))
                fig.add_trace(go.Scatter(x=df_plot['Date'], y=df_plot['MA20'], mode='lines', line=dict(color='#ff9800', width=1.5), name='MA20'))
                fig.add_trace(go.Scatter(x=df_plot['Date'], y=df_plot['VWAP'], mode='lines', line=dict(color='#9c27b0', width=2, dash='dash'), name='VWAP'))

                fig.update_layout(title=dict(text=f"Chart {single_ticker} (TF: {single_tf})", font=dict(size=14)), yaxis_title="Harga (Rp)", xaxis_title="", template="plotly_white", xaxis_rangeslider_visible=False, height=500, margin=dict(l=10, r=10, t=40, b=10), hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                st.plotly_chart(fig, use_container_width=True)

                # --- PIVOT BOX ---
                # 🟢 FIX HTML
                pivot_box = f"""<div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 10px; margin-top: 10px;">
<div style="flex: 1; background: #fffbeb; padding: 15px; border-radius: 8px; text-align: center; border-bottom: 3px solid #f59e0b; color: #1e293b;">
<div style="font-size: 11px; font-weight: bold;">📈 RESISTANCE 2</div><div style="font-size: 18px; font-weight: 800;">Rp {r2:,.0f}</div>
</div>
<div style="flex: 1; background: #fffbeb; padding: 15px; border-radius: 8px; text-align: center; border-bottom: 3px solid #fbbf24; color: #1e293b;">
<div style="font-size: 11px; font-weight: bold;">🎯 RESISTANCE 1</div><div style="font-size: 18px; font-weight: 800;">Rp {r1:,.0f}</div>
</div>
<div style="flex: 1; background: #f8fafc; padding: 15px; border-radius: 8px; text-align: center; border-bottom: 3px solid #94a3b8; color: #1e293b;">
<div style="font-size: 11px; font-weight: bold;">⚖️ PIVOT POINT</div><div style="font-size: 18px; font-weight: 800;">Rp {pivot:,.0f}</div>
</div>
<div style="flex: 1; background: #eff6ff; padding: 15px; border-radius: 8px; text-align: center; border-bottom: 3px solid #60a5fa; color: #1e293b;">
<div style="font-size: 11px; font-weight: bold;">📉 SUPPORT 1</div><div style="font-size: 18px; font-weight: 800;">Rp {s1:,.0f}</div>
</div>
<div style="flex: 1; background: #fef2f2; padding: 15px; border-radius: 8px; text-align: center; border-bottom: 3px solid #ef4444; color: #1e293b;">
<div style="font-size: 11px; font-weight: bold;">✂️ SUPPORT 2</div><div style="font-size: 18px; font-weight: 800;">Rp {s2:,.0f}</div>
</div>
</div>"""
                st.markdown(pivot_box, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Gagal membedah chart. Error: {e}")
