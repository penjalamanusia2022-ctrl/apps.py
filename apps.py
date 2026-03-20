import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Renungan Harian", page_icon="🙏", layout="centered")

# --- 2. FUNGSI LOAD DATA AYAT ---
@st.cache_data
def load_quotes():
    try:
        with open("ayat.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        return ["Akulah jalan dan kebenaran dan hidup."]

quotes_list = load_quotes()

# --- 3. KONEKSI GOOGLE SHEETS ---
# Mengambil koneksi yang dikonfigurasi di Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 4. LOGIKA STATE ---
if 'current_quote' not in st.session_state:
    st.session_state.current_quote = ""

# --- 5. UI APLIKASI ---
st.title("🙏 Aplikasi Renungan Digital")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["✨ Acak Ayat", "📝 Catatan Baru", "📜 Riwayat Log"])

# --- TAB 1: ACAK AYAT ---
with tab1:
    st.subheader("Inspirasi Untukmu")
    if st.session_state.current_quote:
        st.info(f"### {st.session_state.current_quote}")
    else:
        st.write("Klik tombol di bawah untuk mendapatkan ayat hari ini.")
    
    if st.button("🔄 Acak Ayat Baru"):
        st.session_state.current_quote = random.choice(quotes_list)
        st.rerun()

# --- TAB 2: INPUT & SIMPAN (VERSI PERBAIKAN) ---
with tab2:
    st.subheader("Tulis Perenungan")
    
    # PERBAIKAN: Gunakan fungsi callback atau logika session_state yang bersih
    # Kita tidak menggunakan parameter 'value' di sini, tapi langsung lewat session_state
    
    # Pastikan key 'area_ayat' terisi jika ada current_quote dari Tab 1
    if st.session_state.current_quote and not st.session_state.get("area_ayat"):
        st.session_state["area_ayat"] = st.session_state.current_quote

    input_ayat = st.text_area("Ayat terpilih:", 
                              height=100, 
                              key="area_ayat")
    
    input_notes = st.text_area("Catatan/Notes Pribadi:", 
                               placeholder="Apa pesan ayat ini bagimu?", 
                               key="area_notes")

    if st.button("💾 Simpan Permanen ke Cloud"):
        if input_ayat.strip() and input_notes.strip():
            try:
                # 1. Membaca data lama
                existing_data = conn.read()
                
                # 2. Membuat baris baru
                new_row = pd.DataFrame({
                    "ayat": [input_ayat],
                    "notes": [input_notes],
                    "timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                })
                
                # 3. Gabungkan
                updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                
                # 4. Update ke Google Sheets
                conn.update(data=updated_df)
                
                # --- 5. PROSES RESET YANG BENAR ---
                st.session_state.current_quote = ""
                st.session_state["area_ayat"] = ""
                st.session_state["area_notes"] = ""
                
                st.success("✅ Catatan berhasil disimpan!")
                st.rerun() 
                
            except Exception as e:
                st.error(f"Gagal simpan. Error: {e}")
        else:
            st.warning("⚠️ Mohon isi semua kolom.")
# --- TAB 3: RIWAYAT LOG ---
with tab3:
    st.subheader("📜 Riwayat Catatan Anda")
    try:
        # Membaca data dari Google Sheets
        df = conn.read()
        
        if df is None or df.empty:
            st.info("Belum ada catatan yang tersimpan di Cloud.")
        else:
            # Menampilkan dari yang terbaru (reverse)
            for index, row in df.iloc[::-1].iterrows():
                with st.expander(f"📅 {row['timestamp']} | {str(row['ayat'])[:30]}..."):
                    st.markdown(f"**Ayat:**\n{row['ayat']}")
                    st.markdown(f"**Catatan:**\n{row['notes']}")
                    st.caption(f"ID: {index}")
    except Exception as e:
        st.error("Gagal memuat data dari Google Sheets.")

# --- FOOTER ---
st.markdown("---")
st.caption("Aplikasi Renungan v2.0 - Tersimpan di Google Sheets")
