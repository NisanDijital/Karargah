import streamlit as st
import requests
import os
import time
from requests.exceptions import RequestException

# --- Sayfa konfigürasyonu ---
st.set_page_config(page_title="AI Dashboard", page_icon="🤖", layout="wide")
st.title("🔐 Şifre Korumalı AI Dashboard")

# --- Ayarlar / Secrets ---
DASHBOARD_PASS = st.secrets.get("DASHBOARD_PASS") if "DASHBOARD_PASS" in st.secrets else os.getenv("DASHBOARD_PASS")
OPENAI_KEY = st.secrets.get("OPENAI_API_KEY") if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")
GEMINI_KEY = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.getenv("GEMINI_API_KEY")

# --- Basit kimlik doğrulaması (session bazlı) ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    password = st.sidebar.text_input("Şifre", type="password")
    if password:
        if DASHBOARD_PASS and password == DASHBOARD_PASS:
            st.session_state.authenticated = True
            st.experimental_rerun()
        else:
            st.sidebar.error("Yetkisiz giriş. Lütfen doğru şifreyi gir.")
            st.stop()
    else:
        st.sidebar.info("Lütfen giriş yapmak için şifrenizi girin.")
        st.stop()

# --- Sidebar ayarları ---
debug_mode = st.sidebar.checkbox("Debug: Raw JSON göster", value=False)
openai_model = st.sidebar.text_input("OpenAI model (opsiyonel)", value="gpt-4o-mini")
openai_timeout = st.sidebar.number_input("OpenAI timeout (s)", value=15, min_value=1)
gemini_timeout = st.sidebar.number_input("Gemini timeout (s)", value=15, min_value=1)

# --- Kullanıcı girişi ---
user_input = st.text_area("Komut gir:", height=120)
submit = st.button("Gönder")

# --- HTTP session (connection reuse) ---
session = requests.Session()
DEFAULT_HEADERS = {"Content-Type": "application/json"}

def call_openai(prompt: str, api_key: str, model: str, timeout: int = 15):
    if not api_key:
        return {"error": "OPENAI_API_KEY bulunamadı."}
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", **DEFAULT_HEADERS}
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        resp = session.post(url, headers=headers, json=payload, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        # Güvenli parse
        answer = None
        try:
            answer = data.get("choices", [{}])[0].get("message", {}).get("content")
        except Exception:
            answer = None
        return {"raw": data, "answer": answer}
    except RequestException as e:
        return {"error": f"OpenAI request error: {str(e)}", "status_code": getattr(e.response, "status_code", None)}
    except ValueError:
        return {"error": "OpenAI yanıtı JSON olarak çözülemedi."}

def call_gemini(prompt: str, api_key: str, timeout: int = 15):
    if not api_key:
        return {"error": "GEMINI_API_KEY bulunamadı."}
    # Bu endpoint ve payload prod için doğrulanmalı. Google API'leri zaman içinde değişebilir.
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        resp = session.post(url, json=payload, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        # Güvenli parse (fallback'li)
        answer = None
        try:
            answer = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text")
        except Exception:
            answer = None
        return {"raw": data, "answer": answer}
    except RequestException as e:
        return {"error": f"Gemini request error: {str(e)}", "status_code": getattr(e.response, "status_code", None)}
    except ValueError:
        return {"error": "Gemini yanıtı JSON olarak çözülemedi."}

if submit and user_input:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("OpenAI Cevabı")
        if not OPENAI_KEY:
            st.warning("OPENAI_API_KEY bulunamadı.")
        else:
            with st.spinner("OpenAI'den cevap alınıyor..."):
                start = time.time()
                res = call_openai(user_input, OPENAI_KEY, openai_model, timeout=int(openai_timeout))
                elapsed = time.time() - start
            if "error" in res:
                st.error(res["error"])
            else:
                ans = res.get("answer") or "Cevap üretilemedi veya beklenmeyen bir yanıt döndü."
                st.success(ans)
                st.caption(f"Yanıt süresi: {elapsed:.2f}s")
                if debug_mode:
                    st.write("Raw OpenAI yanıtı:")
                    st.json(res["raw"])

    with col2:
        st.subheader("Gemini Cevabı")
        if not GEMINI_KEY:
            st.warning("GEMINI_API_KEY bulunamadı.")
        else:
            with st.spinner("Gemini'den cevap alınıyor..."):
                start = time.time()
                res2 = call_gemini(user_input, GEMINI_KEY, timeout=int(gemini_timeout))
                elapsed = time.time() - start
            if "error" in res2:
                st.error(res2["error"])
            else:
                ans2 = res2.get("answer") or "Cevap üretilemedi veya beklenmeyen bir yanıt döndü."
                st.success(ans2)
                st.caption(f"Yanıt süresi: {elapsed:.2f}s")
                if debug_mode:
                    st.write("Raw Gemini yanıtı:")
                    st.json(res2["raw"])
