import sys
import types
import streamlit as st

# --- 1. THE ULTIMATE STABILITY PATCH ---
if sys.version_info >= (3, 12):
    # Mock 'distutils'
    if 'distutils' not in sys.modules:
        m_dist = types.ModuleType('distutils')
        m_dist.version = types.ModuleType('version')
        class LooseVersion:
            def __init__(self, v): self.v = v
            def __ge__(self, other): return True
        m_dist.version.LooseVersion = LooseVersion
        sys.modules['distutils'] = m_dist
        sys.modules['distutils.version'] = m_dist.version

    # Mock 'aifc'
    m_aifc = types.ModuleType('aifc')
    m_aifc.open = lambda *args, **kwargs: None
    m_aifc.Error = Exception
    sys.modules['aifc'] = m_aifc
    
    # Mock 'audioop'
    m_audioop = types.ModuleType('audioop')
    m_audioop.add = lambda *args: b''
    sys.modules['audioop'] = m_audioop

import openai
import speech_recognition as sr
from gtts import gTTS
import tempfile
import os

# --- 2. CONFIG ---
st.set_page_config(
    page_title="FLUENT.AI 3000",
    page_icon="🌌",
    layout="wide"
)

# --- 3. FUTURE-UI CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        color: white;
        font-family: 'Rajdhani', sans-serif;
    }
    
    /* GLASS CARDS */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    /* BUBBLES */
    .bot-bubble {
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        padding: 15px; border-radius: 0 20px 20px 20px; margin-bottom: 10px; width: fit-content; max-width: 80%;
    }
    .user-bubble {
        background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
        color: #000; font-weight: bold;
        padding: 15px; border-radius: 20px 0 20px 20px; margin-bottom: 10px; margin-left: auto; width: fit-content; max-width: 80%;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. LOGIC ---
with st.sidebar:
    st.markdown("## ⚙️ SYSTEM CORE")
    api_key = st.text_input("🔑 API KEY", type="password")
    if api_key: openai.api_key = api_key
    mode = st.radio("MODE", ["🗣️ NEURAL CHAT", "🧠 MEMORY UPLINK"])

def speak_text(text):
    if text:
        try:
            tts = gTTS(text=text, lang='en')
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                tts.save(fp.name)
                st.audio(fp.name, format="audio/mp3")
        except: pass

if mode == "🗣️ NEURAL CHAT":
    st.markdown("<h1>🗣️ NEURAL INTERFACE</h1>", unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": "You are a futuristic AI tutor named Nexus."}]

    # Chat History
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            style = "user-bubble" if msg["role"] == "user" else "bot-bubble"
            st.markdown(f'<div class="{style}">{msg["content"]}</div>', unsafe_allow_html=True)

    # --- FIXED: INPUT AREA ---
    # We moved the button OUT of columns to prevent the crash
    st.markdown("---")
    
    # Voice Button (Now safe)
    if st.button("🎙️ ACTIVATE VOX SENSOR (Click to Speak)"):
        st.info("⚠️ Listening...")
        try:
            r = sr.Recognizer()
            with sr.Microphone() as source:
                audio = r.listen(source, timeout=3)
                text = r.recognize_google(audio)
                # Append directly to chat
                st.session_state.messages.append({"role": "user", "content": text})
                st.rerun()
        except:
            st.error("❌ SENSOR OFFLINE. USE TEXT BELOW.")

    # Main Chat Input (Must be at root level)
    user_input = st.chat_input("Transmit data packet...")

    if user_input:
        if not api_key:
            st.warning("⚠️ ENTER API KEY IN SIDEBAR")
        else:
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.rerun()

    # AI Response
    if st.session_state.messages[-1]["role"] == "user" and api_key:
        with st.spinner("⚡ PROCESSING..."):
            try:
                response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
                ai_msg = response.choices[0].message['content']
                st.session_state.messages.append({"role": "assistant", "content": ai_msg})
                st.rerun()
            except Exception as e:
                st.error(f"ERROR: {e}")

elif mode == "🧠 MEMORY UPLINK":
    st.markdown("<h1>🧠 KNOWLEDGE UPLINK</h1>", unsafe_allow_html=True)
    words = [
        {"word": "ETHEREAL", "meaning": "Extremely delicate and light."},
        {"word": "NEBULOUS", "meaning": "Hazy, undefined, or vague."},
        {"word": "LUMINESCENT", "meaning": "Emitting light not caused by heat."}
    ]
    for w in words:
        st.markdown(f"""
        <div class="glass-card">
            <h2 style="color:#38ef7d; margin:0">{w['word']}</h2>
            <p>{w['meaning']}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"🔊 ACTIVATE: {w['word']}", key=w['word']):
            speak_text(w['word'])
