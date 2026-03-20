import streamlit as st
from supabase import create_client, Client
import random

# --- KONEKSI ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- LOAD AYAT ---
with open("ayat.txt", "r", encoding="utf-8") as f:
    quotes = [line.strip() for line in f.readlines() if line.strip()]

st.title("🙏 Diary Renungan Digital")
tab1, tab2, tab3 = st.tabs(["✨ Acak", "📝 Tulis", "📜 Riwayat"])

with tab1:
    if st.button("🔄 Acak Ayat"):
        st.session_state.current_quote = random.choice(quotes)
    st.info(f"### {st.session_state.get('current_quote', 'Klik tombol di atas')}")

with tab2:
    at = st.text_area("Ayat:", value=st.session_state.get('current_quote', ""), key="at")
    nt = st.text_area("Catatan:", key="nt")
    if st.button("💾 Simpan"):
        if at and nt:
            # Ganti "renungan_log" dengan nama tabel yang Anda buat tadi
            supabase.table("database_renungan").insert({"ayat": at, "notes": nt}).execute()
            st.session_state.current_quote = ""
            st.success("Tersimpan!")
            st.rerun()

with tab3:
    res = supabase.table("database_renungan").select("*").order("created_at", desc=True).execute()
    for item in res.data:
        with st.expander(f"📅 {item['created_at'][:10]}"):
            st.write(f"**Ayat:** {item['ayat']}")
            st.write(f"**Notes:** {item['notes']}")
