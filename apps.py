import streamlit as st
from supabase import create_client, Client
import random
import re

# --- 1. KONEKSI SUPABASE ---
# Pastikan URL dan KEY sudah ada di Streamlit Secrets
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 2. FUNGSI HELPER ---
def safe_rerun():
    if hasattr(st, "rerun"): st.rerun()
    else: st.experimental_rerun()

# Fungsi Load Ayat tanpa @st.cache_data agar sinkron dengan GitHub commit
def load_ayat():
    try:
        with open("ayat.txt", "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            return lines if lines else ["Tetaplah berdoa."]
    except Exception as e:
        return [f"Gagal memuat ayat.txt: {e}"]

# --- 3. LOGIN SESSION ---
if 'user_email' not in st.session_state:
    st.title("🔐 Akses Diary Pribadi")
    st.markdown("Masukkan email Anda untuk memisahkan catatan pribadi dengan pengguna lain.")
    
    email_input = st.text_input("Masukkan Email Anda:", placeholder="contoh: budi@email.com")
    
    if st.button("Masuk"):
        # Validasi format email sederhana
        if email_input and re.match(r"[^@]+@[^@]+\.[^@]+", email_input):
            st.session_state.user_email = email_input.strip().lower()
            st.rerun()
        else:
            st.error("⚠️ Mohon masukkan format email yang valid.")
    
    st.info("💡 Semua catatan Anda akan disimpan berdasarkan email ini.")
    st.stop()

current_user = st.session_state.user_email

# --- 4. INISIALISASI STATE ---
if "in_at" not in st.session_state:
    st.session_state["in_at"] = ""
if "in_nt" not in st.session_state:
    st.session_state["in_nt"] = ""

# --- 5. LOGIKA FUNGSI (CALLBACK) ---
def handle_save():
    val_at = st.session_state["in_at"]
    val_nt = st.session_state["in_nt"]
    
    if val_at and val_nt:
        try:
            # Pastikan tabel 'database_renungan' punya kolom 'author'
            supabase.table("database_renungan").insert({
                "ayat": val_at, 
                "notes": val_nt,
                "author": current_user 
            }).execute()
            
            # Reset form secara bersih
            st.session_state["in_at"] = ""
            st.session_state["in_nt"] = ""
            st.toast("✅ Berhasil disimpan ke Cloud!", icon="🎉")
        except Exception as e:
            st.error(f"Gagal Simpan: {e}")
    else:
        st.warning("⚠️ Isi ayat dan catatan terlebih dahulu.")

def handle_acak():
    # Selalu panggil fungsi load_ayat() terbaru agar perubahan file terbaca
    quotes_list = load_ayat()
    st.session_state["in_at"] = random.choice(quotes_list)

# --- 6. TAMPILAN UTAMA ---
st.sidebar.title("👤 Profil User")
st.sidebar.info(f"Login sebagai:\n**{current_user}**")
if st.sidebar.button("Keluar (Logout)"):
    del st.session_state.user_email
    st.rerun()
st.text_area("KAMU menerima dengan cuma-cuma, berikan dengan cuma-cuma.)

st.title("🙏 Diary Renungan Digital")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["✨ Acak Ayat", "📝 Tulis Log", "📜 Riwayat Saya"])

# --- TAB 1: ACAK AYAT ---
with tab1:
    st.subheader("Inspirasi Hari Ini")
    st.button("🔄 Dapatkan Ayat Baru", on_click=handle_acak)
    
    q_now = st.session_state["in_at"] if st.session_state["in_at"] else "Klik tombol di atas untuk memulai."
    st.info(f"### {q_now}")

# --- TAB 2: TULIS ---
with tab2:
    st.subheader("Catat Perenunganmu")
    # Tinggi area teks diperbesar agar nyaman membaca ayat panjang
    st.text_area("Ayat / Firman:", key="in_at", height=180, placeholder="silahkan input manual 📝") 
    st.text_area("Catatan Pribadi:", key="in_nt", height=200, placeholder="Apa pesan Tuhan untukmu hari ini?")
    
    st.button("💾 Simpan Permanen", on_click=handle_save)

# --- TAB 3: RIWAYAT ---
with tab3:
    st.subheader(f"Daftar Riwayat: {current_user}")
    try:
        # Filter berdasarkan email (author)
        res = supabase.table("database_renungan").select("*").eq("author", current_user).order("created_at", desc=True).execute()
        
        if not res.data:
            st.write("Belum ada riwayat tersimpan untuk email ini.")
        else:
            for item in res.data:
                tgl = item['created_at'][:10]
                ayat_preview = item['ayat'][:40]
                with st.expander(f"📅 {tgl} | {ayat_preview}..."):
                    st.write(f"**Ayat:**\n{item['ayat']}")
                    st.divider()
                    st.write(f"**Catatan:**\n{item['notes']}")
                    
                    if st.button("🗑️ Hapus Catatan", key=f"del_{item['id']}"):
                        supabase.table("database_renungan").delete().eq("id", item['id']).execute()
                        st.rerun()
    except Exception as e:
        st.error(f"Gagal memuat data dari database: {e}")
