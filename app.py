import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import datetime
import altair as alt
import time
import json
import os
import streamlit.components.v1 as components 

# Mengatur konfigurasi halaman website
st.set_page_config(page_title="Screener Saham Pro", page_icon="📈", layout="wide")

# ==============================================================================
# 💾 SISTEM MINI DATABASE & CLOUD SECRETS (HYBRID)
# ==============================================================================
FILE_DATABASE = "config.json"

def muat_api_key():
    try:
        if "INVEZGO_API_KEY" in st.secrets:
            return st.secrets["INVEZGO_API_KEY"]
    except:
        pass 

    if os.path.exists(FILE_DATABASE):
        try:
            with open(FILE_DATABASE, "r") as f:
                data = json.load(f)
                return data.get("api_key", "")
        except:
            return ""
    return ""

def simpan_api_key(key):
    with open(FILE_DATABASE, "w") as f:
        json.dump({"api_key": key}, f)

# ==============================================================================
# 📦 DATA UTAMA BROKER BEI
# ==============================================================================
DARI_BROKER_NAMA_MAP = {
    "AD": "Sukadana Prima Sekuritas", "AF": "Harita Kencana Sekuritas", "AG": "Kiwoom Sekuritas Indonesia",
    "AH": "Shinhan Sekuritas Indonesia", "AI": "UOB Kay Hian Sekuritas", "AK": "UBS Sekuritas Indonesia",
    "AN": "Wanteg Sekuritas", "AO": "Erdikha Elit Sekuritas", "AP": "Pacific Sekuritas Indonesia",
    "AR": "Binaartha Sekuritas", "AT": "Phintraco Sekuritas", "AZ": "Sucor Sekuritas",
    "BB": "Verdhana Sekuritas Indonesia", "BF": "Inti Fikasa Sekuritas", "BK": "J.P. Morgan Sekuritas",
    "BQ": "Korea Investment & Sekuritas (KISI)", "BS": "Equity Sekuritas Indonesia", "BZ": "Batavia Prosperindo",
    "CC": "Mandiri Sekuritas", "CD": "Mega Capital Sekuritas", "CG": "Citigroup Sekuritas Indonesia",
    "CP": "KB Valbury Sekuritas", "CS": "Credit Suisse Sekuritas", "DD": "Makindo Sekuritas",
    "DH": "Sinarmas Sekuritas", "DM": "Masindo Artha Sekuritas", "DP": "DBS Vickers Sekuritas",
    "DR": "RHB Sekuritas Indonesia", "DX": "Bahana Sekuritas", "EL": "Evergreen Sekuritas",
    "EP": "MNC Sekuritas", "ES": "Ekokapital Sekuritas", "FO": "Forte Global Sekuritas",
    "FS": "Yuanta Sekuritas Indonesia", "FZ": "Waterfront Sekuritas", "GA": "BNC Sekuritas Indonesia",
    "GI": "Mahastra Andalan Sekuritas", "GR": "Panin Sekuritas", "GW": "HSBC Sekuritas Indonesia",
    "HD": "KGI Sekuritas Indonesia", "HP": "Henan Putihrai Sekuritas", "ID": "Anugerah Sekuritas",
    "IF": "Samuel Sekuritas Indonesia", "IH": "Pacific 2000 Sekuritas", "II": "Danatama Makmur Sekuritas",
    "IN": "Investindo Nusantara Sekuritas", "IP": "Indosurya Bersinar Sekuritas", "IT": "Inti Teladan Sekuritas",
    "IU": "Indo Capital Sekuritas", "KI": "Ciptadana Sekuritas Asia", "KK": "Phillip Sekuritas Indonesia",
    "KZ": "CLSA Sekuritas Indonesia", "LG": "Trimegah Sekuritas Indonesia", "LS": "Reliance Sekuritas",
    "MG": "Semesta Indovest Sekuritas", "MI": "Victoria Sekuritas", "MK": "Ekuator Swarna Sekuritas",
    "MS": "Morgan Stanley Sekuritas", "MU": "Minna Padi Investama", "NI": "BNI Sekuritas",
    "OD": "BRI Danareksa Sekuritas", "OK": "NET Sekuritas", "PC": "FAC Sekuritas Indonesia",
    "PD": "Indo Premier Sekuritas (IPOT)", "PF": "Danasakti Sekuritas", "PG": "Panca Global Sekuritas",
    "PO": "Pilarimas Investindo", "PP": "Aldiracita Sekuritas", "PS": "Paramitra Alfa Sekuritas",
    "RB": "Nikko Sekuritas Indonesia", "RF": "Buana Capital Sekuritas", "RG": "Profindo Sekuritas",
    "RO": "Nilai Inti Sekuritas", "RX": "Macquarie Sekuritas Indonesia", "SA": "Elit Sukses Sekuritas",
    "SC": "IMG Sekuritas", "SH": "Artha Sekuritas Indonesia", "SQ": "BCA Sekuritas",
    "TF": "Universal Broker Indonesia", "TP": "OCBC Sekuritas Indonesia", "TS": "Dwidana Sakti Sekuritas",
    "TX": "Dhanawibawa Sekuritas", "XA": "NH Korindo Sekuritas", "XC": "Ajaib Sekuritas Asia",
    "XL": "Stockbit Sekuritas Digital", "YB": "Jasa Utama Capital Sekuritas", "YJ": "Lotus Andalan Sekuritas",
    "YO": "Amantara Sekuritas", "YP": "Mirae Asset Sekuritas", "YU": "CGS International Sekuritas",
    "ZP": "Maybank Sekuritas Indonesia", "ZR": "Bumiputera Sekuritas"
}

# --- FUNGSI BANTUAN FORMAT ANGKA ---
def format_rupiah(angka):
    if pd.isna(angka): return "Rp 0"
    if abs(angka) >= 1_000_000_000:
        return f"Rp {angka / 1_000_000_000:.2f} Miliar" 
    elif abs(angka) >= 1_000_000:
        return f"Rp {angka / 1_000_000:.2f} Juta" 
    else:
        return f"Rp {angka:,.0f}"

def format_lot(angka):
    if pd.isna(angka): return "0 Lot"
    angka = abs(angka) 
    if angka >= 1_000_000:
        return f"{angka / 1_000_000:.1f}Juta Lot"
    elif angka >= 1_000:
        return f"{angka / 1_000:.1f}Ribu Lot"
    else:
        return f"{angka:,.0f} Lot"

# --- FUNGSI KATEGORI WARNA BROKER ---
def get_kategori_broker(kode):
    asing = ['AK', 'ZP', 'RX', 'KZ', 'BK', 'CS', 'CG', 'MS', 'YU', 'GW', 'DX', 'DP', 'BQ', 'BB', 'FS', 'HD', 'AG', 'AH', 'AI', 'DR']
    ritel = ['CC', 'XL', 'DH', 'PD', 'YP', 'NI', 'EP', 'OD', 'XC', 'SQ', 'GR', 'CP', 'MG', 'YB', 'AZ', 'IF', 'HP', 'KK', 'LS', 'SH', 'IN', 'YJ']
    institusi = ['LG', 'KI', 'RF', 'PP', 'TF', 'TP', 'RO', 'MU', 'XA'] 
    
    if kode in asing: return 'Bule (Asing)', '#9b59b6' 
    elif kode in ritel: return 'Investor Biasa', '#e74c3c' 
    elif kode in institusi: return 'Perusahaan Besar', '#3498db' 
    else: return 'Tidak Jelas', '#2ecc71' 

def style_warna_broker(val):
    _, warna = get_kategori_broker(val)
    return f'color: {warna}; font-weight: bold;'

# 🟢 FUNGSI BUNGLON UNTUK ANTI-CRASH DI CLOUD
def apply_styler_map(styler, func, subset=None):
    if hasattr(styler, 'map'):
        return styler.map(func, subset=subset)
    else:
        return styler.applymap(func, subset=subset)

# --- MEMBUAT FITUR "INGATAN" (SESSION STATE) ---
if 'api_key' not in st.session_state:
    st.session_state['api_key'] = muat_api_key()
if 'data_bandarmologi' not in st.session_state:
    st.session_state['data_bandarmologi'] = None
if 'multi_screener_data' not in st.session_state:
    st.session_state['multi_screener_data'] = None

# ==============================================================================
# 📊 MEMBUAT SIDEBAR MENU KEMBALI NORMAL
# ==============================================================================
st.sidebar.title("Menu Navigasi")
pilihan_menu = st.sidebar.radio(
    "Pilih Menu:",
    ("🏠 Halaman Depan", "📊 Deteksi Saham Cepat", "🕵️‍♂️ Deteksi Bandar Penuh", "⚙️ Pengaturan Kode Rahasia")
)

st.sidebar.markdown("---")
st.sidebar.info("Aplikasi Pencari Saham Otomatis V1.0\n\n⚡ **Versi Super Mudah Dipahami**")

# --- KONTEN HALAMAN BERDASARKAN MENU ---

if pilihan_menu == "🏠 Halaman Depan":
    st.title("Selamat Datang Bos! 📈")
    st.success("Sistem siap digunakan. Silakan pilih menu di sebelah kiri untuk mulai mencari cuan.")

