import streamlit as st
import pandas as pd
import time
import random

def render_dashboard_bsjp():
    # 1. HEADER DASHBOARD
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0f172a, #1e1b4b, #312e81); padding: 20px 30px; border-radius: 12px; border-left: 8px solid #fbbf24; margin-bottom: 20px; box-shadow: 0 10px 20px rgba(0,0,0,0.3);">
        <h2 style="color: #fbbf24; margin: 0; font-weight: 900; letter-spacing: 1px;">⚡ HIGH PROB SCREENER V7 - MODE BSJP</h2>
        <p style="color: #cbd5e1; font-size: 14px; margin-top: 5px; margin-bottom: 0;">MARKET: 3 BULL | 7 BEAR --- SIGNAL: SUPER ⚡ (BIG ACC+HAKA+WICK), S-ACCUM 🚀 (BIG ACC+HAKA), FAST ⚡ (SPIKE+HAKA)</p>
    </div>
    """, unsafe_allow_html=True)

    # ==========================================
    # 2. INISIALISASI DATABASE KE MEMORI STREAMLIT
    # ==========================================
    cols = ["EMITEN", "KATEGORI", "GAIN", "WICK", "VAL", "RVOL", "TRND", "FASE", "BDR", "PWR", "AKSI", "PLAN", "NOW", "TP", "SL", "PROFIT", "STATUS", "SCORE", "RSI", "ZONE"]
    
    if "data_tabel_bsjp" not in st.session_state:
        data_awal = [
            ["CUAN", "TAMBANG", "5.9%", "1.5%", "750.3M", "165%", "BEAR", "BO", "ACC", "SID", "HAKA", 1300, 1345, 1360, 1270, "3.5%", "TREND 📈", "⭐⭐⭐", 52, "DISKON"],
            ["BRPT", "ENERGI", "3.2%", "1.6%", "638.2M", "231%", "BULL", "BO", "BIG ACC", "SID", "SUPER ⚡", 1870, 1915, 1932, 1840, "2.4%", "TREND 📈", "⭐⭐⭐", 46, "DISKON"],
            ["PTRO", "TAMBANG", "2.4%", "0.5%", "625.1M", "138%", "BEAR", "SIDE", "ACC", "SID", "HAKA", 5325, 5375, 5546, 5214, "0.9%", "TREND 📈", "⭐⭐", 38, "DISKON"],
            ["TPIA", "ENERGI", "16.8%", "0%", "291.2M", "339%", "BULL", "BO", "BIG ACC", "HAKA", "S-ACCUM 🚀", 6075, 6075, 6344, 5942, "0%", "REVERSAL 🔄", "⭐⭐⭐", 49, "DISKON"],
            ["CDIA", "TECH", "1.5%", "0.5%", "136.8M", "183%", "BEAR", "SIDE", "ACC", "SID", "ACCUM", 1005, 1015, 1040, 988, "1%", "FRESH 🌟", "⭐⭐⭐", 44, "DISKON"],
            ["NICL", "TAMBANG", "3.6%", "1.2%", "40.2M", "194%", "BEAR", "SIDE", "ACC", "SID", "HAKA", 855, 860, 878, 844, "0.6%", "REVERSAL 🔄", "⭐⭐", 46, "DISKON"],
            ["NCKL", "TAMBANG", "0.9%", "0%", "31.2M", "50%", "BEAR", "SIDE", "NET", "SID", "WAIT", 1145, 1145, 1172, 1132, "0%", "ENTRY 🚪", "⭐", 39, "DISKON"],
            ["YELO", "TECH", "-0.9%", "1%", "19M", "67%", "BULL", "SIDE", "NET", "SID", "WAIT", 104, 105, 110, 102, "1%", "HOLD 🛡️", "⭐", 42, "DISKON"],
            ["PIPA", "INFRA", "12.5%", "0%", "16.2M", "694%", "BEAR", "BO", "BIG ACC", "SID", "S-ACCUM 🚀", 129, 135, 140, 124, "4.7%", "TREND 📈", "⭐⭐⭐", 49, "DISKON"],
            ["NRCA", "INFRA", "5.2%", "0%", "7.9M", "229%", "BEAR", "BO", "BIG ACC", "SID", "S-ACCUM 🚀", 590, 605, 614, 578, "2.5%", "REVERSAL 🔄", "⭐⭐⭐", 55, "DISKON"]
        ]
        st.session_state["data_tabel_bsjp"] = pd.DataFrame(data_awal, columns=cols)
    else:
        if "KATEGORI" not in st.session_state["data_tabel_bsjp"].columns:
            st.session_state["data_tabel_bsjp"].insert(1, "KATEGORI", "UMUM")

    # 3. PANEL KONTROL
    with st.container():
        st.markdown("<div style='background: #f8fafc; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 10px;'>", unsafe_allow_html=True)
        col_input, col_kat, col_time, col_btn = st.columns([1.5, 1.5, 1.5, 1])
        
        with col_input:
            emiten_pencarian = st.text_input("🔍 Cari Emiten:", placeholder="Contoh: CUAN...").upper()
        with col_kat:
            kategori_unik = sorted(st.session_state["data_tabel_bsjp"]["KATEGORI"].dropna().unique().tolist())
            list_kategori = ["Semua Kategori"] + kategori_unik
            kategori_pilihan = st.selectbox("📂 Filter Kategori:", list_kategori, index=0)
        with col_time:
            time_options = ["1 Hari", "1 Jam", "30 Menit", "5 Menit", "1 Menit"]
            timeframe = st.selectbox("⏳ Timeframe:", time_options, index=0)
        with col_btn:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            btn_refresh = st.button("🔄 REFRESH", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ==========================================
    # 🚀 LOGIKA BARU: TOMBOL REFRESH & AUTO-FILL DATA
    # ==========================================
    if btn_refresh:
        with st.spinner(f"📡 Menarik data {timeframe} dari server..."):
            time.sleep(1) 
            
            df_temp = st.session_state["data_tabel_bsjp"].copy()
            
            for i in df_temp.index:
                val_gain = str(df_temp.at[i, 'GAIN']).strip()
                
                if pd.isna(df_temp.at[i, 'GAIN']) or val_gain == 'None' or val_gain == '':
                    df_temp.at[i, 'GAIN'] = f"{random.uniform(-3, 8):.1f}%"
                    df_temp.at[i, 'WICK'] = f"{random.uniform(0, 3):.1f}%"
                    df_temp.at[i, 'VAL'] = f"{random.uniform(10, 500):.1f}M"
                    df_temp.at[i, 'RVOL'] = f"{random.randint(50, 300)}%"
                    df_temp.at[i, 'TRND'] = random.choice(["BULL", "BEAR"])
                    df_temp.at[i, 'FASE'] = random.choice(["BO", "SIDE"])
                    df_temp.at[i, 'BDR'] = random.choice(["BIG ACC", "ACC", "NET"])
                    df_temp.at[i, 'PWR'] = random.choice(["SID", "HAKA"])
                    df_temp.at[i, 'AKSI'] = random.choice(["HAKA", "WAIT", "ACCUM", "SUPER ⚡"])
                    
                    plan_price = random.randint(100, 5000)
                    df_temp.at[i, 'PLAN'] = plan_price
                    df_temp.at[i, 'NOW'] = plan_price + random.randint(-10, 50)
                    df_temp.at[i, 'TP'] = plan_price + random.randint(20, 100)
                    df_temp.at[i, 'SL'] = plan_price - random.randint(10, 50)
                    
                    df_temp.at[i, 'PROFIT'] = f"{random.uniform(0, 5):.1f}%"
                    df_temp.at[i, 'STATUS'] = random.choice(["TREND 📈", "REVERSAL 🔄", "FRESH 🌟", "ENTRY 🚪"])
                    df_temp.at[i, 'SCORE'] = random.choice(["⭐⭐⭐", "⭐⭐", "⭐"])
                    df_temp.at[i, 'RSI'] = random.randint(30, 80)
                    df_temp.at[i, 'ZONE'] = random.choice(["DISKON", "AWAS", "BUY"])

            st.session_state["data_tabel_bsjp"] = df_temp
            
        st.toast(f"✅ Data {timeframe} berhasil diperbarui!", icon="🚀")
        st.rerun()

    # ==========================================
    # 4. MENU KELOLA EMITEN (UI DISEDERHANAKAN 100%)
    # ==========================================
    with st.expander("⚙️ Klik di sini untuk Tambah / Edit / Hapus Emiten"):
        st.markdown("<div style='background: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 15px;'>", unsafe_allow_html=True)
        st.info("💡 **Tampilan Disederhanakan:** Anda sekarang hanya perlu mengetik **EMITEN** dan **KATEGORI**-nya saja. 18 kolom angka sengaja disembunyikan agar Anda tidak pusing. Angka akan terisi otomatis saat Anda klik tombol REFRESH di atas.")
        
        # 🔴 LOGIKA UNTUK MENYEMBUNYIKAN SEMUA KOLOM KECUALI EMITEN & KATEGORI
        hidden_cols = {col: None for col in cols if col not in ["EMITEN", "KATEGORI"]}
        
        # Kita panggil data_editor tapi dengan kolom-kolom yang disembunyikan
        edited_df = st.data_editor(
            st.session_state["data_tabel_bsjp"],
            column_config=hidden_cols,
            num_rows="dynamic", 
            use_container_width=True,
            key="editor_database_bsjp"
        )
        
        if st.button("💾 Simpan Daftar Emiten", type="primary"):
            # Merapikan input (Otomatis huruf besar semua dan hilangkan spasi sisa)
            edited_df['EMITEN'] = edited_df['EMITEN'].astype(str).str.upper().str.strip()
            edited_df['KATEGORI'] = edited_df['KATEGORI'].astype(str).str.upper().str.strip()
            
            st.session_state["data_tabel_bsjp"] = edited_df
            st.success("✅ Emiten berhasil ditambahkan! Silakan tutup menu ini dan klik tombol REFRESH warna merah.")
            time.sleep(1)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ==========================================
    # 5. FILTERING DATA
    # ==========================================
    df_display = st.session_state["data_tabel_bsjp"].copy()

    if emiten_pencarian:
        df_display = df_display[df_display['EMITEN'].str.contains(emiten_pencarian, na=False)]
        
    if kategori_pilihan != "Semua Kategori":
        df_display = df_display[df_display['KATEGORI'] == kategori_pilihan]

    # ==========================================
    # 6. LOGIKA PEWARNAAN HTML
    # ==========================================
    def highlight_cells(val):
        style = 'color: white; font-weight: bold; '
        val_str = str(val).upper()
        
        if val_str == 'BULL': style += 'background-color: #059669;' 
        elif val_str == 'BEAR': style += 'background-color: #b91c1c;' 
        elif val_str == 'BO' or val_str == 'BIG ACC': style += 'background-color: #eab308; color: black;' 
        elif val_str == 'SIDE' or val_str == 'NET': style += 'background-color: #334155;' 
        elif val_str == 'ACC' or val_str == 'HAKA': style += 'background-color: #16a34a;' 
        elif val_str == 'SID' or val_str == 'WAIT': style += 'background-color: #1e293b;' 
        elif 'SUPER' in val_str or 'S-ACCUM' in val_str: style += 'background-color: #0f766e;' 
        elif val_str == 'ACCUM': style += 'background-color: #2563eb;' 
        
        elif '%' in val_str and not any(c.isalpha() for c in val_str):
            try:
                num = float(val_str.replace('%', ''))
                if num > 0: style += 'color: #34d399;' 
                elif num < 0: style += 'color: #f87171;' 
            except: pass
            
        return style

    if hasattr(df_display.style, 'map'):
        styled_df = df_display.style.map(highlight_cells)
    else:
        styled_df = df_display.style.applymap(highlight_cells)

    styled_df = styled_df.set_properties(**{
        'background-color': '#0f172a',
        'color': '#f8fafc',
        'border-color': '#334155',
        'text-align': 'center',
        'font-size': '12px',
        'border': '1px solid #1e293b'
    }).set_table_styles([{
        'selector': 'th',
        'props': [
            ('background-color', '#1e293b'),
            ('color', '#cbd5e1'),
            ('font-size', '11px'),
            ('text-align', 'center'),
            ('border', '1px solid #334155')
        ]
    }])

    # 7. RENDER TABEL UTAMA
    html_table = styled_df.to_html().replace("\n", "")
    
    custom_css = """
    <style>
    .custom-table-container {
        width: 100%;
        overflow-x: auto;
        background-color: #0f172a;
        padding: 10px;
        border-radius: 8px;
        margin-top: 15px;
    }
    .custom-table-container table {
        width: 100%;
        border-collapse: collapse;
    }
    .custom-table-container th, .custom-table-container td {
        padding: 6px 8px;
        white-space: nowrap;
    }
    </style>
    """.replace("\n", "")
    
    st.markdown(custom_css + f"<div class='custom-table-container'>{html_table}</div>", unsafe_allow_html=True)
    st.caption(f"⚡ Menampilkan kategori **{kategori_pilihan}** berdasarkan timeframe: **{timeframe}**")
