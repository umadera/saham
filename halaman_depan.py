import streamlit as st
import yfinance as yf
import pandas as pd

# Fungsi untuk mengambil data dengan cache agar tidak berat saat di-refresh
@st.cache_data(ttl=300) # Data di-cache selama 5 menit
def ambil_data_indeks():
    indeks_global = {
        "🇮🇩 IHSG (Indonesia)": "^JKSE",
        "🇺🇸 Dow Jones (US)": "^DJI",
        "🇺🇸 S&P 500 (US)": "^GSPC",
        "🇺🇸 NASDAQ (US)": "^IXIC",
        "🇯🇵 Nikkei 225 (Jepang)": "^N225",
        "🇭🇰 Hang Seng (Hong Kong)": "^HSI"
    }
    
    hasil_indeks = {}
    for nama, ticker in indeks_global.items():
        try:
            # Ambil data 5 hari terakhir untuk memastikan kita dapat data penutupan sebelumnya
            df = yf.Ticker(ticker).history(period="5d")
            if len(df) >= 2:
                harga_sekarang = df['Close'].iloc[-1]
                harga_kemarin = df['Close'].iloc[-2]
                perubahan_poin = harga_sekarang - harga_kemarin
                perubahan_persen = (perubahan_poin / harga_kemarin) * 100
                
                hasil_indeks[nama] = {
                    "harga": harga_sekarang,
                    "poin": perubahan_poin,
                    "persen": perubahan_persen
                }
            else:
                hasil_indeks[nama] = None
        except Exception:
            hasil_indeks[nama] = None
            
    return hasil_indeks

def tampilkan():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e293b, #0f172a); padding: 25px 30px; border-radius: 12px; border-left: 8px solid #3b82f6; margin-bottom: 25px; box-shadow: 0 10px 15px rgba(0,0,0,0.2);">
        <h2 style="color: #ffffff; margin: 0; font-weight: 800;">🌐 Dashboard Makro Global</h2>
        <p style="color: #94a3b8; margin-top: 8px; font-size: 15px; margin-bottom: 0;">Pantau sentimen bursa dunia yang mempengaruhi arah IHSG hari ini.</p>
    </div>
    """, unsafe_allow_html=True)

    data_indeks = ambil_data_indeks()
    
    # Membuat 3 kolom untuk baris pertama (IHSG & US)
    st.markdown("#### 🇺🇸 Pengaruh Wall Street & Lokal")
    col1, col2, col3 = st.columns(3)
    kolom_atas = [col1, col2, col3]
    daftar_atas = ["🇮🇩 IHSG (Indonesia)", "🇺🇸 Dow Jones (US)", "🇺🇸 NASDAQ (US)"]
    
    for i, nama in enumerate(daftar_atas):
        with kolom_atas[i]:
            data = data_indeks.get(nama)
            if data:
                st.metric(
                    label=nama, 
                    value=f"{data['harga']:,.2f}", 
                    delta=f"{data['poin']:,.2f} ({data['persen']:+.2f}%)"
                )
            else:
                st.metric(label=nama, value="Data Off", delta="-")

    st.markdown("<hr style='margin-top: 10px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    
    # Membuat 3 kolom untuk baris kedua (Asia & S&P)
    st.markdown("#### 🌏 Pengaruh Regional Asia & Lainnya")
    col4, col5, col6 = st.columns(3)
    kolom_bawah = [col4, col5, col6]
    daftar_bawah = ["🇯🇵 Nikkei 225 (Jepang)", "🇭🇰 Hang Seng (Hong Kong)", "🇺🇸 S&P 500 (US)"]
    
    for i, nama in enumerate(daftar_bawah):
        with kolom_bawah[i]:
            data = data_indeks.get(nama)
            if data:
                st.metric(
                    label=nama, 
                    value=f"{data['harga']:,.2f}", 
                    delta=f"{data['poin']:,.2f} ({data['persen']:+.2f}%)"
                )
            else:
                st.metric(label=nama, value="Data Off", delta="-")
                
    st.info("💡 **Tips:** Jika Wall Street (US) dan Regional (Asia) kompak menghijau, IHSG biasanya akan memiliki dorongan kuat untuk ikut naik di pagi hari.")
