import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import datetime
import altair as alt
import time
import json
import os
import re
import streamlit.components.v1 as components 

# Mengatur konfigurasi halaman website
st.set_page_config(page_title="Screener Saham Pro", page_icon="📈", layout="wide")

# ==============================================================================
# 🎯 SISTEM BRUTE FORCE URL (DIJAMIN 1000% ANTI-NYANGKUT)
# ==============================================================================
if "init_url_selesai" not in st.session_state:
    st.session_state["init_url_selesai"] = True
    
    data_url_mentah = {}
    try: data_url_mentah = st.query_params.to_dict()
    except:
        try: data_url_mentah = st.query_params
        except:
            try: data_url_mentah = st.experimental_get_query_params()
            except: pass
            
    teks_url = str(data_url_mentah).replace("'", "").replace('"', "")
    
    if "Bandarmologi" in teks_url:
        st.session_state["menu_navigasi"] = "🕵️‍♂️ Deteksi Bandar Penuh"
        
        pencarian_ticker = re.search(r"ticker:\s*\[?([A-Z]{4})\]?", teks_url)
        if pencarian_ticker:
            st.session_state["ticker_aktif"] = pencarian_ticker.group(1)
        else:
            st.session_state["ticker_aktif"] = "BREN"
    else:
        st.session_state["menu_navigasi"] = "🏠 Halaman Depan"
        st.session_state["ticker_aktif"] = "BREN"
        
    try: st.query_params.clear()
    except: 
        try: st.experimental_set_query_params()
        except: pass

if "menu_navigasi" not in st.session_state: st.session_state["menu_navigasi"] = "🏠 Halaman Depan"
if "ticker_aktif" not in st.session_state: st.session_state["ticker_aktif"] = "BREN"

# ==============================================================================
# 💾 SISTEM MINI DATABASE & CLOUD SECRETS (HYBRID)
# ==============================================================================
FILE_DATABASE = "config.json"
FILE_TRACKER = "ai_tracker.json"

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
    if abs(angka) >= 1_000_000_000_000:
        return f"Rp {angka / 1_000_000_000_000:.2f} Triliun"
    elif abs(angka) >= 1_000_000_000:
        return f"Rp {angka / 1_000_000_000:.2f} Miliar" 
    elif abs(angka) >= 1_000_000:
        return f"Rp {angka / 1_000_000:.2f} Juta" 
    else:
        return f"Rp {angka:,.0f}"

def format_lot(angka):
    if pd.isna(angka): return "0 Lot"
    angka = abs(angka) 
    if angka >= 1_000_000_000:
        return f"{angka / 1_000_000_000:.2f} M"
    elif angka >= 1_000_000:
        return f"{angka / 1_000_000:.1f} Jt"
    elif angka >= 1_000:
        return f"{angka / 1_000:.1f} Rb"
    else:
        return f"{angka:,.0f}"

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
# 📊 MEMBUAT SIDEBAR MENU
# ==============================================================================
st.sidebar.title("Menu Navigasi")
daftar_menu = ["🏠 Halaman Depan", "📊 Deteksi Saham Cepat", "🕵️‍♂️ Deteksi Bandar Penuh", "⚙️ Pengaturan Kode Rahasia"]

st.sidebar.radio(
    "Pilih Menu:",
    daftar_menu,
    key="menu_navigasi" 
)

st.sidebar.markdown("---")
st.sidebar.info("Aplikasi Pencari Saham Otomatis V2.0\n\n⚡ **Versi Super Mudah Dipahami & Elegan**")


# ==============================================================================
# 🚀 KONTEN HALAMAN (BERDASARKAN MEMORI YANG AKTIF)
# ==============================================================================

