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

    # 2. PANEL KONTROL (INPUT EMITEN, TIMEFRAME, & TOMBOL REFRESH)
    with st.container():
        st.markdown("<div style='background: #f8fafc; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 20px;'>", unsafe_allow_html=True)
        
        # Dibagi jadi 3 kolom agar tombol Refresh punya tempat khusus di kanan
        col_input, col_time, col_btn = st.columns([2, 2, 1])
        
        with col_input:
            emiten_bsjp = st.text_input("🔍 Cari Emiten Khusus:", placeholder="Contoh: BREN, CUAN...").upper()
        
        with col_time:
            time_options = ["1 Hari", "1 Jam", "30 Menit", "5 Menit", "1 Menit"]
            timeframe = st.selectbox("⏳ Pilih Timeframe:", time_options, index=0)
            
        with col_btn:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            btn_refresh = st.button("🔄 REFRESH", type="primary", use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

    # Efek Loading saat tombol Refresh ditekan
    if btn_refresh:
        with st.spinner(f"📡 Menarik data bandarmologi untuk timeframe {timeframe}..."):
            time.sleep(0.8) # Jeda simulasi loading sistem (bisa dihapus jika API sudah cepat)
        st.toast(f"✅ Data {timeframe} berhasil diperbarui!", icon="🚀")

    # ==========================================
    # 3. MOCK DATA (Simulasi Data)
    # ==========================================
    # Sedikit trik agar data 'terlihat' berubah saat Anda refresh beda timeframe (Untuk preview UI)
    acak = 0 if not btn_refresh else random.randint(-2, 2)
    
    data = [
        ["CUAN", f"{5.9 + acak:.1f}%", "1.5%", "750.3M", "165%", "BEAR", "BO", "ACC", "SID", "HAKA", 1300, 1345, 1360, 1270, "3.5%", "TREND 📈", "⭐⭐⭐", 52, "DISKON"],
        ["BRPT", f"{3.2 + acak:.1f}%", "1.6%", "638.2M", "231%", "BULL", "BO", "BIG ACC", "SID", "SUPER ⚡", 1870, 1915, 1932, 1840, "2.4%", "TREND 📈", "⭐⭐⭐", 46, "DISKON"],
        ["PTRO", f"{2.4 + (acak*0.5):.1f}%", "0.5%", "625.1M", "138%", "BEAR", "SIDE", "ACC", "SID", "HAKA", 5325, 5375, 5546, 5214, "0.9%", "TREND 📈", "⭐⭐", 38, "DISKON"],
        ["TPIA", f"{16.8 + acak:.1f}%", "0%", "291.2M", "339%", "BULL", "BO", "BIG ACC", "HAKA", "S-ACCUM 🚀", 6075, 6075, 6344, 5942, "0%", "REVERSAL 🔄", "⭐⭐⭐", 49, "DISKON"],
        ["CDIA", "1.5%", "0.5%", "136.8M", "183%", "BEAR", "SIDE", "ACC", "SID", "ACCUM", 1005, 1015, 1040, 988, "1%", "FRESH 🌟", "⭐⭐⭐", 44, "DISKON"],
        ["NICL", "3.6%", "1.2%", "40.2M", "194%", "BEAR", "SIDE", "ACC", "SID", "HAKA", 855, 860, 878, 844, "0.6%", "REVERSAL 🔄", "⭐⭐", 46, "DISKON"],
        ["NCKL", "0.9%", "0%", "31.2M", "50%", "BEAR", "SIDE", "NET", "SID", "WAIT", 1145, 1145, 1172, 1132, "0%", "ENTRY 🚪", "⭐", 39, "DISKON"],
        ["YELO", "-0.9%", "1%", "19M", "67%", "BULL", "SIDE", "NET", "SID", "WAIT", 104, 105, 110, 102, "1%", "HOLD 🛡️", "⭐", 42, "DISKON"],
        ["PIPA", "12.5%", "0%", "16.2M", "694%", "BEAR", "BO", "BIG ACC", "SID", "S-ACCUM 🚀", 129, 135, 140, 124, "4.7%", "TREND 📈", "⭐⭐⭐", 49, "DISKON"],
        ["NRCA", "5.2%", "0%", "7.9M", "229%", "BEAR", "BO", "BIG ACC", "SID", "S-ACCUM 🚀", 590, 605, 614, 578, "2.5%", "REVERSAL 🔄", "⭐⭐⭐", 55, "DISKON"]
    ]
    
    cols = ["EMITEN", "GAIN", "WICK", "VAL", "RVOL", "TRND", "FASE", "BDR", "PWR", "AKSI", "PLAN", "NOW", "TP", "SL", "PROFIT", "STATUS", "SCORE", "RSI", "ZONE"]
    df = pd.DataFrame(data, columns=cols)

    # Logika Filter Emiten
    if emiten_bsjp:
        df = df[df['EMITEN'].str.contains(emiten_bsjp)]

    # ==========================================
    # 4. LOGIKA PEWARNAAN (STYLING)
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

    if hasattr(df.style, 'map'):
        styled_df = df.style.map(highlight_cells)
    else:
        styled_df = df.style.applymap(highlight_cells)

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

    # 5. RENDER TABEL (COMPACT HTML)
    html_table = styled_df.to_html().replace("\n", "")
    
    custom_css = """
    <style>
    .custom-table-container {
        width: 100%;
        overflow-x: auto;
        background-color: #0f172a;
        padding: 10px;
        border-radius: 8px;
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
    
    # Keterangan Timeframe Aktif
    st.caption(f"⚡ Menampilkan data terakhir berdasarkan timeframe: **{timeframe}**")
