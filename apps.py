import streamlit as st
from supabase import create_client, Client
import random
import re # Untuk validasi email

# --- 1. KONFIGURASI & KONEKSI ---
st.set_page_config(page_title="My Spiritual Diary", page_icon="📖")

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 2. FUNGSI RERUN ---
def safe_rerun():
    if hasattr(st, "rerun"): st.rerun()
    else: st.experimental_rerun()

# --- 3. LOGIN DENGAN EMAIL ---
if 'user_email' not in st.session_state:
    st.title("🔐 Akses Diary Pribadi")
    st.markdown("Silakan masukkan email Anda untuk mengakses catatan renungan pribadi.")
    
    # Input Email
    email_input = st.text_input("Masukkan Email Anda:", placeholder="contoh: budi@email.com")
    
    if st.button("Masuk"):
        # Validasi format email sederhana
        if email_input and re.match(r"[^@]+@[^@]+\.[^@]+", email_input):
            # Simpan sebagai huruf kecil agar tidak case-sensitive
            st.session_state.user_email = email_input.strip().lower()
            st.success(f"Selamat datang, {st.session_state.user_email}!")
            safe_rerun()
        else:
            st.error("⚠️ Mohon masukkan format email yang valid (harus ada '@' dan '.')")
    
    st.info("💡 Catatan: Email ini digunakan sebagai kunci untuk memisahkan database Anda dengan orang lain.")
    st.stop() 

# --- VARIABEL USER AKTIF ---
current_user = st.session_state.user_email

# --- 4. SIDEBAR LOGOUT ---
st.sidebar.title("👤 Profil")
st.sidebar.write(f"Login sebagai:\n**{current_user}**")
if st.sidebar.button("Keluar (Logout)"):
    del st.session_state.user_email
    safe_rerun()

# --- 5. UI UTAMA ---
st.title("🙏 Diary Renungan Digital")
tab1, tab2, tab3 = st.tabs(["✨ Acak Ayat", "📝 Tulis Log", "📜 Riwayat Saya"])

# --- TAB 1: ACAK ---
with tab1:
    # (Kode load_ayat tetap sama seperti sebelumnya)
    if st.button("🔄 Dapatkan Ayat Baru"):
        # Asumsi quotes_list sudah didefinisikan di atas atau di load
        pass 

# --- TAB 2: TULIS ---
with tab2:
    at = st.text_area("Ayat:", key="in_at")
    nt = st.text_area("Catatan:", key="in_nt")
    
    if st.button("💾 Simpan Permanen"):
        if at and nt:
            # SIMPAN KE SUPABASE DENGAN EMAIL SEBAGAI AUTHOR
            supabase.table("database_renungan").insert({
                "ayat": at, 
                "notes": nt,
                "author": current_user 
            }).execute()
            st.success("Tersimpan di database pribadi Anda!")
            safe_rerun()

# --- TAB 3: RIWAYAT (DIFILTER BERDASARKAN EMAIL) ---
with tab3:
    st.subheader(f"Riwayat untuk {current_user}")
    try:
        # Hanya ambil data yang 'author'-nya adalah email user saat ini
        res = supabase.table("database_renungan")\
            .select("*")\
            .eq("author", current_user)\
            .order("created_at", desc=True)\
            .execute()
        
        if not res.data:
            st.write("Belum ada riwayat untuk email ini.")
        else:
            for item in res.data:
                with st.expander(f"📅 {item['created_at'][:10]} | {item['ayat'][:20]}..."):
                    st.write(f"**Ayat:** {item['ayat']}")
                    st.write(f"**Notes:** {item['notes']}")
                    if st.button("🗑️ Hapus", key=f"del_{item['id']}"):
                        supabase.table("database_renungan").delete().eq("id", item['id']).execute()
                        safe_rerun()
    except Exception as e:
        st.error(f"Error: {e}")
