import streamlit as st
import sqlite3
import random

# --- KONFIGURASI DATABASE ---
conn = sqlite3.connect('spiritual_app.db', check_same_thread=False)
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ayat TEXT,
        notes TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

# --- DATA AYAT ---
quotes_list = [
    "Akulah jalan dan kebenaran dan hidup.",
    "Janganlah gelisah hatimu; percayalah kepada Allah.",
    "Kasihilah sesamamu manusia seperti dirimu sendiri.",
    "Damai sejahtera-Ku Kuberikan kepadamu.",
    "Marilah kepada-Ku, semua yang letih lesu dan berbeban berat.",
]

# --- LOGIKA STATE ---
if 'current_quote' not in st.session_state:
    st.session_state.current_quote = ""

# Fungsi untuk reset input tab 2
def reset_tab2():
    st.session_state.current_quote = ""
    # Kita gunakan key untuk memaksa text_area reset
    st.session_state.notes_input_key = ""

st.title("🙏 Renungan & Log Pribadi")

tab1, tab2, tab3 = st.tabs(["✨ Acak Ayat", "📝 Catatan Baru", "📜 Riwayat Log"])

# --- TAB 1: RANDOM AYAT ---
with tab1:
    st.subheader("Inspirasi Untukmu")
    if st.session_state.current_quote:
        st.info(f"### {st.session_state.current_quote}")
    else:
        st.write("Klik tombol di bawah untuk mendapatkan ayat.")
    
    if st.button("🔄 Acak Ayat Baru"):
        st.session_state.current_quote = random.choice(quotes_list)
        st.rerun()

# --- TAB 2: INPUT & NOTES ---
with tab2:
    st.subheader("Buat Catatan")
    
    # Input Ayat (otomatis terisi dari Tab 1)
    ayat_input = st.text_area("Ayat:", value=st.session_state.current_quote, height=100)
    
    # Input Notes dengan key agar bisa direset
    notes_input = st.text_area("Catatan/Notes:", placeholder="Tulis perenunganmu...", key="notes_area")
    
    if st.button("💾 Simpan Permanen"):
        if ayat_input.strip() and notes_input.strip():
            c.execute('INSERT INTO logs (ayat, notes) VALUES (?, ?)', (ayat_input, notes_input))
            conn.commit()
            
            # Reset state setelah simpan
            st.session_state.current_quote = ""
            # Cara praktis mengosongkan text_area adalah dengan rerun setelah mengubah state
            st.success("✅ Catatan disimpan! Form telah dikosongkan.")
            st.rerun() 
        else:
            st.error("Gagal simpan! Mohon isi semua bidang.")

# --- TAB 3: LOG AKTIVITAS DENGAN FITUR HAPUS ---
with tab3:
    st.subheader("Riwayat Log")
    
    # Ambil data terbaru
    c.execute('SELECT id, ayat, notes, timestamp FROM logs ORDER BY id DESC LIMIT 500')
    data_log = c.fetchall()
    
    if not data_log:
        st.write("Belum ada data.")
    else:
        for item in data_log:
            log_id, log_ayat, log_notes, log_time = item
            
            # Membuat expander untuk setiap log
            with st.expander(f"📅 {log_time} | {log_ayat[:30]}..."):
                st.write(f"**Ayat:** {log_ayat}")
                st.write(f"**Catatan:** {log_notes}")
                
                # Tombol Hapus dengan kunci unik (log_id)
                if st.button(f"🗑️ Hapus Log ini", key=f"del_{log_id}"):
                    c.execute('DELETE FROM logs WHERE id = ?', (log_id,))
                    conn.commit()
                    st.warning(f"Log berhasil dihapus!")
                    st.rerun() # Refresh tampilan setelah hapus
