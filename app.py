import streamlit as st
import requests
import os

st.set_page_config(page_title="AI Dashboard", page_icon="🤖", layout="wide")
st.title("🔐 Şifre Korumalı AI Dashboard")

# --- Şifre kontrolü ---
password = st.sidebar.text_input("Şifre", type="password")
if password != os.getenv("DASHBOARD_PASS"):
    st.error("Yetkisiz giriş. Lütfen doğru şifreyi gir.")
    st.stop()

# --- Kullanıcı girişi ---
user_input = st.text_input("Komut gir:")

# --- API anahtarları ---
openai_key = os.getenv("OPENAI_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")

if user_input:
    col1, col2 = st.columns(2)

    # --- OpenAI cevabı ---
    with col1:
        st.subheader("OpenAI Cevabı")
        if openai_key:
            headers = {"Authorization": f"Bearer {openai_key}"}
            data = {
                "model": "gpt-4o-mini",  # gerekirse "gpt-3.5-turbo" deneyebilirsin
                "messages": [{"role": "user", "content": user_input}]
            }
            r = requests.post("https://api.openai.com/v1/chat/completions",
                              headers=headers, json=data)
            if r.status_code == 200:
                result = r.json()
                answer = result["choices"][0]["message"]["content"]
                st.success(answer)
                st.json(result)  # debug için
            else:
                st.error(f"OpenAI hata: {r.text}")
        else:
            st.warning("OPENAI_API_KEY bulunamadı.")

    # --- Gemini cevabı ---
    with col2:
        st.subheader("Gemini Cevabı")
        if gemini_key:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            data = {
                "contents": [{"parts": [{"text": user_input}]}]
            }
            r = requests.post(url, json=data)
            if r.status_code == 200:
                result = r.json()
                answer = result["candidates"][0]["content"]["parts"][0]["text"]
                st.success(answer)
                st.json(result)  # debug için
            else:
                st.error(f"Gemini hata: {r.text}")
        else:
            st.warning("GEMINI_API_KEY bulunamadı.")
