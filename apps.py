import streamlit as st
from supabase import create_client, Client
import random
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Renungan Digital", page_icon="🙏")

# --- 2. KONEKSI SUPABASE ---
# Mengambil URL dan KEY dari Streamlit Secrets
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 3. LOAD DAFTAR AYAT ---
@st.cache_data
def load_ayat():
    try:
        with open("ayat.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        return ["Tetaplah berdoa.", "Kasihilah sesamamu manusia."]

quotes_list = load_ayat()

# --- 4. LOGIKA STATE ---
if 'current_quote' not in st.session_state:
    st.session_state.current_quote = ""

# --- 5. UI UTAMA ---
st.title("🙏 Diary Renungan Digital")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["✨ Acak Ayat", "📝 Tulis Log", "📜 Riwayat"])

# --- TAB 1: ACAK AYAT ---
with tab1:
    st.subheader("Inspirasi Hari Ini")
    if st.button("🔄 Dapatkan Ayat Baru"):
        st.session_state.current_quote = random.choice(quotes_list)
    
    display_quote = st.session_state.current_quote if st.session_state.current_quote else "Klik tombol di atas."
    st.info(f"### {display_quote}")

# --- TAB 2: TULIS & SIMPAN ---
with tab2:
    st.subheader("Catat Perenunganmu")
    
    # Input otomatis jika ada ayat dari Tab 1
    input_ayat = st.text_area("Ayat:", value=st.session_state.current_quote, key="input_ayat_box")
    input_notes = st.text_area("Catatan Pribadi:", placeholder="Apa pesan Tuhan hari ini...", key="input_notes_box")
    
    if st.button("💾 Simpan ke Cloud"):
        if input_ayat and input_notes:
            try:
                # INSERT ke tabel database_renungan
                supabase.table("database_renungan").insert({
                    "ayat": input_ayat,
                    "notes": input_notes
                }).execute()
                
                # Reset Form
                st.session_state.current_quote = ""
                st.session_state["input_ayat_box"] = ""
                st.session_state["input_notes_box"] = ""
                
                st.success("✅ Berhasil disimpan di Supabase!")
                st.rerun()
            except Exception as e:
                st.error(f"Gagal simpan! Pastikan RLS di Supabase sudah 'Disable' atau 'Allow Insert'. Error: {e}")
        else:
            st.warning("⚠️ Mohon isi ayat dan catatan.")

# --- TAB 3: RIWAYAT ---
with tab3:
    st.subheader("Daftar Renungan Lampau")
    try:
        # SELECT dari tabel database_renungan
        response = supabase.table("database_renungan").select("*").order("created_at", desc=True).execute()
        
        if not response.data:
            st.write("Belum ada data.")
        else:
            for item in response.data:
                # Format tanggal sederhana
                tgl = item['created_at'][:10] if 'created_at' in item else "N/A"
                with st.expander(f"📅 {tgl} | {item['ayat'][:30]}..."):
                    st.write(f"**Ayat:** {item['ayat']}")
                    st.write(f"**Catatan:** {item['notes']}")
    except Exception as e:
        st.error(f"Gagal memuat data. Cek nama tabel di Supabase! Error: {e}")
