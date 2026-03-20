import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
from datetime import datetime

# --- CONFIG HALAMAN ---
st.set_page_config(page_title="Renungan Digital", page_icon="🙏")

# --- KONEKSI KE GOOGLE SHEETS ---
# Hapus variabel url yang lama, gunakan ini:
conn = st.connection("gsheets", type=GSheetsConnection)


# --- DATA AYAT ---
# 1. Membaca ayat dari file ayat.txt
with open("ayat.txt", "r", encoding="utf-8") as f:
    quotes_list = [line.strip() for line in f.readlines() if line.strip()]

# 2. Sisanya tetap seperti kode sebelumnya
if 'current_quote' not in st.session_state:
    st.session_state.current_quote = ""

st.title("🙏 Log Renungan Selamanya")

tab1, tab2, tab3 = st.tabs(["✨ Acak Ayat", "📝 Catatan Baru", "📜 Riwayat Log"])

# --- TAB 1: RANDOM ---
with tab1:
    st.subheader("Inspirasi Hari Ini")
    if st.session_state.current_quote:
        st.info(f"### {st.session_state.current_quote}")
    
    if st.button("🔄 Acak Ayat"):
        st.session_state.current_quote = random.choice(quotes_list)
        st.rerun()

# --- TAB 2: SIMPAN KE GOOGLE SHEETS ---
with tab2:
    st.subheader("Simpan ke Cloud")
    ayat_val = st.text_area("Ayat:", value=st.session_state.current_quote)
    notes_val = st.text_area("Catatan:", placeholder="Tulis di sini...", key="notes")

    if st.button("💾 Simpan ke Google Sheets"):
        if ayat_val and notes_val:
            # 1. Ambil data yang sudah ada
            existing_data = conn.read(spreadsheet=url, usecols=[0,1,2])
            
            # 2. Buat data baru
            new_row = pd.DataFrame({
                "ayat": [ayat_val],
                "notes": [notes_val],
                "timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            })
            
            # 3. Gabungkan dan update
            updated_df = pd.concat([existing_data, new_row], ignore_index=True)
            conn.update(spreadsheet=url, data=updated_df)
            
            st.success("✅ Tersimpan di Google Sheets!")
            st.session_state.current_quote = ""
            st.rerun()
        else:
            st.error("Isi semua data!")

# --- TAB 3: BACA DARI GOOGLE SHEETS ---
with tab3:
    st.subheader("Riwayat dari Cloud")
    try:
        # Membaca data terbaru dari Google Sheets
        df = conn.read(spreadsheet=url)
        
        if df.empty:
            st.write("Belum ada data.")
        else:
            # Tampilkan 500 data terakhir (dibalik agar yang terbaru di atas)
            for index, row in df.iloc[::-1].head(500).iterrows():
                with st.expander(f"📅 {row['timestamp']} | {str(row['ayat'])[:30]}..."):
                    st.write(f"**Ayat:** {row['ayat']}")
                    st.write(f"**Catatan:** {row['notes']}")
    except:
        st.write("Gagal memuat data. Pastikan URL benar dan izin akses Editor aktif.")