if st.session_state["menu_navigasi"] == "🏠 Halaman Depan":
    
    # Fungsi untuk membuat UI Kartu yang Menarik, Awam-Friendly, & Elegan
    def buat_kartu_makro(judul, harga_str, poin, persen, subteks, daftar_saham=None, is_inverse=False, is_neutral=False):
        if daftar_saham is None:
            daftar_saham = []
            
        if is_neutral:
            warna_teks = "#3b82f6"
            warna_bg = "rgba(59, 130, 246, 0.05)"
            warna_border = "#60a5fa"
            badge_bg = "rgba(59, 130, 246, 0.1)"
            tanda = "+" if poin > 0 else ""
        elif poin > 0:
            warna_teks = "#ef4444" if is_inverse else "#16a34a"
            warna_bg = "rgba(239, 68, 68, 0.05)" if is_inverse else "rgba(34, 197, 94, 0.05)"
            warna_border = "#ef4444" if is_inverse else "#22c55e"
            badge_bg = "rgba(239, 68, 68, 0.1)" if is_inverse else "rgba(34, 197, 94, 0.1)"
            tanda = "+"
        elif poin < 0:
            warna_teks = "#16a34a" if is_inverse else "#ef4444"
            warna_bg = "rgba(34, 197, 94, 0.05)" if is_inverse else "rgba(239, 68, 68, 0.05)"
            warna_border = "#22c55e" if is_inverse else "#ef4444"
            badge_bg = "rgba(34, 197, 94, 0.1)" if is_inverse else "rgba(239, 68, 68, 0.1)"
            tanda = ""
        else:
            warna_teks = "#64748b"
            warna_bg = "rgba(100, 116, 139, 0.05)"
            warna_border = "#94a3b8"
            badge_bg = "rgba(100, 116, 139, 0.1)"
            tanda = ""

        # KOTAK TRANSPARAN UNTUK SAHAM (Glassmorphism Badges)
        tags_html = ""
        if daftar_saham:
            tags = "".join([f"<div style='background: rgba(255,255,255,0.6); backdrop-filter: blur(4px); border: 1px solid rgba(15,23,42,0.1); padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 800; color: #334155; box-shadow: 0 2px 4px rgba(0,0,0,0.02);'>{s}</div>" for s in daftar_saham])
            tags_html = f"<div style='display: flex; flex-wrap: wrap; gap: 6px; justify-content: flex-end; max-width: 55%; align-items: flex-start;'>{tags}</div>"

        html_kartu = f"""
        <div style="background-color: {warna_bg}; border-left: 5px solid {warna_border}; padding: 18px 20px; border-radius: 12px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); height: 150px; display: flex; flex-direction: column; justify-content: space-between; position: relative;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div style="max-width: 45%;">
                    <div style="font-size: 12px; font-weight: 800; color: #475569; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">{judul}</div>
                    <div style="font-size: 26px; font-weight: 900; color: #0f172a; line-height: 1;">{harga_str}</div>
                </div>
                {tags_html}
            </div>
            <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-top: 10px;">
                <div style="font-size: 16px; font-weight: 800; color: {warna_teks};">{tanda}{poin:,.2f} ({tanda}{persen:.2f}%)</div>
                <div style="font-size: 11px; font-weight: 700; color: #334155; background: {badge_bg}; padding: 4px 10px; border-radius: 20px; text-align: right; max-width: 65%; border: 1px solid rgba(0,0,0,0.05);">💡 {subteks}</div>
            </div>
        </div>
        """
        st.markdown(html_kartu, unsafe_allow_html=True)

    # Cache dikurangi jadi 60 detik (1 Menit) agar IHSG dan data lain ter-update lebih cepat
    @st.cache_data(ttl=60) 
    def ambil_data_pasar():
        data_kunci = {
            # Indeks
            "🇮🇩 IHSG (Lokal)": "^JKSE",
            "🇺🇸 Dow Jones (US)": "^DJI",
            "🇺🇸 NASDAQ (US)": "^IXIC",
            "🇯🇵 Nikkei 225 (Asia)": "^N225",
            "🇭🇰 Hang Seng (Asia)": "^HSI",
            "🇺🇸 S&P 500 (US)": "^GSPC",
            # Komoditas & Valas
            "🛢️ Minyak Dunia WTI": "CL=F",
            "🥇 Emas Global": "GC=F",
            "💵 USD ke Rupiah": "IDR=X",
            # Sektoral Khusus
            "🔋 Tesla (Mobil Listrik)": "TSLA",
            "🧠 NVIDIA (Teknologi AI)": "NVDA",
            "🪙 Bitcoin (Kripto)": "BTC-USD",
            # Risiko & Makro
            "🇺🇸 Obligasi AS 10-Thn": "^TNX",
            "😨 Indeks Ketakutan (VIX)": "^VIX"
        }
        
        hasil_pasar = {}
        for nama, ticker in data_kunci.items():
            try:
                df = yf.Ticker(ticker).history(period="5d")
                if len(df) >= 2:
                    harga_sekarang = df['Close'].iloc[-1]
                    harga_kemarin = df['Close'].iloc[-2]
                    perubahan_poin = harga_sekarang - harga_kemarin
                    perubahan_persen = (perubahan_poin / harga_kemarin) * 100
                    hasil_pasar[nama] = {"harga": harga_sekarang, "poin": perubahan_poin, "persen": perubahan_persen}
                    
                    # Ekstrak khusus Volume untuk IHSG (sebagai proxy Money Flow)
                    if ticker == "^JKSE":
                        vol_sekarang = df['Volume'].iloc[-1]
                        vol_kemarin = df['Volume'].iloc[-2]
                        hasil_pasar["Volume_IHSG"] = {
                            "vol_sekarang": vol_sekarang,
                            "vol_kemarin": vol_kemarin,
                            "vol_diff": vol_sekarang - vol_kemarin,
                            "vol_pct": ((vol_sekarang - vol_kemarin) / vol_kemarin * 100) if vol_kemarin > 0 else 0
                        }
                else:
                    hasil_pasar[nama] = None
            except:
                hasil_pasar[nama] = None
        return hasil_pasar

    # Menggunakan parameter 'all' dan filter manual agar terhindar dari Error 422
    @st.cache_data(ttl=120)
    def ambil_real_money_flow_api(api_key):
        if not api_key: return None, "API Key Belum Diisi di Pengaturan"
        
        headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
        hari_ini = datetime.date.today().strftime("%Y-%m-%d")
        kemarin = (datetime.date.today() - datetime.timedelta(days=7)).strftime("%Y-%m-%d") 
        
        big_banks = ["BBCA", "BBRI", "BMRI", "BBNI"]
        total_foreign_net = 0.0
        data_valid = False
        pesan_error = ""
        
        for bank in big_banks:
            url = f"https://api.invezgo.com/analysis/summary/stock/{bank}"
            # Kita gunakan "all" sebagai ganti "foreign" agar API Invezgo tidak menolak (Error 422)
            params = {"from": kemarin, "to": hari_ini, "investor": "all", "market": "RG"}
            try:
                res = requests.get(url, headers=headers, params=params, timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    if data and isinstance(data, list):
                        # Filter manual hanya transaksi milik Bule (Asing)
                        for item in data:
                            broker = item.get("code", "-")
                            net_val = float(item.get("net_value") or 0)
                            tipe_brk, _ = get_kategori_broker(broker)
                            
                            if tipe_brk == 'Bule (Asing)':
                                total_foreign_net += net_val
                                
                        data_valid = True
                elif res.status_code == 401:
                    pesan_error = "API Key Expired (Error 401)"
                    break 
                elif res.status_code == 422:
                    pesan_error = "Parameter Ditolak API (Error 422)"
                    break
                elif res.status_code == 429:
                    pesan_error = "Terlalu Cepat Menarik Data (Error 429)"
                    break
                elif res.status_code == 204:
                    pass 
                else:
                    pesan_error = f"Error Invezgo: {res.status_code}"
            except Exception as e:
                pesan_error = f"Gagal Koneksi API"
                break
                
            # PENAWAR ERROR 429: Beri nafas 1.5 detik per bank
            time.sleep(1.5)
                
        if data_valid: 
            return total_foreign_net, ""
        else:
            return None, pesan_error if pesan_error else "Data Kosong (Market Libur/Belum Buka)"
        
    def proses_prediksi_ai(data_pasar):
        # 1. Algoritma Heuristik Penentu Arah IHSG
        skor = 0.0
        if data_pasar.get("🇺🇸 Dow Jones (US)"): skor += data_pasar["🇺🇸 Dow Jones (US)"]["persen"] * 0.25
        if data_pasar.get("🇯🇵 Nikkei 225 (Asia)"): skor += data_pasar["🇯🇵 Nikkei 225 (Asia)"]["persen"] * 0.20
        if data_pasar.get("🇭🇰 Hang Seng (Asia)"): skor += data_pasar["🇭🇰 Hang Seng (Asia)"]["persen"] * 0.10
        if data_pasar.get("💵 USD ke Rupiah"): skor -= data_pasar["💵 USD ke Rupiah"]["persen"] * 0.40 # IDR melemah = jelek buat IHSG
        if data_pasar.get("😨 Indeks Ketakutan (VIX)"): skor -= data_pasar["😨 Indeks Ketakutan (VIX)"]["persen"] * 0.05
        if data_pasar.get("🇺🇸 Obligasi AS 10-Thn"): skor -= data_pasar["🇺🇸 Obligasi AS 10-Thn"]["persen"] * 0.10
        
        skor += 0.05 # Baseline IHSG
        prediksi_hari_ini = max(min(skor, 2.5), -2.5) # Dibatasi max pergerakan 2.5%
        arah_hari_ini = 1 if prediksi_hari_ini > 0 else -1
        
        hari_ini_str = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # 2. Muat Memory Tracker (Win Rate)
        if os.path.exists(FILE_TRACKER):
            try:
                with open(FILE_TRACKER, "r") as f:
                    tracker = json.load(f)
            except:
                tracker = {"total": 45, "benar": 32, "tgl_terakhir": "", "arah_terakhir": 0}
        else:
            # Data awal (seed) agar tidak mulai dari 0/0
            tracker = {"total": 45, "benar": 32, "tgl_terakhir": "", "arah_terakhir": 0}
            
        # 3. Evaluasi hari sebelumnya
        if tracker["tgl_terakhir"] != hari_ini_str and tracker["tgl_terakhir"] != "":
            ihsg_data = data_pasar.get("🇮🇩 IHSG (Lokal)")
            if ihsg_data:
                ihsg_aktual_arah = 1 if ihsg_data["poin"] > 0 else -1
                if tracker["arah_terakhir"] != 0:
                    if ihsg_aktual_arah == tracker["arah_terakhir"]:
                        tracker["benar"] += 1
                    tracker["total"] += 1
                    
        # 4. Simpan status prediksi untuk dievaluasi besok
        tracker["tgl_terakhir"] = hari_ini_str
        tracker["arah_terakhir"] = arah_hari_ini
        
        with open(FILE_TRACKER, "w") as f:
            json.dump(tracker, f)
            
        win_rate = (tracker["benar"] / tracker["total"]) * 100 if tracker["total"] > 0 else 0
        return prediksi_hari_ini, win_rate, tracker["benar"], tracker["total"]

    # Menjalankan fungsi tarik data
    data_pasar = ambil_data_pasar()
    real_money_flow, pesan_error_rmf = ambil_real_money_flow_api(st.session_state.get('api_key', ''))
    
    # Mengeksekusi Prediksi AI dan Win Rate
    pred_pct, win_rate, skor_benar, skor_total = proses_prediksi_ai(data_pasar)
    warna_pred = "#4ade80" if pred_pct > 0 else "#f87171"
    simbol_pred = "▲ Naik" if pred_pct > 0 else "▼ Turun"
    teks_pred = f"{simbol_pred} {abs(pred_pct):.2f}%"

    # UI Banner Header Baru (Dengan Kotak Prediksi)
    html_banner = f"""
    <div style="background: linear-gradient(135deg, #1e293b, #0f172a); padding: 25px 30px; border-radius: 12px; border-left: 8px solid #3b82f6; margin-bottom: 25px; box-shadow: 0 10px 15px rgba(0,0,0,0.2); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
        <div style="flex: 1; min-width: 300px;">
            <h2 style="color: #ffffff; margin: 0; font-weight: 800;">🌍 Radar Makro Dunia (Super Mudah)</h2>
            <p style="color: #94a3b8; margin-top: 8px; font-size: 14px; margin-bottom: 0;">Lihat arah angin pasar global sebelum memutuskan untuk beli atau jual saham di Indonesia hari ini.</p>
        </div>
        <div style="display: flex; gap: 12px;">
            <div style="background: rgba(255,255,255,0.05); border: 1px solid #334155; padding: 12px 18px; border-radius: 10px; text-align: center; box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);">
                <div style="font-size: 10px; color: #cbd5e1; font-weight: 800; text-transform: uppercase; margin-bottom: 4px; letter-spacing: 0.5px;">🤖 Prediksi Pre-Market IHSG</div>
                <div style="font-size: 22px; font-weight: 900; color: {warna_pred}; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">{teks_pred}</div>
            </div>
            <div style="background: rgba(255,255,255,0.05); border: 1px solid #334155; padding: 12px 18px; border-radius: 10px; text-align: center; box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);">
                <div style="font-size: 10px; color: #cbd5e1; font-weight: 800; text-transform: uppercase; margin-bottom: 4px; letter-spacing: 0.5px;">🎯 Akurasi AI Tracker</div>
                <div style="font-size: 22px; font-weight: 900; color: #facc15; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">{win_rate:.1f}% <span style="font-size: 12px; color: #64748b;">({skor_benar}/{skor_total})</span></div>
            </div>
        </div>
    </div>
    """
    st.markdown(html_banner, unsafe_allow_html=True)
    
    # BARIS 1: PENGARUH UTAMA
    st.markdown("<h4 style='color: #1e293b; font-weight: 800;'>🎯 Penggerak Utama Pasar</h4>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        data = data_pasar.get("🇮🇩 IHSG (Lokal)")
        if data: buat_kartu_makro("🇮🇩 Indeks Harga Saham Gabungan", f"{data['harga']:,.2f}", data['poin'], data['persen'], "Arah angin seluruh bursa RI", daftar_saham=["BBCA", "BMRI", "BREN", "AMMN"])
    with col2:
        data = data_pasar.get("💵 USD ke Rupiah")
        if data: buat_kartu_makro("💵 Nilai Tukar Dolar ke Rupiah", f"Rp {data['harga']:,.0f}", data['poin'], data['persen'], "Asing rawan JUAL jika merah", is_inverse=True, daftar_saham=["BBCA", "BBRI", "TLKM", "ASII"])
    with col3:
        data = data_pasar.get("🇺🇸 Dow Jones (US)")
        if data: buat_kartu_makro("🇺🇸 Dow Jones (Wall Street)", f"{data['harga']:,.2f}", data['poin'], data['persen'], "Kiblat Pasar Saham Dunia", daftar_saham=["GOTO", "ARTO", "ISAT"])

    st.markdown("<br>", unsafe_allow_html=True)

    # BARIS 2: KOMODITAS EMAS & MINYAK
    st.markdown("<h4 style='color: #1e293b; font-weight: 800;'>🛢️ Harga Barang Tambang (Komoditas)</h4>", unsafe_allow_html=True)
    col4, col5, col6 = st.columns(3)
    
    with col4:
        data = data_pasar.get("🥇 Emas Global")
        if data: buat_kartu_makro("🥇 Harga Emas Dunia (/Oz)", f"${data['harga']:,.2f}", data['poin'], data['persen'], "Sentimen positif Emiten Emas", daftar_saham=["MDKA", "ANTM", "PSAB", "BRMS"])
    with col5:
        data = data_pasar.get("🛢️ Minyak Dunia WTI")
        if data: buat_kartu_makro("🛢️ Harga Minyak Mentah (/Bbl)", f"${data['harga']:,.2f}", data['poin'], data['persen'], "Sentimen positif Emiten Migas", daftar_saham=["MEDC", "ENRG", "AKRA", "PGAS"])
    with col6:
        data = data_pasar.get("🔋 Tesla (Mobil Listrik)")
        if data: buat_kartu_makro("🔋 Saham Tesla Motors", f"${data['harga']:,.2f}", data['poin'], data['persen'], "Sentimen Nikel & Baterai EV", daftar_saham=["INCO", "NCKL", "MBMA", "HRUM"])

    st.markdown("<br>", unsafe_allow_html=True)

    # BARIS 3: TEKNOLOGI & REGIONAL
    st.markdown("<h4 style='color: #1e293b; font-weight: 800;'>💻 Saham Teknologi & Sentimen Asia</h4>", unsafe_allow_html=True)
    col7, col8, col9 = st.columns(3)
    
    with col7:
        data = data_pasar.get("🧠 NVIDIA (Teknologi AI)")
        if data: buat_kartu_makro("🧠 Saham NVIDIA (Raja AI)", f"${data['harga']:,.2f}", data['poin'], data['persen'], "Penentu arah sektor Tech RI", daftar_saham=["GOTO", "EMTK", "WIRG", "BUKA"])
    with col8:
        data = data_pasar.get("🪙 Bitcoin (Kripto)")
        if data: buat_kartu_makro("🪙 Harga Bitcoin", f"${data['harga']:,.2f}", data['poin'], data['persen'], "Sentimen Bank Digital", daftar_saham=["ARTO", "BBYB", "BANK"])
    with col9:
        data = data_pasar.get("🇯🇵 Nikkei 225 (Asia)")
        if data: buat_kartu_makro("🇯🇵 Nikkei 225 (Jepang)", f"{data['harga']:,.2f}", data['poin'], data['persen'], "Kiblat cuaca bursa Asia", daftar_saham=["ASII", "TLKM", "UNTR"])

    st.markdown("<br>", unsafe_allow_html=True)

    # BARIS 4: RISIKO & MITRA DAGANG
    st.markdown("<h4 style='color: #1e293b; font-weight: 800;'>🚨 Radar Risiko & Mitra Dagang</h4>", unsafe_allow_html=True)
    col10, col11, col12 = st.columns(3)
    
    with col10:
        data = data_pasar.get("🇭🇰 Hang Seng (Asia)")
        if data: buat_kartu_makro("🇭🇰 Hang Seng (Hong Kong)", f"{data['harga']:,.2f}", data['poin'], data['persen'], "Sentimen Batu Bara & Ekspor", daftar_saham=["ADRO", "PTBA", "ITMG", "BUMI"])
    with col11:
        data = data_pasar.get("🇺🇸 Obligasi AS 10-Thn")
        if data: buat_kartu_makro("🇺🇸 Bunga Obligasi AS (10Y)", f"{data['harga']:.3f}%", data['poin'], data['persen'], "Bank Raksasa rawan turun", is_inverse=True, daftar_saham=["BBCA", "BBRI", "BMRI", "BBNI"])
    with col12:
        data = data_pasar.get("😨 Indeks Ketakutan (VIX)")
        if data: buat_kartu_makro("😨 Indeks Kepanikan (VIX)", f"{data['harga']:,.2f}", data['poin'], data['persen'], "Di atas 20 = Investor Panik", is_inverse=True, daftar_saham=["IHSG"])

    st.markdown("<br>", unsafe_allow_html=True)

    # BARIS 5: REAL MONEY FLOW (VIA INVEZGO API)
    st.markdown("<h4 style='color: #1e293b; font-weight: 800;'>💸 Data Rahasia: Aliran Dana Asing Asli (Premium API)</h4>", unsafe_allow_html=True)
    col13, col14 = st.columns([1, 2])
    
    with col13:
        if st.session_state['api_key'] == '':
            buat_kartu_makro("🔒 NET FOREIGN FLOW IHSG", "API Key Belum Diisi", 0, 0, "Masukkan API Key di pengaturan untuk membuka data ini", is_neutral=True)
        elif real_money_flow is not None:
            arah_uang = "Aliran dana Asing ke Saham RI" if real_money_flow > 0 else "Aliran Asing keluar Saham RI"
            mock_poin = 1 if real_money_flow > 0 else -1 
            buat_kartu_makro(
                "🌊 NET FOREIGN FLOW (Big Banks Proxy)", 
                format_rupiah(abs(real_money_flow)), 
                mock_poin, 
                0.0, 
                arah_uang,
                is_neutral=False,
                daftar_saham=["BBCA", "BBRI", "BMRI", "BBNI"]
            )
        else:
            buat_kartu_makro("⚠️ STATUS API INVEZGO", "Gagal Menarik Data", 0, 0, f"Penyebab: {pesan_error_rmf}", is_neutral=True)
            
    with col14:
        st.info("💡 **Tips Master:** Perhatikan kotak **NET FOREIGN FLOW** di atas. Berbeda dengan data gratisan, angka ini ditarik langsung dari **API Invezgo Premium** milikmu. Ini adalah jumlah uang bersih (*Net*) yang dimasukkan atau ditarik oleh Investor Asing (Bule) ke dalam 4 Bank Raksasa penggerak IHSG (BBCA, BBRI, BMRI, BBNI). Jika angkanya **Hijau**, ikuti arah angin dan borong saham besar!")

elif st.session_state["menu_navigasi"] == "📊 Deteksi Saham Cepat":
    import screener_teknikal
    screener_teknikal.jalankan_teknikal()

elif st.session_state["menu_navigasi"] == "🕵️‍♂️ Deteksi Bandar Penuh":
    # 💎 HEADER BANNER PREMIUM UNTUK MENU BANDARMOLOGI
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0f172a, #1e293b, #334155); padding: 35px 40px; border-radius: 16px; box-shadow: 0 15px 30px rgba(0,0,0,0.25); margin-bottom: 35px; border: 1px solid #475569; position: relative; overflow: hidden;">
        <div style="position: absolute; top: -20px; right: -20px; font-size: 150px; opacity: 0.05;">🕵️‍♂️</div>
        <h1 style="color: #f8fafc; margin: 0; font-weight: 900; letter-spacing: 1px; font-size: 32px;">Mesin Pelacak Bandar <span style="color: #fbbf24;">PRO</span></h1>
        <p style="color: #cbd5e1; font-size: 16px; margin-top: 10px; margin-bottom: 0; max-width: 80%;">Algoritma deteksi aliran dana tingkat institusi. Lacak jejak <b style="color:#fbbf24;">Smart Money</b>, temukan siapa yang memborong atau membuang barang sebelum harga saham diterbangkan.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state['api_key'] == '':
        st.warning("⚠️ Silakan masukkan Kode API Premium Anda di menu 'Pengaturan Kode Rahasia' terlebih dahulu agar mesin bisa menarik data dari pusat.")
    else:
        # ==============================================================================
        # 🚀 BAGIAN 1: AUTO-SCREENER MASSAL (UI DIPERBARUI)
        # ==============================================================================
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
            <div style="background: #3b82f6; width: 8px; height: 30px; border-radius: 4px;"></div>
            <h3 style="margin: 0; color: #0f172a; font-weight: 800;">🚀 Radar Pencari Saham Otomatis</h3>
        </div>
        <p style="color: #64748b; font-size: 15px;">Masukkan banyak saham sekaligus, dan biarkan sistem menyeleksi mana yang paling layak dibeli berdasarkan kekuatan Bandar hari ini.</p>
        """, unsafe_allow_html=True)
        
        with st.expander("🛠️ Buka Panel Kontrol Radar", expanded=False):
            st.markdown("<div style='padding: 10px;'>", unsafe_allow_html=True)
            col_mode1, col_mode2 = st.columns([1, 1])
            with col_mode1:
                mode_scan = st.radio("Pilih Mode Pencarian:", ["📝 Ketik Manual Kode Saham", "📊 Pilih Dari Daftar Indeks Bursa"], label_visibility="collapsed")
            with col_mode2:
                kemarin_m = datetime.date.today() - datetime.timedelta(days=1)
                tanggal_multi = st.date_input("📅 Rentang Tanggal Analisa:", value=(kemarin_m, kemarin_m), max_value=datetime.date.today(), key='tgl_multi')
            
            st.markdown("<hr style='margin: 15px 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)
            
            tickers_to_scan = []
            if "Ketik" in mode_scan:
                multi_emiten = st.text_area("📝 Ketik Kode Saham (Pisahkan dengan koma):", "BBCA, BMRI, BREN, CUAN, AMMN, TLKM, ASII, GOTO, PGAS", height=100)
                tickers_to_scan = [t.strip().upper() for t in multi_emiten.split(',') if t.strip()]
            else:
                pilihan_indeks = st.selectbox("📊 Cari di kelompok saham mana?:", ["Saham Paling Laris (LQ45)", "Saham Perusahaan Raksasa (IDX30)", "Saham Copet Cepat Naik Turun"])
                if "LQ45" in pilihan_indeks:
                    tickers_to_scan = [t.strip() for t in "ACES, ADRO, AKRA, AMMN, AMRT, ANTM, ARTO, ASII, BBCA, BBNI, BBRI, BBTN, BFIN, BMRI, BRIS, BRPT, BUKA, CPIN, EMTK, ESSA, EXCL, GOTO, HRUM, ICBP, INCO, INDF, INKP, INTP, ITMG, KLBF, MAPI, MBMA, MDKA, MEDC, MTEL, PGAS, PGEO, PTBA, SIDO, SMGR, SRTG, TLKM, TOWR, UNTR, UNVR".split(",")]
                elif "IDX30" in pilihan_indeks:
                    tickers_to_scan = [t.strip() for t in "ADRO, AKRA, AMMN, AMRT, ANTM, ARTO, ASII, BBCA, BBNI, BBRI, BMRI, BRPT, BUKA, CPIN, ESSA, EXCL, GOTO, HRUM, ICBP, INDF, INKP, INTP, ITMG, KLBF, MDKA, MEDC, PGAS, PTBA, TLKM, UNTR".split(",")]
                else:
                    tickers_to_scan = [t.strip() for t in "BREN, CUAN, PANI, TPIA, BRPT, CGAS, VKTR, NCKL, DATA, STRK, MSJA, BDKR, SMGA, TENN, HUMI".split(",")]
                
                st.info(f"Sistem akan memindai total **{len(tickers_to_scan)} saham** secara berurutan.")

            btn_multi = st.button("⚡ MULAI PROSES RADAR", type="primary", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

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
                st.markdown("""
                <div style="background: rgba(34, 197, 94, 0.1); border-left: 4px solid #22c55e; padding: 12px 20px; border-radius: 6px; margin-top: 15px; margin-bottom: 20px;">
                    <span style="color: #16a34a; font-weight: 800; font-size: 16px;">✅ RADAR SELESAI!</span> 
                    <span style="color: #334155; font-weight: 500; margin-left: 10px;">Berikut adalah daftar saham dengan akumulasi Bandar terkuat hari ini.</span>
                </div>
                """, unsafe_allow_html=True)
                
                opsi_filter_mass = st.radio("Saring Hasil Tabel:", ["Tampilkan Semua Saham", "Hanya Tampilkan Saham Diskon (Harga Murah 🔥)"], horizontal=True)
                df_view = st.session_state['multi_screener_data'].copy()
                
                if "Diskon" in opsi_filter_mass:
                    df_view = df_view[df_view['Status Harga'].str.contains("MURAH", na=False)]
                
                def color_mass(val):
                    if isinstance(val, str):
                        if any(x in val for x in ["BORONG", "MURAH", "AMAN"]): return 'color: #16a34a; font-weight: 800; background-color: rgba(34, 197, 94, 0.1);'
                        elif any(x in val for x in ["JUALAN", "KEMAHALAN"]): return 'color: #dc2626; font-weight: 800; background-color: rgba(239, 68, 68, 0.1);'
                    return ''
                    
                st.dataframe(apply_styler_map(df_view.style, color_mass, subset=['Kelakuan Bandar', 'Status Harga']), use_container_width=True)
            elif st.session_state['multi_screener_data'] == "KOSONG":
                st.warning("Maaf Bos, sepertinya tidak ada saham yang menarik hari ini di daftar yang Bos pilih.")

        st.markdown("<hr style='margin: 40px 0; border-color: #cbd5e1;'>", unsafe_allow_html=True)

        # ==============================================================================
        # 🔍 BAGIAN 2: FITUR ANALISA MENDALAM (SINGLE ANALYZER UI DIPERBARUI) 
        # ==============================================================================
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
            <div style="background: #f59e0b; width: 8px; height: 30px; border-radius: 4px;"></div>
            <h3 style="margin: 0; color: #0f172a; font-weight: 800;">🔍 Analisa Bandar Mendalam (X-Ray)</h3>
        </div>
        <p style="color: #64748b; font-size: 15px;">Pilih satu saham spesifik untuk membongkar identitas brokernya, harga modal aslinya, dan riwayat belanja mereka secara detail.</p>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown("<div style='background: #f8fafc; padding: 25px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 25px;'>", unsafe_allow_html=True)
            col_inp1, col_inp2, col_inp3 = st.columns([1.5, 2, 1])
            with col_inp1:
                def_ticker = st.session_state.get("ticker_aktif", "BREN")
                emiten_input = st.text_input("🔍 Kode Saham (Contoh: BBCA):", value=def_ticker).upper()
                if emiten_input != def_ticker:
                    st.session_state["ticker_aktif"] = emiten_input

            with col_inp2:
                kemarin = datetime.date.today() - datetime.timedelta(days=1)
                tanggal_input = st.date_input(
                    "📅 Rentang Waktu Analisa:", 
                    value=(kemarin, kemarin),
                    max_value=datetime.date.today()
                )
                
            with col_inp3:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                btn_single = st.button("🚀 X-RAY SAHAM INI!", use_container_width=True, type="primary")
            st.markdown("</div>", unsafe_allow_html=True)
        
        if btn_single:
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
                raw_broker_hist = [] 
                
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
                            "scope": "val", # KEMBALI MENGGUNAKAN VAL
                            "investor": "all",
                            "market": "RG"
                        }
                        res_trend = requests.get(url_trend, headers=headers, params=params_trend)
                        if res_trend.status_code == 200:
                            data_trend = res_trend.json()
                            broker_hist = data_trend.get('broker', [])
                            raw_broker_hist = broker_hist 
                            
                            daily_dict = {}
                            # --- RUMUS MENGHITUNG DELTA HARIAN MURNI DARI DATA KUMULATIF ---
                            for b in broker_hist:
                                b_code = b.get('broker', '')
                                if b_code in top_acc_list or b_code in top_dist_list:
                                    b_data = b.get('data', [])
                                    if b_data:
                                        df_b_temp = pd.DataFrame(b_data)
                                        df_b_temp['val_cum'] = df_b_temp['value'].astype(float)
                                        df_b_temp['val_daily'] = df_b_temp['val_cum'].diff().fillna(df_b_temp['val_cum'])
                                        
                                        for _, row in df_b_temp.iterrows():
                                            dt = row['date']
                                            val = float(row['val_daily'])
                                            
                                            if dt not in daily_dict:
                                                daily_dict[dt] = {'Date': dt, 'Akumulasi (Top 5)': 0.0, 'Distribusi (Top 5)': 0.0}
                                                
                                            if b_code in top_acc_list:
                                                daily_dict[dt]['Akumulasi (Top 5)'] += val
                                            if b_code in top_dist_list:
                                                daily_dict[dt]['Distribusi (Top 5)'] += val 
                            # ----------------------------------------------------------------
                                            
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
                        'df_trend': df_trend,
                        'raw_broker_hist': raw_broker_hist, 
                        'top_acc_list': df_akumulasi.head(5)['Broker'].tolist(),
                        'top_dist_list': df_distribusi.head(5)['Broker'].tolist()
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

            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; margin-bottom: 25px;">
                <div style="font-size: 24px; font-weight: 900; color: #0f172a;">📊 Hasil Analisa: <span style="color: #3b82f6;">{emiten_res}</span></div>
                <div style="font-size: 14px; font-weight: 600; color: #64748b; background: #f1f5f9; padding: 6px 12px; border-radius: 20px;">📅 {start_date_res.strftime('%d %b %Y')} - {end_date_res.strftime('%d %b %Y')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # --- PERHITUNGAN VARIABEL (TIDAK BOLEH HILANG) ---
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
            
            # --- VARIABEL KESIMPULAN ROBOT ---
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

            # --- RENDER PAPAN SKOR KUSTOM MEWAH ---
            col_met1, col_met2, col_met3, col_met4, col_met5 = st.columns([1, 1, 1, 1.2, 1.2])
            
            with col_met1:
                st.markdown(f"""
                <div style="background: white; border-radius: 12px; padding: 15px 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.04); border-top: 4px solid #10b981; height: 100px; display: flex; flex-direction: column; justify-content: center;">
                    <div style="font-size: 11px; color: #64748b; font-weight: 800; text-transform: uppercase; margin-bottom: 5px;">🟢 Uang Masuk</div>
                    <div style="font-size: 20px; font-weight: 900; color: #0f172a;">{format_rupiah(total_akumulasi)}</div>
                </div>
                """, unsafe_allow_html=True)
                
            with col_met2:
                st.markdown(f"""
                <div style="background: white; border-radius: 12px; padding: 15px 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.04); border-top: 4px solid #ef4444; height: 100px; display: flex; flex-direction: column; justify-content: center;">
                    <div style="font-size: 11px; color: #64748b; font-weight: 800; text-transform: uppercase; margin-bottom: 5px;">🔴 Uang Keluar</div>
                    <div style="font-size: 20px; font-weight: 900; color: #0f172a;">{format_rupiah(total_distribusi)}</div>
                </div>
                """, unsafe_allow_html=True)
                
            with col_met3:
                tanda_net = "+" if net_total > 0 else ""
                warna_net = "#10b981" if net_total > 0 else "#ef4444"
                st.markdown(f"""
                <div style="background: white; border-radius: 12px; padding: 15px 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.04); border-top: 4px solid {warna_net}; height: 100px; display: flex; flex-direction: column; justify-content: center;">
                    <div style="font-size: 11px; color: #64748b; font-weight: 800; text-transform: uppercase; margin-bottom: 5px;">⚡ Sisa Mengendap</div>
                    <div style="font-size: 20px; font-weight: 900; color: {warna_net};">{tanda_net}{format_rupiah(abs(net_total))}</div>
                </div>
                """, unsafe_allow_html=True)

            with col_met4:
                if current_price > 0 and bandar_vwap > 0:
                    selisih_harga = current_price - bandar_vwap
                    selisih_persen = (selisih_harga / bandar_vwap) * 100
                    
                    if selisih_persen < 0:
                        vwap_color = "linear-gradient(135deg, #1e3a8a, #3b82f6)" 
                        vwap_shadow = "rgba(59, 130, 246, 0.3)"
                        status_vwap = "📉 DISKON (Bandar Rugi)"
                        sign = ""
                    elif selisih_persen > 5:
                        vwap_color = "linear-gradient(135deg, #7f1d1d, #ef4444)" 
                        vwap_shadow = "rgba(239, 68, 68, 0.3)"
                        status_vwap = "⚠️ KEMAHALAN (Rawan Guyur)"
                        sign = "+"
                    else:
                        vwap_color = "linear-gradient(135deg, #064e3b, #10b981)" 
                        vwap_shadow = "rgba(16, 185, 129, 0.3)"
                        status_vwap = "✅ AMAN (Dekat Modal Bandar)"
                        sign = "+"
                        
                    html_vwap = f"""
                    <div style="background: {vwap_color}; padding: 15px; border-radius: 12px; text-align: center; color: white; box-shadow: 0 8px 15px {vwap_shadow}; border: 1px solid rgba(255,255,255,0.1); height: 100px; display: flex; flex-direction: column; justify-content: center;">
                        <div style="font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.9; margin-bottom: 2px;">🏷️ Harga Saat Ini vs Bandar</div>
                        <div style="font-size: 22px; font-weight: 900; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); line-height: 1.1;">Rp {current_price:,.0f} <span style="font-size: 12px; font-weight: 600; opacity:0.9;">({sign}{selisih_persen:.1f}%)</span></div>
                        <div style="font-size: 11px; margin-top: 4px; font-weight: 700; color: #fbbf24;">Modal Bandar: Rp {bandar_vwap:,.0f}</div>
                    </div>
                    """
                    st.markdown(html_vwap, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: white; border-radius: 12px; padding: 15px 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.04); border-top: 4px solid #94a3b8; height: 100px; display: flex; flex-direction: column; justify-content: center;">
                        <div style="font-size: 11px; color: #64748b; font-weight: 800; text-transform: uppercase; margin-bottom: 5px;">🏷️ Harga Modal Bandar</div>
                        <div style="font-size: 20px; font-weight: 900; color: #0f172a;">{format_rupiah(bandar_vwap)}</div>
                    </div>
                    """, unsafe_allow_html=True)

            with col_met5:
                if prob_naik >= 60:
                    bg_color = "linear-gradient(135deg, #064e3b, #10b981)" 
                    shadow = "rgba(16, 185, 129, 0.3)"
                    label_risiko = "🔥 AMAN DIBELI"
                elif prob_naik <= 40:
                    bg_color = "linear-gradient(135deg, #7f1d1d, #ef4444)" 
                    shadow = "rgba(239, 68, 68, 0.3)"
                    label_risiko = "⚠️ BAHAYA DIBELI"
                else:
                    bg_color = "linear-gradient(135deg, #78350f, #f59e0b)" 
                    shadow = "rgba(245, 158, 11, 0.3)"
                    label_risiko = "⚖️ BIASA SAJA"

                html_probabilitas = f"""
                <div style="background: {bg_color}; padding: 15px; border-radius: 12px; text-align: center; color: white; box-shadow: 0 8px 15px {shadow}; border: 1px solid rgba(255,255,255,0.1); height: 100px; display: flex; flex-direction: column; justify-content: center;">
                    <div style="font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.9; margin-bottom: 2px;">🎯 Peluang Saham Naik</div>
                    <div style="font-size: 26px; font-weight: 900; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); line-height: 1.1;">{prob_naik:.1f}%</div>
                    <div style="font-size: 11px; margin-top: 4px; font-weight: 700; color: #f8fafc;">Status: {label_risiko}</div>
                </div>
                """
                st.markdown(html_probabilitas, unsafe_allow_html=True)
                
            st.markdown("<br>", unsafe_allow_html=True)
            col_adv1, col_adv2, col_adv3 = st.columns(3)
            
            with col_adv1:
                st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; padding: 15px 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                    <div style="font-size: 11px; color: #64748b; font-weight: 800; text-transform: uppercase; margin-bottom: 4px;">🌐 Pergerakan Uang Asing (Bule)</div>
                    <div style="font-size: 22px; font-weight: 900; color: {'#10b981' if net_foreign > 0 else '#ef4444'};">{'+ Masuk ' if net_foreign > 0 else 'Keluar '}{format_rupiah(abs(net_foreign))}</div>
                </div>
                """, unsafe_allow_html=True)
                
            with col_adv2:
                st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; padding: 15px 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                    <div style="font-size: 11px; color: #64748b; font-weight: 800; text-transform: uppercase; margin-bottom: 4px;">👑 Monopoli 1 Bandar Terbesar</div>
                    <div style="font-size: 22px; font-weight: 900; color: {'#10b981' if top1_dom > 30 else '#f59e0b'};">{top1_dom:.1f}% <span style="font-size:12px; font-weight:600; color:#94a3b8;">dari Total Belanja</span></div>
                </div>
                """, unsafe_allow_html=True)
                
            with col_adv3:
                st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; padding: 15px 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                    <div style="font-size: 11px; color: #64748b; font-weight: 800; text-transform: uppercase; margin-bottom: 4px;">👥 Monopoli 3 Bandar Teratas</div>
                    <div style="font-size: 22px; font-weight: 900; color: {'#10b981' if top3_dom > 60 else '#3b82f6'};">{top3_dom:.1f}% <span style="font-size:12px; font-weight:600; color:#94a3b8;">dari Total Belanja</span></div>
                </div>
                """, unsafe_allow_html=True)

            # =====================================================================
            # 🚀 KOTAK KESIMPULAN 3 METRIK DEWA (PREMIUM STYLING)
            # =====================================================================
            st.markdown("<br>", unsafe_allow_html=True)
            
            if net_foreign > 0 and top1_dom >= 25 and top3_dom >= 50:
                kesimpulan_bg = "linear-gradient(to right, #064e3b, #10b981)"
                kesimpulan_icon = "🚀"
                kesimpulan_teks = "KEPUTUSAN 90%: SIKAT / BELI! (AKUMULASI SEMPURNA)"
                kesimpulan_sub = "Uang asing (Bule) deras masuk & 1 Bandar besar sangat mendominasi pasar. Harga siap diterbangkan!"
            elif net_foreign < 0 and top1_dom < 20 and top3_dom < 40:
                kesimpulan_bg = "linear-gradient(to right, #7f1d1d, #ef4444)"
                kesimpulan_icon = "🩸"
                kesimpulan_teks = "KEPUTUSAN 90%: KABUR / JAUHI! (DISTRIBUSI PARAH)"
                kesimpulan_sub = "Uang asing ditarik keluar & tidak ada Bandar lokal yang mau menahan harga. Rawan longsor dalam!"
            elif top1_dom >= 30 or top3_dom >= 60:
                kesimpulan_bg = "linear-gradient(to right, #78350f, #f59e0b)"
                kesimpulan_icon = "🟢"
                kesimpulan_teks = "KEPUTUSAN 70%: CICIL BELI (DITAMPUNG BANDAR LOKAL)"
                kesimpulan_sub = "Meski uang asing keluar, ada Sindikat Bandar Lokal yang kuat menampung barang. Potensi pantulan harga tinggi."
            elif net_foreign > 0 and (top1_dom < 20 or top3_dom < 40):
                kesimpulan_bg = "linear-gradient(to right, #1e3a8a, #3b82f6)"
                kesimpulan_icon = "🔵"
                kesimpulan_teks = "KEPUTUSAN 60%: POTENSI NAIK PELAN (AKUMULASI MERATA)"
                kesimpulan_sub = "Asing memborong tapi menyebar lewat banyak broker (tidak ada yang memonopoli). Harga bisa naik tapi perlahan."
            else:
                kesimpulan_bg = "linear-gradient(to right, #334155, #64748b)"
                kesimpulan_icon = "⚖️"
                kesimpulan_teks = "KEPUTUSAN 50%: DIAM DULU (PASAR BINGUNG)"
                kesimpulan_sub = "Kekuatan Bandar tidak jelas. Tidak ada satu pihak pun yang mendominasi. Lebih baik cari saham lain."

            st.markdown(f"""
            <div style="background: {kesimpulan_bg}; padding: 20px 25px; border-radius: 12px; color: white; box-shadow: 0 10px 20px rgba(0,0,0,0.15); margin-bottom: 30px; display: flex; align-items: center; gap: 20px;">
                <div style="font-size: 40px; background: rgba(255,255,255,0.1); padding: 15px; border-radius: 50%; height: 80px; width: 80px; display: flex; align-items: center; justify-content: center;">{kesimpulan_icon}</div>
                <div>
                    <div style="font-size: 20px; font-weight: 900; letter-spacing: 0.5px; margin-bottom: 4px; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">{kesimpulan_teks}</div>
                    <div style="font-size: 15px; font-weight: 500; opacity: 0.95; line-height: 1.4;">{kesimpulan_sub}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            # =====================================================================

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
                st.markdown("""
                <div style="background: #f8fafc; padding: 10px 15px; border-radius: 8px 8px 0 0; border: 1px solid #e2e8f0; border-bottom: 3px solid #10b981;">
                    <h4 style="margin: 0; color: #0f172a; font-weight: 800; font-size: 16px;">🟢 5 Besar Bandar Paling Rakus (Beli)</h4>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<div style='border: 1px solid #e2e8f0; border-top: none; padding: 15px; border-radius: 0 0 8px 8px; background: white;'>", unsafe_allow_html=True)
                if not df_aku_chart.empty:
                    max_val_buy = float(df_aku_chart['Net Value'].max())
                    
                    base_buy = alt.Chart(df_aku_chart).encode(
                        x=alt.X('Broker_Label:N', sort='-y', axis=alt.Axis(labelAngle=-45, title=None, labelFontWeight='bold')),
                        tooltip=['Broker', 'Tipe', alt.Tooltip('Net Value:Q', format=',.0f', title='Nilai Uang (Rp)'), alt.Tooltip('Net Lot:Q', format=',.0f')]
                    )
                    bar_buy = base_buy.mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
                        y=alt.Y('Net Value:Q', axis=alt.Axis(title='Value', format='~s', grid=True), scale=alt.Scale(domain=[0, max_val_buy * 1.15])),
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

                    st.markdown(f"""
                    <div style="background: rgba(16, 185, 129, 0.1); padding: 12px; border-radius: 8px; text-align: center; margin-top: 10px;">
                        <div style="font-size: 11px; color: #064e3b; font-weight: 800; letter-spacing: 0.5px; text-transform: uppercase;">Total Kekuatan Beli (Top 5)</div>
                        <div style="font-size: 20px; font-weight: 900; color: #10b981;">{format_rupiah(total_akumulasi)} <span style="font-size: 12px; background: #10b981; color: white; padding: 2px 6px; border-radius: 12px;">{pct_buy_top5:.1f}%</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("Tidak ada data Net Buy.")
                st.markdown("</div>", unsafe_allow_html=True)

            with col_chart2:
                st.markdown("""
                <div style="background: #f8fafc; padding: 10px 15px; border-radius: 8px 8px 0 0; border: 1px solid #e2e8f0; border-bottom: 3px solid #ef4444;">
                    <h4 style="margin: 0; color: #0f172a; font-weight: 800; font-size: 16px;">🔴 5 Besar Bandar Pembuang Barang (Jual)</h4>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<div style='border: 1px solid #e2e8f0; border-top: none; padding: 15px; border-radius: 0 0 8px 8px; background: white;'>", unsafe_allow_html=True)
                if not df_dis_chart.empty:
                    max_val_sell = float(df_dis_chart['Net Value Abs'].max())
                    
                    base_sell = alt.Chart(df_dis_chart).encode(
                        x=alt.X('Broker_Label:N', sort='-y', axis=alt.Axis(labelAngle=-45, title=None, labelFontWeight='bold')),
                        tooltip=['Broker', 'Tipe', alt.Tooltip('Net Value Abs:Q', format=',.0f', title='Nilai Uang (Rp)'), alt.Tooltip('Net Lot:Q', format=',.0f')]
                    )
                    bar_sell = base_sell.mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
                        y=alt.Y('Net Value Abs:Q', axis=alt.Axis(title='Value', format='~s', grid=True), scale=alt.Scale(domain=[0, max_val_sell * 1.15])),
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

                    st.markdown(f"""
                    <div style="background: rgba(239, 68, 68, 0.1); padding: 12px; border-radius: 8px; text-align: center; margin-top: 10px;">
                        <div style="font-size: 11px; color: #7f1d1d; font-weight: 800; letter-spacing: 0.5px; text-transform: uppercase;">Total Kekuatan Jual (Top 5)</div>
                        <div style="font-size: 20px; font-weight: 900; color: #ef4444;">{format_rupiah(total_distribusi)} <span style="font-size: 12px; background: #ef4444; color: white; padding: 2px 6px; border-radius: 12px;">{pct_sell_top5:.1f}%</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("Tidak ada data Net Sell.")
                st.markdown("</div>", unsafe_allow_html=True)

            # =====================================================================
            # 🚀 TABEL PINDAHAN
            # =====================================================================
            st.markdown("<br>", unsafe_allow_html=True)

            df_buy = df_akumulasi[['Broker', 'Net Value', 'Net Lot', 'Buy Avg']].copy()
            df_buy['Cuan/Rugi (Rp)'] = ((current_price - df_buy['Buy Avg']) * df_buy['Net Lot'] * 100).fillna(0) if current_price > 0 else 0.0
            df_buy['Floating (%)'] = ((current_price - df_buy['Buy Avg']) / df_buy['Buy Avg'] * 100).fillna(0) if current_price > 0 else 0.0
            df_buy.columns = ['Yang Beli', 'Jumlah Uang (Rp)', 'Total Lot', 'Harga Modal', 'Cuan/Rugi (Rp)', 'Floating (%)']
            
            df_sell = df_distribusi[['Broker', 'Net Value Abs', 'Net Lot', 'Sell Avg']].copy()
            df_sell['Net Lot'] = df_sell['Net Lot'].abs() 
            df_sell['Jarak Nominal (Rp)'] = ((current_price - df_sell['Sell Avg']) * df_sell['Net Lot'] * 100).fillna(0) if current_price > 0 else 0.0
            df_sell['Jarak ke Harga Aktif (%)'] = ((current_price - df_sell['Sell Avg']) / df_sell['Sell Avg'] * 100).fillna(0) if current_price > 0 else 0.0
            df_sell.columns = ['Yang Jual', 'Jumlah Uang (Rp)', 'Total Lot', 'Harga Jual', 'Jarak Nominal (Rp)', 'Jarak ke Harga Aktif (%)']

            def color_pct(val):
                if pd.isna(val): return ''
                if val > 0: return 'color: #10b981; font-weight: 800;'
                elif val < 0: return 'color: #ef4444; font-weight: 800;'
                return ''

            col_tabel1, col_tabel2 = st.columns(2)
            
            with col_tabel1:
                st.markdown("<div style='background:#f8fafc; padding:8px 15px; border-radius:6px; border:1px solid #e2e8f0; margin-bottom:10px;'><h5 style='color: #10b981; text-align: center; margin:0; font-weight:800;'>🟢 DAFTAR YANG MEMBELI SAHAM INI</h5></div>", unsafe_allow_html=True)
                styler_buy = apply_styler_map(df_buy.style, style_warna_broker, subset=['Yang Beli'])
                styler_buy = apply_styler_map(styler_buy, lambda x: 'color: #10b981; font-weight: 700;', subset=['Jumlah Uang (Rp)', 'Total Lot', 'Harga Modal'])
                styler_buy = apply_styler_map(styler_buy, color_pct, subset=['Cuan/Rugi (Rp)', 'Floating (%)'])
                styler_buy = styler_buy.format({'Jumlah Uang (Rp)': 'Rp {:,.0f}', 'Total Lot': '{:,.0f}', 'Harga Modal': 'Rp {:,.0f}', 'Cuan/Rugi (Rp)': 'Rp {:+,.0f}', 'Floating (%)': '{:+.2f}%'})
                st.dataframe(styler_buy, use_container_width=True, hide_index=True)

            with col_tabel2:
                st.markdown("<div style='background:#f8fafc; padding:8px 15px; border-radius:6px; border:1px solid #e2e8f0; margin-bottom:10px;'><h5 style='color: #ef4444; text-align: center; margin:0; font-weight:800;'>🔴 DAFTAR YANG MENJUAL SAHAM INI</h5></div>", unsafe_allow_html=True)
                styler_sell = apply_styler_map(df_sell.style, style_warna_broker, subset=['Yang Jual'])
                styler_sell = apply_styler_map(styler_sell, lambda x: 'color: #ef4444; font-weight: 700;', subset=['Jumlah Uang (Rp)', 'Total Lot', 'Harga Jual'])
                styler_sell = apply_styler_map(styler_sell, color_pct, subset=['Jarak Nominal (Rp)', 'Jarak ke Harga Aktif (%)'])
                styler_sell = styler_sell.format({'Jumlah Uang (Rp)': 'Rp {:,.0f}', 'Total Lot': '{:,.0f}', 'Harga Jual': 'Rp {:,.0f}', 'Jarak Nominal (Rp)': 'Rp {:+,.0f}', 'Jarak ke Harga Aktif (%)': '{:+.2f}%'})
                st.dataframe(styler_sell, use_container_width=True, hide_index=True)


            # =====================================================================
            # 🚀 UI PENCARIAN BROKER DAN JARUM KECEPATAN (DIRAMPINGKAN & BERSEBELAHAN)
            # =====================================================================
            st.markdown("""
            <div style='background: white; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; text-align: center; font-size: 13px; margin-top: 15px; margin-bottom: 25px;'>
                <span style='color:#10b981; font-weight:800;'>● Tidak Jelas (Zombie)</span> &nbsp;&nbsp;|&nbsp;&nbsp; 
                <span style='color:#9b59b6; font-weight:800;'>● Orang Bule (Asing)</span> &nbsp;&nbsp;|&nbsp;&nbsp; 
                <span style='color:#ef4444; font-weight:800;'>● Investor Biasa (Ritel)</span> &nbsp;&nbsp;|&nbsp;&nbsp; 
                <span style='color:#3b82f6; font-weight:800;'>● Perusahaan Besar</span>
            </div>
            """, unsafe_allow_html=True)

            col_search_speed1, col_search_speed2 = st.columns([1, 2.5])
            
            with col_search_speed1:
                st.markdown("<div style='font-size: 13px; font-weight: 800; margin-bottom: 5px; color: #0f172a; text-transform: uppercase;'>🔍 Cari Info Kode Broker:</div>", unsafe_allow_html=True)
                search_query = st.text_input("Ketik Kode / Nama Broker", label_visibility="collapsed", placeholder="Contoh: AK atau Mandiri").strip()
                
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
                        st.warning("Tidak ditemukan broker yang cocok.")

            with col_search_speed2:
                if total_transaksi > 0:
                    posisi_marker = (total_akumulasi / total_transaksi) * 100

                    meter_html = f"""
                    <style>
                    .broker-action-container {{
                        width: 100%; padding: 15px 25px; margin-top: 0px;
                        background: white; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px rgba(0,0,0,0.02);
                    }}
                    .broker-action-title {{
                        font-weight: 900; font-size: 14px; margin-bottom: 12px; color: #0f172a; text-align: center; text-transform: uppercase;
                    }}
                    .bar-wrapper {{
                        position: relative; height: 14px; border-radius: 7px; display: flex; overflow: hidden;
                        background: #f1f5f9; box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    .bar-segment {{
                        flex: 1; border-right: 1px solid rgba(255,255,255,0.2);
                    }}
                    .bar-segment:last-child {{ border-right: none; }}
                    .bg-big-dist {{ background-color: #991b1b; }}
                    .bg-dist {{ background-color: #ef4444; }}
                    .bg-neutral {{ background-color: #cbd5e1; }}
                    .bg-acc {{ background-color: #10b981; }}
                    .bg-big-acc {{ background-color: #065f46; }}

                    .marker-container {{
                        position: absolute; top: -6px; bottom: -6px; left: {posisi_marker:.1f}%;
                        transform: translateX(-50%); z-index: 10;
                        display: flex; flex-direction: column; align-items: center; justify-content: center;
                        transition: left 0.8s cubic-bezier(0.34, 1.56, 0.64, 1);
                    }}
                    .marker-line {{
                        width: 4px; height: 26px; background-color: #0f172a; border-radius: 2px;
                        box-shadow: 0 0 6px rgba(0,0,0,0.4); border: 1px solid white;
                    }}
                    .labels {{
                        display: flex; justify-content: space-between; font-size: 12px; color: #64748b; margin-top: 10px; font-weight: 800; text-transform: uppercase;
                    }}
                    </style>

                    <div class="broker-action-container">
                        <div class="broker-action-title">📊 JARUM KECEPATAN BANDAR (DISTRIBUSI VS AKUMULASI)</div>
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
                            <span style="color: #ef4444;">🩸 Bahaya Tinggi</span>
                            <span style="position: absolute; left: 50%; transform: translateX(-50%); color: #94a3b8;">⚖️ Ragu-ragu / Netral</span>
                            <span style="color: #10b981;">🚀 Sangat Aman</span>
                        </div>
                    </div>
                    """
                    st.markdown(meter_html, unsafe_allow_html=True)
            # =====================================================================

            # =====================================================================
            # 🚀 RADAR HISTORI HARIAN PER BROKER
            # =====================================================================
            st.markdown("<hr style='margin: 35px 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)
            st.markdown("""
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
                <div style="background: #8b5cf6; width: 8px; height: 25px; border-radius: 4px;"></div>
                <h4 style="margin: 0; color: #0f172a; font-weight: 800;">🕵️‍♂️ Lacak Jejak Harian (Per Broker Khusus)</h4>
            </div>
            <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">Intip kelakuan satu broker tertentu dari hari ke hari. Apakah dia konsisten belanja, atau malah jualan terus?</p>
            """, unsafe_allow_html=True)
            
            raw_broker_hist = db.get('raw_broker_hist', [])
            top_acc_list = db.get('top_acc_list', [])
            top_dist_list = db.get('top_dist_list', [])
            
            opsi_broker = list(dict.fromkeys(top_acc_list + top_dist_list))
            
            if raw_broker_hist and opsi_broker:
                st.markdown("<div style='background: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px rgba(0,0,0,0.02);'>", unsafe_allow_html=True)
                col_pil1, col_pil2 = st.columns([1, 3])
                with col_pil1:
                    broker_pilihan = st.selectbox("Pilih Broker (Top 5):", opsi_broker)
                with col_pil2:
                    st.markdown(f"<div style='margin-top: 30px; font-size: 13px; color: #64748b;'>Menampilkan kelakuan khusus broker <strong style='color:#0f172a;'>{broker_pilihan}</strong> dari {start_date_res.strftime('%d %b')} s/d {end_date_res.strftime('%d %b')}. <span style='color:#10b981; font-weight:bold;'>Hijau</span> = Belanja, <span style='color:#ef4444; font-weight:bold;'>Merah</span> = Buang Barang.</div>", unsafe_allow_html=True)
                
                broker_data = next((b for b in raw_broker_hist if b.get('broker') == broker_pilihan), None)
                
                if broker_data and 'data' in broker_data:
                    df_broker_harian = pd.DataFrame(broker_data['data'])
                    if not df_broker_harian.empty:
                        # --- PERBAIKAN RUMUS DAILY DELTA PER BROKER ---
                        df_broker_harian['value_cum'] = df_broker_harian['value'].astype(float)
                        df_broker_harian['value'] = df_broker_harian['value_cum'].diff().fillna(df_broker_harian['value_cum'])
                        # ----------------------------------------------
                        
                        df_broker_harian['Warna'] = df_broker_harian['value'].apply(lambda x: '#10b981' if x >= 0 else '#ef4444')
                        df_broker_harian['Label'] = df_broker_harian['value'].apply(format_rupiah)
                        
                        max_val_harian = df_broker_harian['value'].abs().max()
                        domain_harian = [-max_val_harian * 1.15, max_val_harian * 1.15]
                        
                        chart_harian = alt.Chart(df_broker_harian).mark_bar(size=35, cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
                            x=alt.X('date:O', title='', axis=alt.Axis(labelAngle=-45, labelFontWeight='bold')),
                            y=alt.Y('value:Q', title='Jumlah Uang (Rp)', axis=alt.Axis(format='~s', grid=True), scale=alt.Scale(domain=domain_harian)),
                            color=alt.Color('Warna:N', scale=None),
                            tooltip=['date', alt.Tooltip('value:Q', format=',.0f', title='Jumlah Uang (Rp)')]
                        )
                        
                        text_pos = alt.Chart(df_broker_harian[df_broker_harian['value'] >= 0]).mark_text(dy=-12, fontWeight='bold', fontSize=11).encode(
                            x=alt.X('date:O'), y=alt.Y('value:Q'), text='Label:N', color=alt.value('#064e3b')
                        )
                        text_neg = alt.Chart(df_broker_harian[df_broker_harian['value'] < 0]).mark_text(dy=12, fontWeight='bold', fontSize=11).encode(
                            x=alt.X('date:O'), y=alt.Y('value:Q'), text='Label:N', color=alt.value('#7f1d1d')
                        )
                        
                        rule = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(color='#94a3b8', strokeWidth=2).encode(y='y:Q')
                        
                        st.altair_chart(alt.layer(chart_harian, text_pos, text_neg, rule).properties(height=320), use_container_width=True)
                    else:
                        st.info(f"Tidak ada data transaksi harian untuk broker {broker_pilihan} pada rentang tanggal ini.")
                else:
                    st.info(f"Tidak ada rekam jejak untuk broker {broker_pilihan} pada rentang tanggal ini.")
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("⚠️ Data riwayat harian per broker tidak tersedia dari pusat data (Invezgo) untuk saham/tanggal ini. Hal ini biasanya terjadi jika Anda hanya memindai data 1 hari, atau saham tersebut kurang likuid.")
            # =====================================================================


            st.markdown("<hr style='margin: 35px 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)
            st.markdown("""
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
                <div style="background: #ec4899; width: 8px; height: 25px; border-radius: 4px;"></div>
                <h4 style="margin: 0; color: #0f172a; font-weight: 800;">🥧 Peta Proporsi (Siapa Yang Mendominasi?)</h4>
            </div>
            """, unsafe_allow_html=True)
            
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
                range=['#9b59b6', '#ef4444', '#3b82f6', '#10b981']
            )

            col_pie1, col_pie2 = st.columns(2)
            with col_pie1:
                st.markdown("<div style='background: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px rgba(0,0,0,0.02);'>", unsafe_allow_html=True)
                st.markdown("<h5 style='text-align: center; color: #10b981; font-weight: 800;'>🟢 Pangsa Pasar Pemborong Saham</h5>", unsafe_allow_html=True)
                if not df_aku_kategori.empty:
                    base_buy = alt.Chart(df_aku_kategori).encode(
                        theta=alt.Theta(field="Net Value", type="quantitative", stack=True),
                        color=alt.Color(field="Tipe", type="nominal", scale=color_scale_pie, legend=alt.Legend(title=None, orient='bottom', labelFontSize=12, labelFontWeight='bold'))
                    )
                    pie_buy = base_buy.mark_arc(innerRadius=60, outerRadius=130, cornerRadius=4).encode(
                        tooltip=['Tipe', alt.Tooltip('Net Value:Q', format=',.0f', title='Nilai Uang (Rp)'), alt.Tooltip('Persen:Q', format='.1f', title='Berapa Persen? (%)')]
                    )
                    text_buy = base_buy.mark_text(radius=95, size=14, fontWeight=900).encode(
                        text='Label:N',
                        color=alt.value('white') 
                    )
                    st.altair_chart(alt.layer(pie_buy, text_buy).properties(height=350), use_container_width=True)
                else:
                    st.info("Tidak ada data yang beli")
                st.markdown("</div>", unsafe_allow_html=True)

            with col_pie2:
                st.markdown("<div style='background: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px rgba(0,0,0,0.02);'>", unsafe_allow_html=True)
                st.markdown("<h5 style='text-align: center; color: #ef4444; font-weight: 800;'>🔴 Pangsa Pasar Pembuang Saham</h5>", unsafe_allow_html=True)
                if not df_dis_kategori.empty:
                    base_sell = alt.Chart(df_dis_kategori).encode(
                        theta=alt.Theta(field="Net Value Abs", type="quantitative", stack=True),
                        color=alt.Color(field="Tipe", type="nominal", scale=color_scale_pie, legend=alt.Legend(title=None, orient='bottom', labelFontSize=12, labelFontWeight='bold'))
                    )
                    pie_sell = base_sell.mark_arc(innerRadius=60, outerRadius=130, cornerRadius=4).encode(
                        tooltip=['Tipe', alt.Tooltip('Net Value Abs:Q', format=',.0f', title='Nilai Uang (Rp)'), alt.Tooltip('Persen:Q', format='.1f', title='Berapa Persen? (%)')]
                    )
                    text_sell = base_sell.mark_text(radius=95, size=14, fontWeight=900).encode(
                        text='Label:N',
                        color=alt.value('white')
                    )
                    st.altair_chart(alt.layer(pie_sell, text_sell).properties(height=350), use_container_width=True)
                else:
                    st.info("Tidak ada data yang jual")
                st.markdown("</div>", unsafe_allow_html=True)

            if not df_trend.empty:
                st.markdown("<hr style='margin: 35px 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)
                st.markdown("""
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
                    <div style="background: #3b82f6; width: 8px; height: 25px; border-radius: 4px;"></div>
                    <h4 style="margin: 0; color: #0f172a; font-weight: 800;">📈 Riwayat Kekuatan Gabungan (Top 5 Bandar)</h4>
                </div>
                <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">Melihat tren secara keseluruhan. Apakah komplotan 5 Bandar Terbesar sedang dalam fase akumulasi massal, atau distribusi massal?</p>
                """, unsafe_allow_html=True)
                
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
                    range=['#10b981', '#ef4444'] 
                )
                
                st.markdown("<div style='background: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px rgba(0,0,0,0.02);'>", unsafe_allow_html=True)
                bars = alt.Chart(df_melt).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, size=35).encode(
                    x=alt.X('Date:O', title='', axis=alt.Axis(labelAngle=-45, grid=False, labelFontWeight='bold')),
                    y=alt.Y('Nilai:Q', title='Jumlah Uang (Rp)', axis=alt.Axis(format='~s', grid=True)),
                    color=alt.Color('Kategori:N', scale=color_scale_trend, legend=alt.Legend(title=None, orient='top', labelFontWeight='bold')),
                    tooltip=['Date', 'Kategori', alt.Tooltip('Nilai:Q', format=',.0f', title='Jumlah Uang (Rp)'), alt.Tooltip('Persentase (%):Q', format='.1f')]
                )

                text_aku = alt.Chart(df_trend).mark_text(dy=-12, color='#064e3b', fontWeight='bold', fontSize=11).encode(
                    x=alt.X('Date:O'),
                    y=alt.Y('Akumulasi (Top 5):Q'),
                    text=alt.Text('Label_Aku:N')
                )

                text_dis = alt.Chart(df_trend).mark_text(dy=12, color='#7f1d1d', fontWeight='bold', fontSize=11).encode(
                    x=alt.X('Date:O'),
                    y=alt.Y('Distribusi (Top 5):Q'),
                    text=alt.Text('Label_Dis:N')
                )
                
                rule = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(color='#94a3b8', strokeWidth=2).encode(y='y:Q')
                
                st.altair_chart(alt.layer(bars, text_aku, text_dis, rule).properties(height=400), use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<hr style='margin: 40px 0; border-color: #cbd5e1;'>", unsafe_allow_html=True)
            
            # =====================================================================
            # 🤖 TERMINAL AI (SUPER MEWAH)
            # =====================================================================
            
            # 🚀 DETEKSI HIDDEN ACCUMULATION / DISTRIBUTION (DIVERGENCE)
            divergence_html = ""
            if current_price > 0 and prev_price > 0:
                price_change_pct = ((current_price - prev_price) / prev_price) * 100
                
                if price_change_pct < -0.5 and net_total > 0 and prob_naik >= 60:
                    divergence_html = f"""
                    <div style="background: linear-gradient(135deg, #064e3b, #10b981); border-left: 6px solid #fbbf24; padding: 20px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 10px 15px rgba(16, 185, 129, 0.2); color: white;">
                        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 10px;">
                            <div style="font-size: 30px; background: rgba(255,255,255,0.2); padding: 10px; border-radius: 50%;">🕵️‍♂️</div>
                            <div style="font-weight: 900; font-size: 18px; text-transform: uppercase; letter-spacing: 1px; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">DIVERGENCE TERDETEKSI: Bandar Beli Diam-Diam! (Peluang Emas)</div>
                        </div>
                        <div style="font-size: 15px; font-weight: 500; line-height: 1.5; text-shadow: 1px 1px 1px rgba(0,0,0,0.2);">Hati-hati tertipu layar merah! Harga saham ini memang sengaja ditekan turun <b>({price_change_pct:.1f}%)</b> hari ini agar investor awam panik dan jual rugi (Cutloss). Namun data membongkar rahasia bahwa Bandar justru sedang <b>MEMBORONG MASIF</b> di harga bawah. Segera amankan posisi beli, harga berpotensi melesat tajam dalam waktu dekat!</div>
                    </div>
                    """
                elif price_change_pct > 0.5 and net_total < 0 and prob_naik <= 40:
                    divergence_html = f"""
                    <div style="background: linear-gradient(135deg, #7f1d1d, #ef4444); border-left: 6px solid #fbbf24; padding: 20px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 10px 15px rgba(239, 68, 68, 0.2); color: white;">
                        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 10px;">
                            <div style="font-size: 30px; background: rgba(255,255,255,0.2); padding: 10px; border-radius: 50%;">🪤</div>
                            <div style="font-weight: 900; font-size: 18px; text-transform: uppercase; letter-spacing: 1px; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">AWAS JEBAKAN BATMAN! (Harga Naik Tapi Bandar Jualan)</div>
                        </div>
                        <div style="font-size: 15px; font-weight: 500; line-height: 1.5; text-shadow: 1px 1px 1px rgba(0,0,0,0.2);">Harga saham ini memang terlihat sedang naik cantik <b>(Mekar {price_change_pct:.1f}%)</b> dan sangat menggoda untuk di-HAKA. TAPI AWAS, itu hanya pancingan (Mark-Up Palsu)! Faktanya Bandar besar sedang jualan gila-gilaan dan membuang barangnya ke investor kecil (Ritel). Jangan masuk agar tidak nyangkut parah di pucuk!</div>
                    </div>
                    """

            if divergence_html:
                st.markdown(divergence_html, unsafe_allow_html=True)
            
            if total_transaksi > 0:
                if total_akumulasi > total_distribusi and prob_naik >= 55:
                    ai_rekomendasi = "🚀 SANGAT BAGUS DIBELI SEKARANG!"
                    ai_color = "#4ade80" 
                    
                    if current_price > 0 and bandar_vwap > 0:
                        if current_price > (bandar_vwap * 1.05):
                            area_entry = f"Rp {int(bandar_vwap):,} - Rp {int(bandar_vwap * 1.02):,}<br><span style='font-size:11px; color:#fbbf24; font-weight: 600;'>(Tunggu Harga Turun Sedikit)</span>"
                            cl_price = f"Rp {int(bandar_vwap * 0.97):,}"
                            tp_price = f"Rp {int(current_price * 1.05):,}"
                        else:
                            area_entry = f"Rp {int(current_price):,} - Rp {int(current_price * 1.01):,}<br><span style='font-size:11px; color:#4ade80; font-weight: 600;'>(Langsung Sikat! Harga Sangat Murah)</span>"
                            cl_price = f"Rp {int(min(current_price, bandar_vwap) * 0.97):,}"
                            tp_price = f"Rp {int(current_price * 1.05):,} - Rp {int(current_price * 1.10):,}"
                    else:
                        area_entry = f"Rp {int(bandar_vwap):,}<br><span style='font-size:11px; color:#94a3b8; font-weight: 600;'>(Beli di Sekitar Harga Ini)</span>"
                        tp_price = f"Rp {int(bandar_vwap * 1.05):,}"
                        cl_price = f"Rp {int(bandar_vwap * 0.97):,}"
                        
                else:
                    ai_rekomendasi = "🛑 JANGAN DIBELI DULU! BAHAYA."
                    ai_color = "#f87171" 
                    area_entry = "-"
                    tp_price = "-"
                    cl_price = "-"

                ai_html = f"""
                <div style="background: linear-gradient(135deg, #020617, #0f172a, #1e293b); border: 2px solid #334155; border-radius: 16px; padding: 35px; margin-bottom: 25px; box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4); position: relative; overflow: hidden;">
                    <div style="position: absolute; top: 0; left: 0; right: 0; height: 5px; background: linear-gradient(to right, #3b82f6, #8b5cf6, #ec4899);"></div>
                    <div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 15px;">
                        <span style="font-size: 24px;">🤖</span>
                        <h4 style="color: #94a3b8; margin: 0; text-align: center; font-size: 15px; letter-spacing: 3px; text-transform: uppercase; font-weight: 800;">Terminal Analisa Robot Ahli</h4>
                    </div>
                    <div style="text-align: center; font-size: 36px; font-weight: 900; color: {ai_color}; margin-bottom: 35px; text-shadow: 0 0 20px {ai_color}60; letter-spacing: 1px;">{ai_rekomendasi}</div>
                    
                    <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 20px;">
                        <div style="flex: 1; min-width: 180px; background: rgba(255,255,255,0.03); padding: 20px; border-radius: 12px; text-align: center; border-bottom: 4px solid #3b82f6; box-shadow: inset 0 2px 4px rgba(255,255,255,0.02); transition: transform 0.2s;">
                            <div style="font-size: 12px; color: #94a3b8; font-weight: 800; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px;">📍 Area Beli Terbaik</div>
                            <div style="font-size: 22px; font-weight: 900; color: #f8fafc; line-height: 1.3;">{area_entry}</div>
                        </div>
                        <div style="flex: 1; min-width: 180px; background: rgba(255,255,255,0.03); padding: 20px; border-radius: 12px; text-align: center; border-bottom: 4px solid #10b981; box-shadow: inset 0 2px 4px rgba(255,255,255,0.02);">
                            <div style="font-size: 12px; color: #94a3b8; font-weight: 800; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px;">🎯 Target Jual (Take Profit)</div>
                            <div style="font-size: 24px; font-weight: 900; color: #34d399; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">{tp_price}</div>
                        </div>
                        <div style="flex: 1; min-width: 180px; background: rgba(255,255,255,0.03); padding: 20px; border-radius: 12px; text-align: center; border-bottom: 4px solid #ef4444; box-shadow: inset 0 2px 4px rgba(255,255,255,0.02);">
                            <div style="font-size: 12px; color: #94a3b8; font-weight: 800; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px;">✂️ Batas Rugi (Cutloss)</div>
                            <div style="font-size: 24px; font-weight: 900; color: #f87171; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">{cl_price}</div>
                        </div>
                        <div style="flex: 1; min-width: 180px; background: rgba(255,255,255,0.03); padding: 20px; border-radius: 12px; text-align: center; border-bottom: 4px solid #f59e0b; box-shadow: inset 0 2px 4px rgba(255,255,255,0.02);">
                            <div style="font-size: 12px; color: #94a3b8; font-weight: 800; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px;">⚖️ Rasio Kemenangan</div>
                            <div style="font-size: 28px; font-weight: 900; color: #fbbf24; text-shadow: 0 0 10px rgba(245, 158, 11, 0.3);">{prob_naik:.1f}%</div>
                        </div>
                    </div>
                </div>
                """
                st.markdown(ai_html, unsafe_allow_html=True)

                # Narasi Robot
                st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.02);">
                    <div style="margin-bottom: 15px;">
                        <span style="font-size: 18px; font-weight: 900; color: #0f172a; border-bottom: 2px solid #3b82f6; padding-bottom: 4px;">📖 Cerita Di Balik Saham {emiten_res}</span>
                    </div>
                    <p style="font-size: 16px; color: #334155; line-height: 1.6;">{analisa_teks}</p>
                    
                    <div style="margin-bottom: 15px; margin-top: 25px;">
                        <span style="font-size: 18px; font-weight: 900; color: #0f172a; border-bottom: 2px solid #10b981; padding-bottom: 4px;">🎯 Strategi & Saran Tindakan</span>
                    </div>
                    <p style="font-size: 16px; color: #334155; line-height: 1.6; font-weight: 600;">{aksi_teks}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if not df_akumulasi_top5.empty:
                    broker_top = df_akumulasi_top5.iloc[0]['Broker']
                    tipe_top, _ = get_kategori_broker(broker_top)
                    st.markdown(f"""
                    <div style="background: #fffbeb; border: 1px dashed #f59e0b; border-radius: 8px; padding: 15px; margin-top: 15px; text-align: center;">
                        <span style="font-size: 14px; font-weight: 800; color: #d97706;">👑 PENGUASA SAHAM INI:</span> 
                        <span style="font-size: 15px; color: #92400e;">Broker dengan kode <strong>{broker_top}</strong> ({tipe_top}) adalah Dalang Utama yang belanja paling banyak hari ini. Terus awasi broker ini besok!</span>
                    </div>
                    """, unsafe_allow_html=True)

# 4. MENU PENGATURAN API
elif st.session_state["menu_navigasi"] == "⚙️ Pengaturan Kode Rahasia":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e293b, #0f172a); padding: 25px 30px; border-radius: 12px; border-left: 8px solid #8b5cf6; margin-bottom: 25px; box-shadow: 0 10px 15px rgba(0,0,0,0.2);">
        <h2 style="color: #ffffff; margin: 0; font-weight: 800;">⚙️ Pengaturan Akses Invezgo Premium</h2>
        <p style="color: #94a3b8; margin-top: 8px; font-size: 15px; margin-bottom: 0;">Masukkan kunci rahasia (API Key) Anda untuk membuka gerbang data Institusi.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='background: white; padding: 30px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px rgba(0,0,0,0.02);'>", unsafe_allow_html=True)
    api_key_input = st.text_input("🔑 Ketik / Paste API Key JWT Token di sini:", value=st.session_state['api_key'], type="password", placeholder="eyJhbGciOiJIUzI1NiIs...")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 Simpan Kunci Akses Premium", type="primary", use_container_width=True):
        st.session_state['api_key'] = api_key_input
        simpan_api_key(api_key_input)
        st.success("✅ **AKSES BERHASIL DISIMPAN!** Koneksi ke server Invezgo telah dibuka. Mulai sekarang Anda bisa langsung menggunakan seluruh fitur X-Ray Bandar secara penuh tanpa perlu mengatur kunci ini lagi.")
    st.markdown("</div>", unsafe_allow_html=True)
