import streamlit as st

# Mengatur konfigurasi halaman (HARUS PALING ATAS di main.py)
st.set_page_config(page_title="Screener Saham Pro", page_icon="📈", layout="wide")

# Import module halaman yang sudah kita pisah
import halaman_depan

# --- FUNGSI NAVIGASI ---
def navigasi_sidebar():
    st.sidebar.title("Menu Navigasi")
    
    # Inisialisasi session state untuk menu jika belum ada
    if "menu_aktif" not in st.session_state:
        st.session_state["menu_aktif"] = "🏠 Halaman Depan"

    daftar_menu = [
        "🏠 Halaman Depan", 
        "📊 Deteksi Saham Cepat", 
        "🕵️‍♂️ Deteksi Bandar Penuh", 
        "⚙️ Pengaturan Kode Rahasia"
    ]

    pilihan = st.sidebar.radio("Pilih Menu:", daftar_menu, key="menu_aktif")
    
    st.sidebar.markdown("---")
    st.sidebar.info("Aplikasi Pencari Saham Otomatis V2.0\n\n⚡ **Versi Modular Pro**")
    
    return pilihan

# --- ROUTING HALAMAN ---
menu_pilihan = navigasi_sidebar()

if menu_pilihan == "🏠 Halaman Depan":
    # Memanggil fungsi tampilkan() dari file halaman_depan.py
    halaman_depan.tampilkan()

elif menu_pilihan == "📊 Deteksi Saham Cepat":
    st.title("Bagian Deteksi Saham Cepat")
    st.write("Nanti kode teknikal kita masukkan ke sini.")

elif menu_pilihan == "🕵️‍♂️ Deteksi Bandar Penuh":
    st.title("Bagian Bandarmologi")
    st.write("Nanti kode Invezgo API kita masukkan ke sini.")

elif menu_pilihan == "⚙️ Pengaturan Kode Rahasia":
    st.title("Pengaturan API")
    st.write("Nanti pengaturan config kita masukkan ke sini.")
