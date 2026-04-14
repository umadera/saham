import streamlit as st
import pandas as pd

def render_dashboard_bsjp():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0f172a, #1e1b4b, #312e81); padding: 20px 30px; border-radius: 12px; border-left: 8px solid #fbbf24; margin-bottom: 20px; box-shadow: 0 10px 20px rgba(0,0,0,0.3);">
        <h2 style="color: #fbbf24; margin: 0; font-weight: 900; letter-spacing: 1px;">⚡ HIGH PROB SCREENER V7 - MODE BSJP</h2>
        <p style="color: #cbd5e1; font-size: 14px; margin-top: 5px; margin-bottom: 0;">MARKET: 3 BULL | 7 BEAR --- SIGNAL: SUPER ⚡ (BIG ACC+HAKA+WICK), S-ACCUM 🚀 (BIG ACC+HAKA), FAST ⚡ (SPIKE+HAKA)</p>
    </div>
    """, unsafe_allow_html=True)

    # ==========================================
    # 1. MOCK DATA (Simulasi Data seperti di Gambar)
    # Nanti Anda bisa ganti data ini dengan tarikan API atau Database Anda
    # ==========================================
    data = [
        ["CUAN", "5.9%", "1.5%", "750.3M", "165%", "BEAR", "BO", "ACC", "SID", "HAKA", 1300, 1345, 1360, 1270, "3.5%", "TREND 📈", "⭐⭐⭐", 52, "DISKON"],
        ["BRPT", "3.2%", "1.6%", "638.2M", "231%", "BULL", "BO", "BIG ACC", "SID", "SUPER ⚡", 1870, 1915, 1932, 1840, "2.4%", "TREND 📈", "⭐⭐⭐", 46, "DISKON"],
        ["PTRO", "2.4%", "0.5%", "625.1M", "138%", "BEAR", "SIDE", "ACC", "SID", "HAKA", 5325, 5375, 5546, 5214, "0.9%", "TREND 📈", "⭐⭐", 38, "DISKON"],
        ["TPIA", "16.8%", "0%", "291.2M", "339%", "BULL", "BO", "BIG ACC", "HAKA", "S-ACCUM 🚀", 6075, 6075, 6344, 5942, "0%", "REVERSAL 🔄", "⭐⭐⭐", 49, "DISKON"],
        ["CDIA", "1.5%", "0.5%", "136.8M", "183%", "BEAR", "SIDE", "ACC", "SID", "ACCUM", 1005, 1015, 1040, 988, "1%", "FRESH 🌟", "⭐⭐⭐", 44, "DISKON"],
        ["NICL", "3.6%", "1.2%", "40.2M", "194%", "BEAR", "SIDE", "ACC", "SID", "HAKA", 855, 860, 878, 844, "0.6%", "REVERSAL 🔄", "⭐⭐", 46, "DISKON"],
        ["NCKL", "0.9%", "0%", "31.2M", "50%", "BEAR", "SIDE", "NET", "SID", "WAIT", 1145, 1145, 1172, 1132, "0%", "ENTRY 🚪", "⭐", 39, "DISKON"],
        ["YELO", "-0.9%", "1%", "19M", "67%", "BULL", "SIDE", "NET", "SID", "WAIT", 104, 105, 110, 102, "1%", "HOLD 🛡️", "⭐", 42, "DISKON"],
        ["PIPA", "12.5%", "0%", "16.2M", "694%", "BEAR", "BO", "BIG ACC", "SID", "S-ACCUM 🚀", 129, 135, 140, 124, "4.7%", "TREND 📈", "⭐⭐⭐", 49, "DISKON"],
        ["NRCA", "5.2%", "0%", "7.9M", "229%", "BEAR", "BO", "BIG ACC", "SID", "S-ACCUM 🚀", 590, 605, 614, 578, "2.5%", "REVERSAL 🔄", "⭐⭐⭐", 55, "DISKON"]
    ]
    
    cols = ["EMITEN", "GAIN", "WICK", "VAL", "RVOL", "TRND", "FASE", "BDR", "PWR", "AKSI", "PLAN", "NOW", "TP", "SL", "PROFIT", "STATUS", "SCORE", "RSI", "ZONE"]
    df = pd.DataFrame(data, columns=cols)

    # ==========================================
    # 2. LOGIKA PEWARNAAN (STYLING)
    # ==========================================
    def highlight_cells(val):
        style = 'color: white; font-weight: bold; '
        val_str = str(val).upper()
        
        # Pewarnaan Background Dasar
        if val_str == 'BULL': style += 'background-color: #059669;' # Hijau Gelap
        elif val_str == 'BEAR': style += 'background-color: #b91c1c;' # Merah Gelap
        elif val_str == 'BO' or val_str == 'BIG ACC': style += 'background-color: #eab308; color: black;' # Kuning Emas
        elif val_str == 'SIDE' or val_str == 'NET': style += 'background-color: #334155;' # Abu-abu
        elif val_str == 'ACC' or val_str == 'HAKA': style += 'background-color: #16a34a;' # Hijau Terang
        elif val_str == 'SID' or val_str == 'WAIT': style += 'background-color: #1e293b;' # Biru Dongker Gelap
        elif 'SUPER' in val_str or 'S-ACCUM' in val_str: style += 'background-color: #0f766e;' # Teal
        elif val_str == 'ACCUM': style += 'background-color: #2563eb;' # Biru
        
        # Pewarnaan Teks Angka
        elif '%' in val_str and not any(c.isalpha() for c in val_str):
            num = float(val_str.replace('%', ''))
            if num > 0: style += 'color: #34d399;' # Teks Hijau
            elif num < 0: style += 'color: #f87171;' # Teks Merah
            else: style += 'color: #cbd5e1;'
            
        return style

    # Gunakan fungsi yang aman untuk semua versi Pandas
    if hasattr(df.style, 'map'):
        styled_df = df.style.map(highlight_cells)
    else:
        styled_df = df.style.applymap(highlight_cells)

    # Styling Table keseluruhan agar persis seperti gambar (Dark Theme)
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

    
# ==========================================
    # 3. RENDER TABEL SEBAGAI HTML CUSTOM
    # Ini memastikan tabel terlihat 'rapat' ala TradingView
    # ==========================================
    html_table = styled_df.to_html()
    
    # 🔴 TAMBAHAN KRUSIAL: Hapus semua "enter" (newline) agar tidak dibaca sebagai teks oleh Streamlit
    html_table = html_table.replace("\n", "") 
    
    # CSS Tambahan agar tabel responsive & tidak ada jarak putih
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
    """.replace("\n", "") # 🔴 Hapus enter di CSS juga
    
    st.markdown(custom_css + f"<div class='custom-table-container'>{html_table}</div>", unsafe_allow_html=True)
