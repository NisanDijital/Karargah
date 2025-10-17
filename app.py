# app.py
import streamlit as st

# Sayfa ayarları
st.set_page_config(page_title="AI Dashboard", page_icon="🤖", layout="wide")

# Başlık
st.title("🤖 AI Destekli Dashboard")

# Sidebar
with st.sidebar:
    st.header("Kontroller")
    st.write("Buraya filtreler, parametreler eklenebilir.")

# Ana alan
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Panel Alanı")
    st.info("Burada grafikler, tablolar veya AI çıktıları görünecek.")

with col2:
    st.subheader("AI / API Çıktısı")
    st.write("Buraya AI fonksiyonunu veya API entegrasyonunu ekleyeceksin.")
    # Örnek placeholder
    user_input = st.text_input("Komut gir:")
    if user_input:
        st.success(f"AI cevabı burada görünecek → '{user_input}' işlendi.")
        # Buraya kendi modelini veya API çağrını koyabilirsin
        # örn: response = call_my_api(user_input)