elif pilihan_menu == "📊 Deteksi Saham Cepat":
    # Memanggil script Teknikal (Pastikan file screener_teknikal.py ada di folder yang sama)
    import screener_teknikal
    screener_teknikal.jalankan_teknikal()

elif pilihan_menu == "🕵️‍♂️ Deteksi Bandar Penuh":
    st.title("Mesin Pelacak Bandar Saham 🕵️‍♂️")
    st.markdown("Alat canggih untuk mengintip **Apakah Bandar sedang memborong (Beli) atau membuang barang (Jual)**.")
    
    if st.session_state['api_key'] == '':
        st.warning("⚠️ Silakan masukkan Kode API Anda di menu 'Pengaturan Kode Rahasia' terlebih dahulu agar mesin bisa menarik data dari pusat.")
    else:
        # ==============================================================================
        # 🚀 BAGIAN 1: AUTO-SCREENER MASSAL
        # ==============================================================================
        st.markdown("### 🚀 MESIN PENCARI BANYAK SAHAM SEKALIGUS")
        st.markdown("Masukkan banyak saham, dan biarkan sistem mencari mana yang paling bagus dibeli hari ini!")
        
        with st.expander("Klik di sini untuk membuka Mesin Pencari", expanded=False):
            col_mode1, col_mode2 = st.columns([1, 1])
            with col_mode1:
                mode_scan = st.radio("Pilih Cara Mencari:", ["📝 Ketik Nama Saham Sendiri", "📊 Cari Otomatis dari Pasar"])
            with col_mode2:
                kemarin_m = datetime.date.today() - datetime.timedelta(days=1)
                tanggal_multi = st.date_input("Pilih Tanggal Transaksi:", value=(kemarin_m, kemarin_m), max_value=datetime.date.today(), key='tgl_multi')
            
            tickers_to_scan = []
            if "Ketik" in mode_scan:
                multi_emiten = st.text_area("Ketik Kode Saham (Pisahkan dengan koma):", "BBCA, BMRI, BREN, CUAN, AMMN, TLKM, ASII, GOTO, PGAS")
                tickers_to_scan = [t.strip().upper() for t in multi_emiten.split(',') if t.strip()]
            else:
                pilihan_indeks = st.selectbox("Cari di kelompok saham mana?:", ["Saham Paling Laris (LQ45)", "Saham Perusahaan Raksasa (IDX30)", "Saham Copet Cepat Naik Turun"])
                if "LQ45" in pilihan_indeks:
                    tickers_to_scan = [t.strip() for t in "ACES, ADRO, AKRA, AMMN, AMRT, ANTM, ARTO, ASII, BBCA, BBNI, BBRI, BBTN, BFIN, BMRI, BRIS, BRPT, BUKA, CPIN, EMTK, ESSA, EXCL, GOTO, HRUM, ICBP, INCO, INDF, INKP, INTP, ITMG, KLBF, MAPI, MBMA, MDKA, MEDC, MTEL, PGAS, PGEO, PTBA, SIDO, SMGR, SRTG, TLKM, TOWR, UNTR, UNVR".split(",")]
                elif "IDX30" in pilihan_indeks:
                    tickers_to_scan = [t.strip() for t in "ADRO, AKRA, AMMN, AMRT, ANTM, ARTO, ASII, BBCA, BBNI, BBRI, BMRI, BRPT, BUKA, CPIN, ESSA, EXCL, GOTO, HRUM, ICBP, INDF, INKP, INTP, ITMG, KLBF, MDKA, MEDC, PGAS, PTBA, TLKM, UNTR".split(",")]
                else:
                    tickers_to_scan = [t.strip() for t in "BREN, CUAN, PANI, TPIA, BRPT, CGAS, VKTR, NCKL, DATA, STRK, MSJA, BDKR, SMGA, TENN, HUMI".split(",")]
                
                st.info(f"Sistem akan memeriksa **{len(tickers_to_scan)} saham** secara berurutan.")

            btn_multi = st.button("⚡ Mulai Cari Saham Bagus", use_container_width=True)

        if btn_multi:
            if len(tanggal_multi) == 2:
                start_m, end_m = tanggal_multi
            elif len(tanggal_multi) == 1:
                start_m = end_m = tanggal_multi[0]
            else:
                st.error("Pilih tanggal dengan benar ya, Bos.")
                st.stop()

            if not tickers_to_scan:
                st.warning("Silakan ketik minimal 1 nama saham.")
            else:
                screener_results = []
                progress_bar = st.progress(0, text="Sistem sedang bekerja keras membongkar data bandar...")
                
                headers_m = {"Authorization": f"Bearer {st.session_state['api_key']}", "Accept": "application/json"}
                params_m = {
                    "from": start_m.strftime("%Y-%m-%d"),
                    "to": end_m.strftime("%Y-%m-%d"),
                    "investor": "all",
                    "market": "RG"
                }

                for i, ticker in enumerate(tickers_to_scan):
                    progress_bar.progress((i) / len(tickers_to_scan), text=f"Sedang mengintip saham {ticker} ({i+1}/{len(tickers_to_scan)})...")
                    url_m = f"https://api.invezgo.com/analysis/summary/stock/{ticker}"
                    try:
                        res_m = requests.get(url_m, headers=headers_m, params=params_m, timeout=10)
                        if res_m.status_code == 200:
                            data_m = res_m.json()
                            if data_m:
                                df_net_m = pd.DataFrame(data_m)
                                df_net_m['net_value'] = df_net_m['net_value'].astype(float)
                                df_net_m['net_volume'] = pd.to_numeric(df_net_m.get('net_volume', 0), errors='coerce').fillna(0)
                                
                                df_aku_m = df_net_m[df_net_m['net_value'] > 0].sort_values(by='net_value', ascending=False).head(5)
                                df_dis_m = df_net_m[df_net_m['net_value'] < 0].copy()
                                df_dis_m['net_value_abs'] = df_dis_m['net_value'].abs()
                                df_dis_m = df_dis_m.sort_values(by='net_value_abs', ascending=False).head(5)
                                
                                tot_aku_m = df_aku_m['net_value'].sum() if not df_aku_m.empty else 0
                                tot_lot_m = (df_aku_m['net_volume'].sum() / 100) if not df_aku_m.empty else 0
                                
                                tot_dis_m = df_dis_m['net_value_abs'].sum() if not df_dis_m.empty else 0
                                tot_trans_m = tot_aku_m + tot_dis_m
                                net_vol_m = tot_aku_m - tot_dis_m
                                
                                vwap_bandar_m = (tot_aku_m / (tot_lot_m * 100)) if tot_lot_m > 0 else 0
                                
                                prob_m = 50.0
                                status_m = "RAGU-RAGU 🟡"
                                
                                if tot_trans_m > 0:
                                    rasio_m = (tot_aku_m / tot_trans_m) * 100 if tot_aku_m > tot_dis_m else (tot_dis_m / tot_trans_m) * 100
                                    if tot_aku_m > tot_dis_m:
                                        if rasio_m > 70:
                                            prob_m = min(rasio_m + 10, 95.0)
                                            status_m = "BANDAR BORONG BESAR 🚀"
                                        else:
                                            prob_m = min(rasio_m + 5, 85.0)
                                            status_m = "BANDAR MULAI BELI 🟢"
                                    elif tot_dis_m > tot_aku_m:
                                        if rasio_m > 70:
                                            prob_turun_m = min(rasio_m + 10, 95.0)
                                            prob_m = 100 - prob_turun_m
                                            status_m = "BANDAR JUALAN BESAR 🩸"
                                        else:
                                            prob_turun_m = min(rasio_m + 5, 85.0)
                                            prob_m = 100 - prob_turun_m
                                            status_m = "BANDAR MULAI JUAL 🔴"
                                            
                                try:
                                    hist_m = yf.Ticker(f"{ticker}.JK").history(period="1d")
                                    c_price_m = float(hist_m['Close'].iloc[-1]) if not hist_m.empty else 0
                                except:
                                    c_price_m = 0
                                    
                                status_nyangkut = "-"
                                if c_price_m > 0 and vwap_bandar_m > 0:
                                    diff_pct = ((c_price_m - vwap_bandar_m) / vwap_bandar_m) * 100
                                    if diff_pct < -2:
                                        status_nyangkut = f"HARGA MURAH SEKALI ({diff_pct:.1f}%)"
                                    elif diff_pct > 5:
                                        status_nyangkut = f"HARGA KEMAHALAN ({diff_pct:.1f}%)"
                                    else:
                                        status_nyangkut = f"HARGA AMAN SEDANG ({diff_pct:.1f}%)"
                                
                                screener_results.append({
                                    "Nama Saham": ticker,
                                    "Peluang Naik 🎯": prob_m,
                                    "Kelakuan Bandar": status_m,
                                    "Status Harga": status_nyangkut,
                                    "Sisa Uang Bandar": net_vol_m,
                                    "Uang Dipakai Beli": tot_aku_m,
                                    "Uang Ditarik Keluar": tot_dis_m
                                })
                    except:
                        pass 
                    time.sleep(0.1) 
                    
                progress_bar.progress(100, text="✅ Semua Saham Selesai Diperiksa!")
                time.sleep(0.5)
                progress_bar.empty()

                if screener_results:
                    df_screener = pd.DataFrame(screener_results)
                    df_screener = df_screener.sort_values(by="Peluang Naik 🎯", ascending=False).reset_index(drop=True)
                    
                    df_display = df_screener.copy()
                    df_display['Peluang Naik 🎯'] = df_display['Peluang Naik 🎯'].apply(lambda x: f"{x:.1f}%")
                    df_display['Sisa Uang Bandar'] = df_display['Sisa Uang Bandar'].apply(format_rupiah)
                    df_display['Uang Dipakai Beli'] = df_display['Uang Dipakai Beli'].apply(format_rupiah)
                    df_display['Uang Ditarik Keluar'] = df_display['Uang Ditarik Keluar'].apply(format_rupiah)
                    
                    st.session_state['multi_screener_data'] = df_display
                else:
                    st.session_state['multi_screener_data'] = "KOSONG"

        if st.session_state['multi_screener_data'] is not None:
            if isinstance(st.session_state['multi_screener_data'], pd.DataFrame):
                st.success("🎯 **INI DIA SAHAM-SAHAM YANG PALING BAGUS DIBELI HARI INI:** (Pilih salah satu lalu periksa detailnya di kotak paling bawah)")
                
                opsi_filter_mass = st.radio("Saring Tabel Ini:", ["Tampilkan Semua Saham", "Tampilkan Hanya Saham Harga Murah Sekali 🔥"], horizontal=True)
                df_view = st.session_state['multi_screener_data'].copy()
                
                if opsi_filter_mass == "Tampilkan Hanya Saham Harga Murah Sekali 🔥":
                    df_view = df_view[df_view['Status Harga'].str.contains("MURAH", na=False)]
                
                def color_mass(val):
                    if isinstance(val, str):
                        if any(x in val for x in ["BORONG", "MURAH", "AMAN"]): return 'color: #2ecc71; font-weight: bold; background-color: rgba(46, 204, 113, 0.1);'
                        elif any(x in val for x in ["JUALAN", "KEMAHALAN"]): return 'color: #e74c3c; font-weight: bold; background-color: rgba(231, 76, 60, 0.1);'
                    return ''
                    
                st.dataframe(apply_styler_map(df_view.style, color_mass, subset=['Kelakuan Bandar', 'Status Harga']), use_container_width=True)
            elif st.session_state['multi_screener_data'] == "KOSONG":
                st.warning("Maaf Bos, sepertinya tidak ada saham yang menarik hari ini di daftar yang Bos pilih.")

        st.write("---")

        # ==============================================================================
        # 🔍 BAGIAN 2: FITUR ANALISA MENDALAM (SINGLE ANALYZER) 
        # ==============================================================================
        st.markdown("### 🔍 Periksa Satu Saham Secara Penuh")
        with st.container():
            col_inp1, col_inp2 = st.columns([1, 2])
            with col_inp1:
                emiten_input = st.text_input("Ketik Singkatan Saham (Contoh: BBCA):", "BREN").upper()
            with col_inp2:
                kemarin = datetime.date.today() - datetime.timedelta(days=1)
                tanggal_input = st.date_input(
                    "Pilih Rentang Tanggal (Bisa Mingguan/Bulanan):", 
                    value=(kemarin, kemarin),
                    max_value=datetime.date.today()
                )
        
        if st.button("🚀 Mulai Periksa Saham Ini!", use_container_width=True):
            if len(tanggal_input) == 2:
                start_date, end_date = tanggal_input
            elif len(tanggal_input) == 1:
                start_date = end_date = tanggal_input[0]
            else:
                st.error("Silakan pilih tanggalnya dengan benar ya, Bos.")
                st.stop()

            b_days = pd.bdate_range(start=start_date, end=end_date)
            
            if len(b_days) == 0:
                st.session_state['data_bandarmologi'] = "KOSONG"
            else:
                progress_text = "Menarik data rahasia bursa... Mohon tunggu sebentar."
                my_bar = st.progress(40, text=progress_text)
                
                data_ditemukan = False
                pesan_error_api = "" 
                data_net = []
                current_price = 0 
                prev_price = 0
                
                url = f"https://api.invezgo.com/analysis/summary/stock/{emiten_input}"
                headers = {"Authorization": f"Bearer {st.session_state['api_key']}", "Accept": "application/json"}
                parameter = {
                    "from": start_date.strftime("%Y-%m-%d"),
                    "to": end_date.strftime("%Y-%m-%d"),
                    "investor": "all",
                    "market": "RG"
                }
                
                try:
                    response = requests.get(url, headers=headers, params=parameter)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, list) and len(data) > 0:
                            data_ditemukan = True
                            for item in data:
                                broker = item.get("code", "-")
                                net_val = float(item.get("net_value") or 0)
                                net_lot = float(item.get("net_volume") or 0) / 100 
                                buy_avg = float(item.get("buy_avg") or 0)
                                sell_avg = float(item.get("sell_avg") or 0)
                                
                                tipe_brk, warna_brk = get_kategori_broker(broker) 
                                data_net.append({
                                    "Broker": broker, "Tipe": tipe_brk, 
                                    "Net Value": net_val, "Net Lot": net_lot, "Warna": warna_brk,
                                    "Buy Avg": buy_avg, "Sell Avg": sell_avg
                                })
                                
                    elif response.status_code == 204:
                        data_ditemukan = False
                    else:
                        pesan_error_api = f"Error {response.status_code}: {response.text}"
                        
                except Exception as e:
                    pesan_error_api = f"Sistem Gagal Terhubung: {e}"

                if data_ditemukan:
                    try:
                        my_bar.progress(60, text="Mengambil Harga Saham Saat Ini...")
                        yf_ticker = yf.Ticker(f"{emiten_input}.JK")
                        hist = yf_ticker.history(period="5d")
                        if not hist.empty and len(hist) > 1:
                            current_price = float(hist['Close'].iloc[-1])
                            prev_price = float(hist['Close'].iloc[-2])
                        elif not hist.empty:
                            current_price = float(hist['Close'].iloc[-1])
                            prev_price = current_price
                    except:
                        pass 

                df_trend = pd.DataFrame()
                if data_ditemukan:
                    try:
                        my_bar.progress(80, text="Membongkar Sejarah Belanja Bandar...")
                        
                        df_net_sementara = pd.DataFrame(data_net)
                        df_akumulasi_sementara = df_net_sementara[df_net_sementara['Net Value'] > 0].sort_values(by='Net Value', ascending=False)
                        df_distribusi_sementara = df_net_sementara[df_net_sementara['Net Value'] < 0].sort_values(by='Net Value', ascending=True)
                        
                        top_acc_list = df_akumulasi_sementara.head(5)['Broker'].tolist()
                        top_dist_list = df_distribusi_sementara.head(5)['Broker'].tolist()

                        url_trend = f"https://api.invezgo.com/analysis/inventory-chart/stock/{emiten_input}"
                        params_trend = {
                            "from": start_date.strftime("%Y-%m-%d"),
                            "to": end_date.strftime("%Y-%m-%d"),
                            "scope": "val",
                            "investor": "all",
                            "market": "RG"
                        }
                        res_trend = requests.get(url_trend, headers=headers, params=params_trend)
                        if res_trend.status_code == 200:
                            data_trend = res_trend.json()
                            broker_hist = data_trend.get('broker', [])
                            
                            daily_dict = {}
                            for b in broker_hist:
                                b_code = b.get('broker', '')
                                if b_code in top_acc_list or b_code in top_dist_list:
                                    for day_data in b.get('data', []):
                                        dt = day_data.get('date')
                                        val = float(day_data.get('value', 0))
                                        
                                        if dt not in daily_dict:
                                            daily_dict[dt] = {'Date': dt, 'Akumulasi (Top 5)': 0.0, 'Distribusi (Top 5)': 0.0}
                                            
                                        if b_code in top_acc_list:
                                            daily_dict[dt]['Akumulasi (Top 5)'] += val
                                        if b_code in top_dist_list:
                                            daily_dict[dt]['Distribusi (Top 5)'] += val 
                                            
                            df_trend = pd.DataFrame(list(daily_dict.values()))
                            if not df_trend.empty:
                                df_trend = df_trend.sort_values('Date')
                    except Exception as e:
                        pass 

                my_bar.progress(100, text="Selesai Boss!")
                time.sleep(0.5)
                my_bar.empty() 

                if pesan_error_api != "":
                    st.error(f"🚨 **GAGAL MENARIK DATA KE PUSAT!**\nPesan dari server: `{pesan_error_api}`")
                    st.session_state['data_bandarmologi'] = None
                elif data_ditemukan:
                    df_net = pd.DataFrame(data_net)
                    
                    df_akumulasi = df_net[df_net['Net Value'] > 0].sort_values(by='Net Value', ascending=False)
                    df_distribusi = df_net[df_net['Net Value'] < 0].copy()
                    df_distribusi['Net Value Abs'] = df_distribusi['Net Value'].abs()
                    df_distribusi = df_distribusi.sort_values(by='Net Value Abs', ascending=False)

                    st.session_state['data_bandarmologi'] = {
                        'emiten': emiten_input, 'start_date': start_date, 'end_date': end_date,
                        'df_akumulasi': df_akumulasi, 'df_distribusi': df_distribusi,
                        'df_akumulasi_top5': df_akumulasi.head(5), 'df_distribusi_top5': df_distribusi.head(5),
                        'current_price': current_price,
                        'prev_price': prev_price,
                        'df_trend': df_trend 
                    }
                else:
                    st.session_state['data_bandarmologi'] = "KOSONG"

        if st.session_state['data_bandarmologi'] == "KOSONG":
            st.warning("Data tidak ditemukan. Mungkin Bursa Efek sedang libur atau saham ini tidak laku pada tanggal tersebut.")
        
        elif st.session_state['data_bandarmologi'] is not None:
            db = st.session_state['data_bandarmologi']
            emiten_res, start_date_res, end_date_res = db['emiten'], db['start_date'], db['end_date']
            df_akumulasi, df_distribusi = db['df_akumulasi'], db['df_distribusi']
            df_akumulasi_top5, df_distribusi_top5 = db['df_akumulasi_top5'], db['df_distribusi_top5']
            current_price = db.get('current_price', 0)
            prev_price = db.get('prev_price', 0)
            df_trend = db.get('df_trend', pd.DataFrame())

            col_alert, col_print = st.columns([4, 1])
            with col_alert:
                st.success(f"✅ Berhasil! Mengambil data tanggal: **{start_date_res.strftime('%d %b %Y')}** s/d **{end_date_res.strftime('%d %b %Y')}**")
            with col_print:
                components.html(
                    """
                    <script>
                    function printLaporan() { window.parent.print(); }
                    </script>
                    <div style="text-align: right; padding-top: 2px;">
                        <button onclick="printLaporan()" style="background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; border: none; padding: 12px 18px; border-radius: 6px; cursor: pointer; font-weight: bold; font-family: sans-serif; box-shadow: 0 4px 6px rgba(0,0,0,0.15); width: 100%;">
                            🖨️ Cetak Untuk Disimpan
                        </button>
                    </div>
                    """, height=55
                )
            
            total_akumulasi = df_akumulasi_top5['Net Value'].sum()
            total_distribusi = df_distribusi_top5['Net Value Abs'].sum()
            net_total = total_akumulasi - total_distribusi
            
            asing_buy_tot = df_akumulasi[df_akumulasi['Tipe'] == 'Bule (Asing)']['Net Value'].sum() if not df_akumulasi.empty else 0
            asing_sell_tot = df_distribusi[df_distribusi['Tipe'] == 'Bule (Asing)']['Net Value Abs'].sum() if not df_distribusi.empty else 0
            net_foreign = asing_buy_tot - asing_sell_tot
            
            top1_acc = df_akumulasi.iloc[0]['Net Value'] if len(df_akumulasi) > 0 else 0
            top3_acc = df_akumulasi.head(3)['Net Value'].sum() if len(df_akumulasi) >= 3 else total_akumulasi
            all_acc = df_akumulasi['Net Value'].sum()
            top1_dom = (top1_acc / all_acc * 100) if all_acc > 0 else 0
            top3_dom = (top3_acc / all_acc * 100) if all_acc > 0 else 0
            
            total_top5_gabungan = total_akumulasi + total_distribusi
            pct_buy_top5 = (total_akumulasi / total_top5_gabungan * 100) if total_top5_gabungan > 0 else 0
            pct_sell_top5 = (total_distribusi / total_top5_gabungan * 100) if total_top5_gabungan > 0 else 0

            bandar_vwap = 0
            if total_akumulasi > 0 and df_akumulasi_top5['Net Lot'].sum() > 0:
                bandar_vwap = total_akumulasi / (df_akumulasi_top5['Net Lot'].sum() * 100)

            total_transaksi = total_akumulasi + total_distribusi
            prob_naik = 50.0
            status = "BANDAR RAGU-RAGU 🟡"
            warna = "warning"
            analisa_teks = "Kekuatan yang beli dan yang jual sama imbangnya. Bandar sedang santai atau cuma memutar-mutar barang sendiri."
            aksi_teks = "Sebaiknya tahan diri dulu. Jangan beli sebelum ada yang mulai borong terang-terangan."

            if total_transaksi > 0:
                rasio = (total_akumulasi / total_transaksi) * 100 if total_akumulasi > total_distribusi else (total_distribusi / total_transaksi) * 100
                
                if total_akumulasi > total_distribusi:
                    if rasio > 70:
                        status, warna, prob_naik = "BANDAR BORONG BESAR! 🚀", "success", min(rasio + 10, 95.0)
                        analisa_teks = f"Wow! Bandar besar memborong saham ini tanpa ampun! (Sebesar **{rasio:.1f}%**). Saham yang ada di tangan orang-orang kecil (ritel) mulai habis disapu bersih."
                        aksi_teks = "Sangat bagus untuk dibeli sekarang! Silakan beli langsung jika antrean pembeli masih terlihat tebal."
                    else:
                        status, warna, prob_naik = "BANDAR MULAI BELI 🟢", "info", min(rasio + 5, 85.0)
                        analisa_teks = f"Bandar sedang cicil beli pelan-pelan (Menguasai **{rasio:.1f}%**). Tapi masih ada sedikit perlawanan dari pihak yang ingin menjual."
                        aksi_teks = "Boleh cicil beli saat harga turun sedikit, atau tunggu saat antrean penjualnya mulai habis."
                elif total_distribusi > total_akumulasi:
                    if rasio > 70:
                        status, warna = "AWAS BANDAR JUALAN BESAR! 🩸", "error"
                        prob_turun = min(rasio + 10, 95.0); prob_naik = 100 - prob_turun
                        analisa_teks = f"Gawat! Bandar besar sedang buang barang besar-besaran (Sebesar **{rasio:.1f}%**). Mereka sedang cuci gudang ke investor kecil yang kebingungan."
                        aksi_teks = "**JANGAN DIBELI!** Hindari saham ini. Jika Anda sudah punya, lebih baik segera jual dan selamatkan uang Anda."
                    else:
                        status, warna = "BANDAR MULAI JUAL 🔴", "warning"
                        prob_turun = min(rasio + 5, 85.0); prob_naik = 100 - prob_turun
                        analisa_teks = f"Bandar terlihat mulai menjual sahamnya pelan-pelan (Sebesar **{rasio:.1f}%**). Masih belum terlalu bahaya, tapi patut diwaspadai."
                        aksi_teks = "Kurang disarankan untuk pemula. Hanya untuk pemain cepat yang siap jual kapan saja."

            st.markdown("### 📊 Papan Skor: Uang Masuk vs Uang Keluar")
            col_met1, col_met2, col_met3, col_met4, col_met5 = st.columns([1, 1, 1, 1.2, 1.2])
            
            col_met1.metric("🟢 Total Uang Masuk (Bandar)", format_rupiah(total_akumulasi))
            col_met2.metric("🔴 Total Uang Keluar (Bandar)", format_rupiah(total_distribusi))
            col_met3.metric(
                "⚡ SISA UANG MENGENDAP", format_rupiah(abs(net_total)), 
                delta="Uang Masuk Menang" if net_total > 0 else "-Uang Keluar Menang",
                delta_color="normal" if net_total > 0 else "inverse"
            )

            with col_met4:
                if current_price > 0 and bandar_vwap > 0:
                    selisih_harga = current_price - bandar_vwap
                    selisih_persen = (selisih_harga / bandar_vwap) * 100
                    
                    if selisih_persen < 0:
                        vwap_color = "linear-gradient(135deg, #2563eb, #3b82f6)" 
                        vwap_shadow = "rgba(59, 130, 246, 0.4)"
                        status_vwap = "📉 HARGA DISKON (Bandar Sedang Rugi)"
                        sign = ""
                    elif selisih_persen > 5:
                        vwap_color = "linear-gradient(135deg, #dc2626, #ef4444)" 
                        vwap_shadow = "rgba(239, 68, 68, 0.4)"
                        status_vwap = "⚠️ HARGA MAHAL (Hati-hati Bandar Jualan)"
                        sign = "+"
                    else:
                        vwap_color = "linear-gradient(135deg, #059669, #10b981)" 
                        vwap_shadow = "rgba(16, 185, 129, 0.4)"
                        status_vwap = "✅ HARGA AMAN (Sangat Dekat Harga Bandar)"
                        sign = "+"
                        
                    html_vwap = f"""
                    <div style="background: {vwap_color}; padding: 12px 10px; border-radius: 12px; text-align: center; color: white; box-shadow: 0 8px 15px {vwap_shadow}; border: 1px solid rgba(255,255,255,0.2); margin-top: -10px;">
                        <div style="font-size: 11px; font-weight: 700; margin-bottom: 2px; text-transform: uppercase; letter-spacing: 0.5px;">🏷️ Harga Kita vs Harga Bandar</div>
                        <div style="font-size: 20px; font-weight: 900; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); line-height: 1.2;">Rp {current_price:,.0f} <span style="font-size: 13px; font-weight: normal;">({sign}{selisih_persen:.1f}%)</span></div>
                        <div style="font-size: 12px; margin-top: 4px; font-weight: 600; color: #f1f5f9;">Harga Modal Bandar: <span style="color: #fde047; font-weight: 800;">Rp {bandar_vwap:,.0f}</span></div>
                        <div style="font-size: 10px; margin-top: 6px; font-weight: 700; background: rgba(0,0,0,0.2); border-radius: 20px; padding: 3px 8px; display: inline-block;">{status_vwap}</div>
                    </div>
                    """
                    st.markdown(html_vwap, unsafe_allow_html=True)
                else:
                    st.metric("🏷️ Harga Rata-rata Modal Bandar", format_rupiah(bandar_vwap))

            with col_met5:
                if prob_naik >= 60:
                    bg_color = "linear-gradient(135deg, #16a34a, #22c55e)" 
                    shadow = "rgba(34, 197, 94, 0.4)"
                    label_risiko = "🔥 AMAN DIBELI"
                elif prob_naik <= 40:
                    bg_color = "linear-gradient(135deg, #dc2626, #ef4444)" 
                    shadow = "rgba(239, 68, 68, 0.4)"
                    label_risiko = "⚠️ BAHAYA DIBELI"
                else:
                    bg_color = "linear-gradient(135deg, #d97706, #eab308)" 
                    shadow = "rgba(234, 179, 8, 0.4)"
                    label_risiko = "⚖️ BIASA SAJA"

                html_probabilitas = f"""
                <div style="background: {bg_color}; padding: 12px 10px; border-radius: 12px; text-align: center; color: white; box-shadow: 0 8px 15px {shadow}; border: 1px solid rgba(255,255,255,0.2); margin-top: -10px;">
                    <div style="font-size: 11px; font-weight: 700; margin-bottom: 2px; text-transform: uppercase; letter-spacing: 0.5px;">🎯 Peluang Saham Naik Besok</div>
                    <div style="font-size: 26px; font-weight: 900; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); line-height: 1.2;">{prob_naik:.1f}%</div>
                    <div style="font-size: 10px; margin-top: 4px; font-weight: 700; background: rgba(0,0,0,0.2); border-radius: 20px; padding: 3px 8px; display: inline-block;">{label_risiko}</div>
                </div>
                """
                st.markdown(html_probabilitas, unsafe_allow_html=True)
                
            st.markdown("<br>", unsafe_allow_html=True)
            col_adv1, col_adv2, col_adv3 = st.columns(3)
            
            with col_adv1:
                st.markdown(f"""
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 15px; border-radius: 8px;">
                    <div style="font-size: 12px; color: #64748b; font-weight: bold; text-transform: uppercase;">🌐 Pergerakan Uang Asing (Bule)</div>
                    <div style="font-size: 20px; font-weight: 900; color: {'#16a34a' if net_foreign > 0 else '#dc2626'};">{'+ Masuk ' if net_foreign > 0 else 'Keluar '}{format_rupiah(abs(net_foreign))}</div>
                </div>
                """, unsafe_allow_html=True)
                
            with col_adv2:
                st.markdown(f"""
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 15px; border-radius: 8px;">
                    <div style="font-size: 12px; color: #64748b; font-weight: bold; text-transform: uppercase;">👑 Kekuatan 1 Bandar Paling Besar</div>
                    <div style="font-size: 20px; font-weight: 900; color: {'#16a34a' if top1_dom > 30 else '#f59e0b'};">{top1_dom:.1f}% dari Total Pembelian</div>
                </div>
                """, unsafe_allow_html=True)
                
            with col_adv3:
                st.markdown(f"""
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 15px; border-radius: 8px;">
                    <div style="font-size: 12px; color: #64748b; font-weight: bold; text-transform: uppercase;">👥 Kekuatan Gabungan 3 Bandar Teratas</div>
                    <div style="font-size: 20px; font-weight: 900; color: {'#16a34a' if top3_dom > 60 else '#3b82f6'};">{top3_dom:.1f}% dari Total Pembelian</div>
                </div>
                """, unsafe_allow_html=True)

            st.write("---")

            col_chart1, col_chart2 = st.columns(2)
            
            df_aku_chart = df_akumulasi_top5.copy()
            if not df_aku_chart.empty:
                df_aku_chart['Broker_Label'] = df_aku_chart['Broker'] + " (" + df_aku_chart['Tipe'] + ")"
                df_aku_chart['Label_Val'] = df_aku_chart['Net Value'].apply(lambda x: format_rupiah(x).replace('Rp ', ''))
                df_aku_chart['Label_Lot'] = df_aku_chart['Net Lot'].apply(format_lot)

            df_dis_chart = df_distribusi_top5.copy()
            if not df_dis_chart.empty:
                df_dis_chart['Broker_Label'] = df_dis_chart['Broker'] + " (" + df_dis_chart['Tipe'] + ")"
                df_dis_chart['Label_Val'] = df_dis_chart['Net Value Abs'].apply(lambda x: format_rupiah(x).replace('Rp ', ''))
                df_dis_chart['Label_Lot'] = df_dis_chart['Net Lot'].apply(format_lot)

            with col_chart1:
                st.markdown("<h4 style='text-align: center;'>🟢 5 Besar Bandar Paling Rakus (Beli)</h4>", unsafe_allow_html=True)
                if not df_aku_chart.empty:
                    base_buy = alt.Chart(df_aku_chart).encode(
                        x=alt.X('Broker_Label:N', sort='-y', axis=alt.Axis(labelAngle=-45, title=None)),
                        tooltip=['Broker', 'Tipe', alt.Tooltip('Net Value:Q', format=',.0f', title='Nilai Uang (Rp)'), alt.Tooltip('Net Lot:Q', format=',.0f')]
                    )
                    bar_buy = base_buy.mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
                        y=alt.Y('Net Value:Q', axis=alt.Axis(title='Value', format='~s')),
                        color=alt.Color('Warna:N', scale=None)
                    )
                    text_val_buy = base_buy.mark_text(dy=-18, fontWeight=800, fontSize=12).encode(
                        y=alt.Y('Net Value:Q'),
                        text='Label_Val:N'
                    )
                    text_lot_buy = base_buy.mark_text(dy=-5, fontWeight=600, fontSize=10, color='#888888').encode(
                        y=alt.Y('Net Value:Q'),
                        text='Label_Lot:N'
                    )
                    chart_buy = alt.layer(bar_buy, text_val_buy, text_lot_buy).properties(height=350)
                    st.altair_chart(chart_buy, use_container_width=True)

                    # INI BLOK KODE YANG SEMPAT HILANG (DIKEMBALIKAN)
                    st.markdown(f"""
                    <div style="background: rgba(46, 204, 113, 0.08); border-top: 3px solid #2ecc71; padding: 12px; border-radius: 0 0 8px 8px; text-align: center; margin-top: -15px;">
                        <div style="font-size: 11px; color: #94a3b8; font-weight: 700; letter-spacing: 0.5px; margin-bottom: 3px; text-transform: uppercase;">Total Uang Masuk (Top 5)</div>
                        <div style="display: flex; justify-content: center; align-items: baseline; gap: 8px;">
                            <span style="font-size: 18px; font-weight: 900; color: #2ecc71;">{format_rupiah(total_akumulasi)}</span>
                            <span style="font-size: 12px; font-weight: 800; color: #ffffff; background: #2ecc71; padding: 2px 8px; border-radius: 12px;">{pct_buy_top5:.1f}%</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("Tidak ada data yang beli.")

            with col_chart2:
                st.markdown("<h4 style='text-align: center;'>🔴 5 Besar Bandar Buang Barang (Jual)</h4>", unsafe_allow_html=True)
                if not df_dis_chart.empty:
                    base_sell = alt.Chart(df_dis_chart).encode(
                        x=alt.X('Broker_Label:N', sort='-y', axis=alt.Axis(labelAngle=-45, title=None)),
                        tooltip=['Broker', 'Tipe', alt.Tooltip('Net Value Abs:Q', format=',.0f', title='Nilai Uang (Rp)'), alt.Tooltip('Net Lot:Q', format=',.0f')]
                    )
                    bar_sell = base_sell.mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
                        y=alt.Y('Net Value Abs:Q', axis=alt.Axis(title='Value', format='~s')),
                        color=alt.Color('Warna:N', scale=None)
                    )
                    text_val_sell = base_sell.mark_text(dy=-18, fontWeight=800, fontSize=12).encode(
                        y=alt.Y('Net Value Abs:Q'),
                        text='Label_Val:N'
                    )
                    text_lot_sell = base_sell.mark_text(dy=-5, fontWeight=600, fontSize=10, color='#888888').encode(
                        y=alt.Y('Net Value Abs:Q'),
                        text='Label_Lot:N'
                    )
                    chart_sell = alt.layer(bar_sell, text_val_sell, text_lot_sell).properties(height=350)
                    st.altair_chart(chart_sell, use_container_width=True)

                    # INI BLOK KODE YANG SEMPAT HILANG (DIKEMBALIKAN)
                    st.markdown(f"""
                    <div style="background: rgba(231, 76, 60, 0.08); border-top: 3px solid #e74c3c; padding: 12px; border-radius: 0 0 8px 8px; text-align: center; margin-top: -15px;">
                        <div style="font-size: 11px; color: #94a3b8; font-weight: 700; letter-spacing: 0.5px; margin-bottom: 3px; text-transform: uppercase;">Total Uang Keluar (Top 5)</div>
                        <div style="display: flex; justify-content: center; align-items: baseline; gap: 8px;">
                            <span style="font-size: 18px; font-weight: 900; color: #e74c3c;">{format_rupiah(total_distribusi)}</span>
                            <span style="font-size: 12px; font-weight: 800; color: #ffffff; background: #e74c3c; padding: 2px 8px; border-radius: 12px;">{pct_sell_top5:.1f}%</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("Tidak ada data yang jual.")

            st.write("---")
            st.markdown("### 📋 Laporan Lengkap Pembeli & Penjual")

            df_buy = df_akumulasi[['Broker', 'Net Value', 'Net Lot', 'Buy Avg']].copy()
            df_buy.columns = ['Yang Beli', 'Jumlah Uang (Rp)', 'Total Lot', 'Harga Modal']
            
            df_sell = df_distribusi[['Broker', 'Net Value Abs', 'Net Lot', 'Sell Avg']].copy()
            df_sell['Net Lot'] = df_sell['Net Lot'].abs() 
            df_sell.columns = ['Yang Jual', 'Jumlah Uang (Rp)', 'Total Lot', 'Harga Jual']

            col_tabel1, col_tabel2 = st.columns(2)
            
            with col_tabel1:
                st.markdown("<h5 style='color: #2ecc71; text-align: center;'>🟢 DAFTAR YANG MEMBELI SAHAM INI</h5>", unsafe_allow_html=True)
                styler_buy = apply_styler_map(df_buy.style, style_warna_broker, subset=['Yang Beli'])
                styler_buy = apply_styler_map(styler_buy, lambda x: 'color: #2ecc71; font-weight: bold;', subset=['Jumlah Uang (Rp)', 'Total Lot', 'Harga Modal'])
                styler_buy = styler_buy.format({'Jumlah Uang (Rp)': 'Rp {:,.0f}', 'Total Lot': '{:,.0f}', 'Harga Modal': 'Rp {:,.0f}'})
                st.dataframe(styler_buy, use_container_width=True, hide_index=True)

            with col_tabel2:
                st.markdown("<h5 style='color: #e74c3c; text-align: center;'>🔴 DAFTAR YANG MENJUAL SAHAM INI</h5>", unsafe_allow_html=True)
                styler_sell = apply_styler_map(df_sell.style, style_warna_broker, subset=['Yang Jual'])
                styler_sell = apply_styler_map(styler_sell, lambda x: 'color: #e74c3c; font-weight: bold;', subset=['Jumlah Uang (Rp)', 'Total Lot', 'Harga Jual'])
                styler_sell = styler_sell.format({'Jumlah Uang (Rp)': 'Rp {:,.0f}', 'Total Lot': '{:,.0f}', 'Harga Jual': 'Rp {:,.0f}'})
                st.dataframe(styler_sell, use_container_width=True, hide_index=True)

            st.markdown("""
            <div style='text-align: center; font-size: 16px; margin-top: 10px; margin-bottom: 20px;'>
                <span style='color:#2ecc71; font-weight:bold;'>● Tidak Jelas (Zombie)</span> &nbsp;&nbsp;|&nbsp;&nbsp; 
                <span style='color:#9b59b6; font-weight:bold;'>● Orang Bule (Asing)</span> &nbsp;&nbsp;|&nbsp;&nbsp; 
                <span style='color:#e74c3c; font-weight:bold;'>● Investor Biasa (Ritel)</span> &nbsp;&nbsp;|&nbsp;&nbsp; 
                <span style='color:#3498db; font-weight:bold;'>● Perusahaan Besar</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 🔍 Cari Info Kode Broker")
            col_search1, col_search2 = st.columns([1, 2])
            
            with col_search1:
                search_query = st.text_input("Ketik Kode / Nama Broker:", "", placeholder="Contoh: AK atau Mandiri").strip()
            
            if search_query:
                df_semua_broker = pd.DataFrame(list(DARI_BROKER_NAMA_MAP.items()), columns=['Kode', 'Nama'])
                df_filtered = df_semua_broker[
                    df_semua_broker['Kode'].str.contains(search_query, case=False, na=False) | 
                    df_semua_broker['Nama'].str.contains(search_query, case=False, na=False)
                ]
                
                if not df_filtered.empty:
                    df_filtered_styled = apply_styler_map(df_filtered.style, style_warna_broker, subset=['Kode', 'Nama'])
                    st.dataframe(df_filtered_styled, use_container_width=True, hide_index=True)
                else:
                    st.warning("Tidak ditemukan broker yang cocok dengan pencarian.")

            if total_transaksi > 0:
                posisi_marker = (total_akumulasi / total_transaksi) * 100

                meter_html = f"""
                <style>
                .broker-action-container {{
                    width: 100%; margin-top: 10px; margin-bottom: 30px; padding: 25px 20px;
                    background-color: rgba(15, 23, 42, 0.6); border-radius: 12px; border: 1px solid rgba(255,255,255,0.2);
                    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
                }}
                .broker-action-title {{
                    font-weight: 800; font-size: 18px; margin-bottom: 25px; color: #f8fafc; text-align: center; letter-spacing: 1px;
                }}
                .bar-wrapper {{
                    position: relative; height: 20px; border-radius: 10px; display: flex; overflow: hidden;
                    box-shadow: 0 0 10px rgba(0,0,0,0.8) inset;
                }}
                .bar-segment {{
                    flex: 1; border-right: 2px solid rgba(0,0,0,0.6);
                }}
                .bar-segment:last-child {{ border-right: none; }}
                .bg-big-dist {{ background-color: #dc2626; }}
                .bg-dist {{ background-color: #ef4444; }}
                .bg-neutral {{ background-color: #94a3b8; }}
                .bg-acc {{ background-color: #22c55e; }}
                .bg-big-acc {{ background-color: #16a34a; }}

                .marker-container {{
                    position: absolute; top: -12px; bottom: -12px; left: {posisi_marker:.1f}%;
                    transform: translateX(-50%); z-index: 10;
                    display: flex; flex-direction: column; align-items: center; justify-content: center;
                    transition: left 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
                }}
                .marker-line {{
                    width: 8px; height: 44px; background-color: #fde047; border-radius: 4px;
                    box-shadow: 0 0 15px 4px rgba(253, 224, 71, 0.9); border: 1px solid #ffffff;
                }}
                .labels {{
                    display: flex; justify-content: space-between; font-size: 15px; color: #ffffff; margin-top: 15px; font-weight: 700;
                    text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
                }}
                </style>

                <div class="broker-action-container">
                    <div class="broker-action-title">📊 JARUM KECEPATAN BANDAR 📊</div>
                    <div class="bar-wrapper">
                        <div class="bar-segment bg-big-dist"></div>
                        <div class="bar-segment bg-dist"></div>
                        <div class="bar-segment bg-neutral"></div>
                        <div class="bar-segment bg-acc"></div>
                        <div class="bar-segment bg-big-acc"></div>
                        <div class="marker-container">
                            <div class="marker-line"></div>
                        </div>
                    </div>
                    <div class="labels">
                        <span style="color: #ffcccc;">🩸 Sangat Bahaya</span>
                        <span style="position: absolute; left: 50%; transform: translateX(-50%); color: #e2e8f0;">⚖️ Ragu-ragu</span>
                        <span style="color: #ccffcc;">🚀 Sangat Aman</span>
                    </div>
                </div>
                """
                st.markdown(meter_html, unsafe_allow_html=True)

            st.write("---")
            st.markdown("### 🥧 Peta Kekuatan: Siapa Yang Paling Banyak Transaksi?")
            
            df_aku_kategori = df_akumulasi.groupby('Tipe')['Net Value'].sum().reset_index()
            if not df_aku_kategori.empty:
                tot_aku_kategori = df_aku_kategori['Net Value'].sum()
                df_aku_kategori['Persen'] = (df_aku_kategori['Net Value'] / tot_aku_kategori) * 100
                df_aku_kategori['Label'] = df_aku_kategori['Persen'].apply(lambda x: f"{x:.1f}%" if x > 4 else "")

            df_dis_kategori = df_distribusi.groupby('Tipe')['Net Value Abs'].sum().reset_index()
            if not df_dis_kategori.empty:
                tot_dis_kategori = df_dis_kategori['Net Value Abs'].sum()
                df_dis_kategori['Persen'] = (df_dis_kategori['Net Value Abs'] / tot_dis_kategori) * 100
                df_dis_kategori['Label'] = df_dis_kategori['Persen'].apply(lambda x: f"{x:.1f}%" if x > 4 else "")
            
            color_scale_pie = alt.Scale(
                domain=['Bule (Asing)', 'Investor Biasa', 'Perusahaan Besar', 'Tidak Jelas'],
                range=['#9b59b6', '#e74c3c', '#3498db', '#2ecc71']
            )

            col_pie1, col_pie2 = st.columns(2)
            with col_pie1:
                st.markdown("<h5 style='text-align: center; color: #2ecc71;'>🟢 Persentase Pemborong Saham</h5>", unsafe_allow_html=True)
                if not df_aku_kategori.empty:
                    base_buy = alt.Chart(df_aku_kategori).encode(
                        theta=alt.Theta(field="Net Value", type="quantitative", stack=True),
                        color=alt.Color(field="Tipe", type="nominal", scale=color_scale_pie, legend=alt.Legend(title=None, orient='bottom', labelFontSize=12))
                    )
                    pie_buy = base_buy.mark_arc(innerRadius=50, outerRadius=120, cornerRadius=3).encode(
                        tooltip=['Tipe', alt.Tooltip('Net Value:Q', format=',.0f', title='Nilai Uang (Rp)'), alt.Tooltip('Persen:Q', format='.1f', title='Berapa Persen? (%)')]
                    )
                    text_buy = base_buy.mark_text(radius=85, size=13, fontWeight=800).encode(
                        text='Label:N',
                        color=alt.value('white') 
                    )
                    st.altair_chart(alt.layer(pie_buy, text_buy).properties(height=320), use_container_width=True)
                else:
                    st.info("Tidak ada data yang beli")

            with col_pie2:
                st.markdown("<h5 style='text-align: center; color: #e74c3c;'>🔴 Persentase Pembuang Saham</h5>", unsafe_allow_html=True)
                if not df_dis_kategori.empty:
                    base_sell = alt.Chart(df_dis_kategori).encode(
                        theta=alt.Theta(field="Net Value Abs", type="quantitative", stack=True),
                        color=alt.Color(field="Tipe", type="nominal", scale=color_scale_pie, legend=alt.Legend(title=None, orient='bottom', labelFontSize=12))
                    )
                    pie_sell = base_sell.mark_arc(innerRadius=50, outerRadius=120, cornerRadius=3).encode(
                        tooltip=['Tipe', alt.Tooltip('Net Value Abs:Q', format=',.0f', title='Nilai Uang (Rp)'), alt.Tooltip('Persen:Q', format='.1f', title='Berapa Persen? (%)')]
                    )
                    text_sell = base_sell.mark_text(radius=85, size=13, fontWeight=800).encode(
                        text='Label:N',
                        color=alt.value('white')
                    )
                    st.altair_chart(alt.layer(pie_sell, text_sell).properties(height=320), use_container_width=True)
                else:
                    st.info("Tidak ada data yang jual")

            total_aku_all = df_aku_kategori['Net Value'].sum() if not df_aku_kategori.empty else 0
            total_dis_all = df_dis_kategori['Net Value Abs'].sum() if not df_dis_kategori.empty else 0
            
            pct_asing_buy = 0
            pct_ritel_sell = 0
            
            if total_aku_all > 0 and 'Bule (Asing)' in df_aku_kategori['Tipe'].values:
                asing_buy = df_aku_kategori[df_aku_kategori['Tipe'] == 'Bule (Asing)']['Net Value'].iloc[0]
                pct_asing_buy = (asing_buy / total_aku_all) * 100
                
            if total_dis_all > 0 and 'Investor Biasa' in df_dis_kategori['Tipe'].values:
                ritel_sell = df_dis_kategori[df_dis_kategori['Tipe'] == 'Investor Biasa']['Net Value Abs'].iloc[0]
                pct_ritel_sell = (ritel_sell / total_dis_all) * 100

            if pct_asing_buy > 40 and pct_ritel_sell > 40:
                insight_bg = "linear-gradient(90deg, rgba(20, 83, 45, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%)"
                insight_border = "#4ade80" 
                insight_title = "🔥 PELUANG EMAS! (Orang Kaya Masuk, Orang Kecil Keluar)"
                insight_teks = "Sangat bagus! Uang besar dari **Orang Bule (Asing)** sedang masuk diam-diam, sementara **Investor Biasa (Ritel)** justru sedang ketakutan dan membuang sahamnya. Ini adalah pola sempurna sebelum saham diterbangkan harganya ke atas langit. Sangat layak dibeli!"
            elif pct_asing_buy > 40:
                insight_bg = "linear-gradient(90deg, rgba(88, 28, 135, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%)"
                insight_border = "#c084fc" 
                insight_title = "🟣 DIBORONG BULE (ASING)"
                insight_teks = "Saham ini sedang dikuasai penuh oleh **Orang Asing**. Aliran uang yang masuk sangat kuat dan stabil. Posisi yang sangat aman untuk ikut membeli dan menyimpan sahamnya."
            elif pct_ritel_sell > 40:
                insight_bg = "linear-gradient(90deg, rgba(30, 58, 138, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%)"
                insight_border = "#60a5fa" 
                insight_title = "📉 INVESTOR KECIL KETAKUTAN (PANIC SELLING)"
                insight_teks = "Para **Investor Biasa (Ritel)** terpantau sedang panik dan menjual murah saham-saham mereka. Ini sebenarnya pertanda bagus, karena saham sedang dibersihkan dari 'penumpang gelap' sebelum nanti diangkat naik oleh bandar."
            else:
                insight_bg = "linear-gradient(90deg, rgba(51, 65, 85, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%)"
                insight_border = "#cbd5e1" 
                insight_title = "💤 PASAR SEDANG MEMBOSANKAN"
                insight_teks = "Tidak ada uang besar yang dominan masuk, dan tidak ada aksi kepanikan. Saham ini cuma sedang dimainkan oper-operan oleh pemain kecil (scalper) saja. Sebaiknya **bersabar dulu** dan cari saham lain."

            st.markdown(f"""
            <div style="background: {insight_bg}; border-left: 8px solid {insight_border}; padding: 15px 20px; border-radius: 6px; margin-top: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
                <div style="color: {insight_border}; margin-top: 0; margin-bottom: 8px; font-weight: 900; font-size: 16px; letter-spacing: 0.5px;">{insight_title}</div>
                <div style="font-size: 14px; font-weight: 500; color: #f8fafc; line-height: 1.5;">{insight_teks}</div>
            </div>
            """, unsafe_allow_html=True)

            if not df_trend.empty:
                st.write("---")
                st.markdown("### 📈 Riwayat Kekuatan Bandar Dari Hari ke Hari")
                st.markdown("Grafik ini menunjukkan apakah Bandar terus menambah belanjaan tiap hari (hijau membesar), atau malah asyik jualan (merah membesar).")
                
                df_trend['Total_Abs'] = df_trend['Akumulasi (Top 5)'].abs() + df_trend['Distribusi (Top 5)'].abs()
                df_trend['Pct_Aku'] = (df_trend['Akumulasi (Top 5)'].abs() / df_trend['Total_Abs'] * 100).fillna(0)
                df_trend['Pct_Dis'] = (df_trend['Distribusi (Top 5)'].abs() / df_trend['Total_Abs'] * 100).fillna(0)

                df_trend['Label_Aku'] = df_trend['Pct_Aku'].apply(lambda x: f"{x:.0f}%" if x >= 1 else "")
                df_trend['Label_Dis'] = df_trend['Pct_Dis'].apply(lambda x: f"{x:.0f}%" if x >= 1 else "")
                
                df_melt = df_trend.melt(
                    id_vars=['Date', 'Pct_Aku', 'Pct_Dis'], 
                    value_vars=['Akumulasi (Top 5)', 'Distribusi (Top 5)'], 
                    var_name='Kategori', 
                    value_name='Nilai'
                )
                df_melt['Persentase (%)'] = df_melt.apply(lambda row: row['Pct_Aku'] if 'Akumulasi' in row['Kategori'] else row['Pct_Dis'], axis=1)
                
                color_scale_trend = alt.Scale(
                    domain=['Akumulasi (Top 5)', 'Distribusi (Top 5)'],
                    range=['#2ecc71', '#e74c3c'] 
                )
                
                bars = alt.Chart(df_melt).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3, size=25).encode(
                    x=alt.X('Date:O', title='Tanggal Transaksi', axis=alt.Axis(labelAngle=-45, grid=False)),
                    y=alt.Y('Nilai:Q', title='Jumlah Uang (Rp)', axis=alt.Axis(format='~s')),
                    color=alt.Color('Kategori:N', scale=color_scale_trend, legend=alt.Legend(title=None, orient='top')),
                    tooltip=['Date', 'Kategori', alt.Tooltip('Nilai:Q', format=',.0f', title='Jumlah Uang (Rp)'), alt.Tooltip('Persentase (%):Q', format='.1f')]
                )

                text_aku = alt.Chart(df_trend).mark_text(dy=-12, color='#22c55e', fontWeight='bold', fontSize=12).encode(
                    x=alt.X('Date:O'),
                    y=alt.Y('Akumulasi (Top 5):Q'),
                    text=alt.Text('Label_Aku:N')
                )

                text_dis = alt.Chart(df_trend).mark_text(dy=12, color='#ef4444', fontWeight='bold', fontSize=12).encode(
                    x=alt.X('Date:O'),
                    y=alt.Y('Distribusi (Top 5):Q'),
                    text=alt.Text('Label_Dis:N')
                )
                
                rule = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(color='gray', strokeWidth=1).encode(y='y:Q')
                
                st.altair_chart(alt.layer(bars, text_aku, text_dis, rule).properties(height=380), use_container_width=True)

            st.write("---")
            st.markdown(f"## 🤖 Kesimpulan Robot Untuk Saham Ini: {emiten_res}")
            
            # 🚀 DETEKSI HIDDEN ACCUMULATION / DISTRIBUTION (DIVERGENCE)
            divergence_html = ""
            if current_price > 0 and prev_price > 0:
                price_change_pct = ((current_price - prev_price) / prev_price) * 100
                
                if price_change_pct < -0.5 and net_total > 0 and prob_naik >= 60:
                    divergence_html = f"""
                    <div style="background: rgba(34, 197, 94, 0.1); border-left: 5px solid #22c55e; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                        <div style="color: #22c55e; font-weight: 900; font-size: 15px;">🕵️‍♂️ BANDAR BELI DIAM-DIAM! (Peluang Emas)</div>
                        <div style="font-size: 13px; color: #f8fafc; margin-top: 5px;">Hati-hati tertipu! Harga saham ini memang sengaja diturunkan <b>({price_change_pct:.1f}%)</b> hari ini agar orang-orang awam takut dan jual rugi (Cutloss). Namun diam-diam, data menunjukkan si Bandar justru sedang memborong sahamnya di harga bawah. Bersiaplah, sebentar lagi saham ini akan melesat!</div>
                    </div>
                    """
                elif price_change_pct > 0.5 and net_total < 0 and prob_naik <= 40:
                    divergence_html = f"""
                    <div style="background: rgba(239, 68, 68, 0.1); border-left: 5px solid #ef4444; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                        <div style="color: #ef4444; font-weight: 900; font-size: 15px;">🪤 AWAS JEBAKAN! (Harga Naik Tapi Bandar Jualan)</div>
                        <div style="font-size: 13px; color: #f8fafc; margin-top: 5px;">Harga saham ini memang terlihat sedang naik <b>(Mekar {price_change_pct:.1f}%)</b> dan menggoda untuk dibeli. TAPI AWAS, itu hanya pancingan! Faktanya Bandar sedang jualan dan membuang barangnya ke investor kecil. Jangan beli agar tidak nyangkut di pucuk!</div>
                    </div>
                    """

            if divergence_html:
                st.markdown(divergence_html, unsafe_allow_html=True)
            
            if total_transaksi > 0:
                if total_akumulasi > total_distribusi and prob_naik >= 55:
                    ai_rekomendasi = "🚀 SANGAT BAGUS DIBELI SEKARANG!"
                    ai_color = "#22c55e" 
                    
                    if current_price > 0 and bandar_vwap > 0:
                        if current_price > (bandar_vwap * 1.05):
                            area_entry = f"Rp {int(bandar_vwap):,} - Rp {int(bandar_vwap * 1.02):,}<br><span style='font-size:11px; color:#fbbf24;'>(Tunggu Harga Turun Sedikit)</span>"
                            cl_price = f"Rp {int(bandar_vwap * 0.97):,}"
                            tp_price = f"Rp {int(current_price * 1.05):,}"
                        else:
                            area_entry = f"Rp {int(current_price):,} - Rp {int(current_price * 1.01):,}<br><span style='font-size:11px; color:#4ade80;'>(Langsung Sikat! Harga Sangat Murah)</span>"
                            cl_price = f"Rp {int(min(current_price, bandar_vwap) * 0.97):,}"
                            tp_price = f"Rp {int(current_price * 1.05):,} - Rp {int(current_price * 1.10):,}"
                    else:
                        area_entry = f"Rp {int(bandar_vwap):,}<br><span style='font-size:11px; color:#cbd5e1;'>(Beli di Sekitar Harga Ini)</span>"
                        tp_price = f"Rp {int(bandar_vwap * 1.05):,}"
                        cl_price = f"Rp {int(bandar_vwap * 0.97):,}"
                        
                else:
                    ai_rekomendasi = "🛑 JANGAN DIBELI DULU! BAHAYA."
                    ai_color = "#ef4444" 
                    area_entry = "-"
                    tp_price = "-"
                    cl_price = "-"

                ai_html = f"""<div style="background: linear-gradient(135deg, #1e293b, #0f172a); border: 1px solid #334155; border-radius: 12px; padding: 25px; margin-bottom: 20px; box-shadow: 0 10px 20px rgba(0, 0, 0, 0.4);">
<h4 style="color: #94a3b8; margin-top: 0; text-align: center; font-size: 14px; letter-spacing: 2px; text-transform: uppercase;">⚡ Perhitungan Robot Ahli Saham ⚡</h4>
<div style="text-align: center; font-size: 32px; font-weight: 900; color: {ai_color}; margin-bottom: 25px; text-shadow: 0 0 15px {ai_color}80;">{ai_rekomendasi}</div>
<div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 15px;">
<div style="flex: 1; min-width: 150px; background: rgba(255,255,255,0.03); padding: 15px; border-radius: 8px; text-align: center; border-bottom: 3px solid #3b82f6;">
<div style="font-size: 12px; color: #94a3b8; font-weight: bold; margin-bottom: 8px;">📍 HARGA BELI TERBAIK</div>
<div style="font-size: 18px; font-weight: 800; color: #f8fafc; line-height: 1.3;">{area_entry}</div>
</div>
<div style="flex: 1; min-width: 150px; background: rgba(255,255,255,0.03); padding: 15px; border-radius: 8px; text-align: center; border-bottom: 3px solid #22c55e;">
<div style="font-size: 12px; color: #94a3b8; font-weight: bold; margin-bottom: 8px;">🎯 JUAL KETIKA UNTUNG DI HARGA</div>
<div style="font-size: 20px; font-weight: 800; color: #4ade80;">{tp_price}</div>
</div>
<div style="flex: 1; min-width: 150px; background: rgba(255,255,255,0.03); padding: 15px; border-radius: 8px; text-align: center; border-bottom: 3px solid #ef4444;">
<div style="font-size: 12px; color: #94a3b8; font-weight: bold; margin-bottom: 8px;">✂️ JUAL RUGI (CUTLOSS) JIKA TURUN KE</div>
<div style="font-size: 20px; font-weight: 800; color: #f87171;">{cl_price}</div>
</div>
<div style="flex: 1; min-width: 150px; background: rgba(255,255,255,0.03); padding: 15px; border-radius: 8px; text-align: center; border-bottom: 3px solid #eab308;">
<div style="font-size: 12px; color: #94a3b8; font-weight: bold; margin-bottom: 8px;">⚖️ PELUANG KITA MENANG</div>
<div style="font-size: 24px; font-weight: 900; color: #facc15;">{prob_naik:.1f}%</div>
</div>
</div>
</div>"""
                st.markdown(ai_html, unsafe_allow_html=True)

                if warna == "success": st.success(f"### KESIMPULAN DATA: {status}")
                elif warna == "info": st.info(f"### KESIMPULAN DATA: {status}")
                elif warna == "warning": st.warning(f"### KESIMPULAN DATA: {status}")
                else: st.error(f"### KESIMPULAN DATA: {status}")

                st.markdown(f"**📖 Cerita Di Balik Saham Ini:**\n{analisa_teks}")
                st.markdown(f"**🎯 Saran Tindakan Besok Pagi:**\n{aksi_teks}")
                
                if not df_akumulasi_top5.empty:
                    broker_top = df_akumulasi_top5.iloc[0]['Broker']
                    tipe_top, _ = get_kategori_broker(broker_top)
                    st.markdown(f"**👑 Sosok Pemain Utamanya:** Broker dengan kode **{broker_top}** ({tipe_top}) adalah orang yang belanja paling banyak hari ini. Terus awasi broker ini besok!")

# 4. MENU PENGATURAN API
elif pilihan_menu == "⚙️ Pengaturan Kode Rahasia":
    st.title("Pengaturan Kode API")
    st.markdown("Agar aplikasi ini bisa mencuri data bandar dari bursa, pastikan Anda memasukkan *API Key* Invezgo Anda di bawah ini.")
    
    api_key_input = st.text_input("Ketik / Paste API Key Invezgo di sini:", value=st.session_state['api_key'], type="password")
    if st.button("Simpan Kodenya"):
        st.session_state['api_key'] = api_key_input
        simpan_api_key(api_key_input)
        st.success("✅ Hebat! Kodenya sudah tersimpan aman. Mulai sekarang Anda bisa langsung cari saham tanpa perlu ketik kode ini lagi.")
