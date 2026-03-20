import streamlit as st
from supabase import create_client, Client
import random
import re

# --- 1. KONEKSI SUPABASE ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 2. FUNGSI HELPER ---
def safe_rerun():
    if hasattr(st, "rerun"): st.rerun()
    else: st.experimental_rerun()

@st.cache_data
def load_ayat():
    try:
        with open("ayat.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except:
        return ["Bersyukurlah dalam segala hal.", "Tuhan adalah Gembalaku."]

quotes_list = load_ayat()

# --- 3. LOGIN SESSION ---
if 'user_email' not in st.session_state:
    st.title("🔐 Akses Diary Pribadi")
    email_input = st.text_input("Masukkan Email Anda:", placeholder="contoh: budi@email.com")
    if st.button("Masuk"):
        if email_input and re.match(r"[^@]+@[^@]+\.[^@]+", email_input):
            st.session_state.user_email = email_input.strip().lower()
            safe_rerun()
        else:
            st.error("⚠️ Email tidak valid.")
    st.stop()

current_user = st.session_state.user_email

# --- 4. TAMPILAN UTAMA ---
st.sidebar.write(f"Logged in: **{current_user}**")
if st.sidebar.button("Logout"):
    del st.session_state.user_email
    safe_rerun()

st.title("🙏 Diary Renungan Digital")
tab1, tab2, tab3 = st.tabs(["✨ Acak Ayat", "📝 Tulis Log", "📜 Riwayat Saya"])

# --- TAB 1: ACAK AYAT (FIXED) ---
with tab1:
    st.subheader("Inspirasi Hari Ini")
    if st.button("🔄 Dapatkan Ayat Baru"):
        # Pilih ayat acak dan simpan ke session state
        st.session_state.current_quote = random.choice(quotes_list)
        # Paksa update ke input box di Tab 2
        st.session_state["in_at"] = st.session_state.current_quote
    
    q_display = st.session_state.get('current_quote', "Klik tombol di atas.")
    st.info(f"### {q_display}")

# --- TAB 2: TULIS ---
with tab2:
    # Widget input dengan key yang terhubung ke session state
    at = st.text_area("Ayat:", key="in_at", height=100)
    nt = st.text_area("Catatan:", key="in_nt", height=200)
    
    if st.button("💾 Simpan Permanen"):
        if at and nt:
            try:
                supabase.table("database_renungan").insert({
                    "ayat": at, 
                    "notes": nt,
                    "author": current_user 
                }).execute()
                
                # Reset Form setelah simpan
                st.session_state["in_at"] = ""
                st.session_state["in_nt"] = ""
                st.session_state.current_quote = ""
                
                st.success("✅ Tersimpan di database pribadi Anda!")
                safe_rerun()
            except Exception as e:
                st.error(f"Gagal Simpan: {e}")

# --- TAB 3: RIWAYAT ---
with tab3:
    st.subheader(f"Catatan {current_user}")
    try:
        res = supabase.table("database_renungan").select("*").eq("author", current_user).order("created_at", desc=True).execute()
        
        if not res.data:
            st.write("Belum ada riwayat.")
        else:
            for item in res.data:
                with st.expander(f"📅 {item['created_at'][:10]} | {item['ayat'][:20]}..."):
                    st.write(f"**Ayat:** {item['ayat']}")
                    st.write(f"**Notes:** {item['notes']}")
                    if st.button("🗑️ Hapus", key=f"del_{item['id']}"):
                        supabase.table("database_renungan").delete().eq("id", item['id']).execute()
                        safe_rerun()
    except Exception as e:
        st.error(f"Gagal memuat data: {e}")
