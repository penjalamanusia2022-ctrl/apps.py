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

# --- 4. LOGIKA STATE (inisialisasi sebelum widget dibuat) ---
st.session_state.setdefault('current_quote', "")
st.session_state.setdefault('input_ayat_box', st.session_state.current_quote)
st.session_state.setdefault('input_notes_box', "")

# --- 5. UI UTAMA ---
st.title("🙏 Diary Renungan Digital")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["✨ Acak Ayat", "📝 Tulis Log", "📜 Riwayat"])

# --- TAB 1: ACAK AYAT ---
with tab1:
    st.subheader("Inspirasi Hari Ini")
    if st.button("🔄 Dapatkan Ayat Baru"):
        st.session_state.current_quote = random.choice(quotes_list)
        # Perbarui default input_ayat_box agar Tab 2 menunjukkan quote baru saat dibuka
        st.session_state.input_ayat_box = st.session_state.current_quote
        # rerun agar perubahan terlihat segera
        st.experimental_rerun()

    display_quote = st.session_state.current_quote if st.session_state.current_quote else "Klik tombol di atas."
    st.info(f"### {display_quote}")

# --- TAB 2: TULIS & SIMPAN ---
with tab2:
    st.subheader("Catat Perenunganmu")

    # Buat widget (nilai awal berasal dari session_state yang sudah di-set di atas)
    input_ayat = st.text_area("Ayat:", value=st.session_state.get('input_ayat_box', ''), key="input_ayat_box", height=150)
    input_notes = st.text_area("Catatan Pribadi:", placeholder="Apa pesan Tuhan hari ini...", key="input_notes_box", height=200)

    def on_submit():
        val_ayat = st.session_state.get('input_ayat_box', '').strip()
        val_notes = st.session_state.get('input_notes_box', '').strip()
        if not (val_ayat and val_notes):
            st.warning("⚠️ Mohon isi ayat dan catatan.")
            return

        try:
            # INSERT ke tabel database_renungan
            res = supabase.table("database_renungan").insert({
                "ayat": val_ayat,
                "notes": val_notes
            }).execute()

            # Periksa response error dari supabase client (library bisa mengembalikan error di .error atau status_code)
            # Penanganan sederhana: jika ada error atribut, tampilkan
            if hasattr(res, "error") and res.error:
                st.error(f"Gagal simpan! Pastikan RLS di Supabase sudah 'Disable' atau 'Allow Insert'. Error: {res.error}")
                return

        except Exception as e:
            st.error(f"Gagal simpan! Pastikan RLS di Supabase sudah 'Disable' atau 'Allow Insert'. Error: {e}")
            return

        # Reset form safely inside callback
        st.session_state.current_quote = ""
        st.session_state["input_ayat_box"] = ""
        st.session_state["input_notes_box"] = ""
        st.success("✅ Berhasil disimpan di Supabase!")
        # Segarkan UI untuk menampilkan perubahan (opsional)
        st.experimental_rerun()

    st.button("💾 Simpan ke Cloud", on_click=on_submit)

# --- TAB 3: RIWAYAT ---
with tab3:
    st.subheader("Daftar Renungan Lampau")
    try:
        # SELECT dari tabel database_renungan
        response = supabase.table("database_renungan").select("*").order("created_at", desc=True).execute()

        # Jika library mengemas hasil di .data atau .json, menyesuaikan sederhana:
        data = None
        if hasattr(response, "data"):
            data = response.data
        elif isinstance(response, dict) and "data" in response:
            data = response["data"]
        else:
            # fallback: coba response itself
            data = response

        if not data:
            st.write("Belum ada data.")
        else:
            for item in data:
                # Format tanggal sederhana
                tgl = item.get('created_at', '')[:10] if isinstance(item, dict) else "N/A"
                ayat_preview = item.get('ayat', '')[:30] if isinstance(item, dict) else ""
                notes = item.get('notes', '') if isinstance(item, dict) else ""
                with st.expander(f"📅 {tgl} | {ayat_preview}..."):
                    st.write(f"**Ayat:** {item.get('ayat', '')}")
                    st.write(f"**Catatan:** {notes}")
    except Exception as e:
        st.error(f"Gagal memuat data. Cek nama tabel di Supabase! Error: {e}")
