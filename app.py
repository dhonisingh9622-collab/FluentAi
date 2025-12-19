import sys
import types
import streamlit as st

# --- 1. THE ULTIMATE STABILITY PATCH (Keeps the app running on Cloud) ---
if sys.version_info >= (3, 12):
    # Mock 'distutils' for SpeechRecognition
    if 'distutils' not in sys.modules:
        m_dist = types.ModuleType('distutils')
        m_dist.version = types.ModuleType('version')
        class LooseVersion:
            def __init__(self, v): self.v = v
            def __ge__(self, other): return True
        m_dist.version.LooseVersion = LooseVersion
        sys.modules['distutils'] = m_dist
        sys.modules['distutils.version'] = m_dist.version

    # Mock 'aifc' and 'audioop' for Audio
    m_aifc = types.ModuleType('aifc')
    m_aifc.open = lambda *args, **kwargs: None
    m_aifc.Error = Exception
    sys.modules['aifc'] = m_aifc
    
    m_audioop = types.ModuleType('audioop')
    m_audioop.add = lambda *args: b''
    sys.modules['audioop'] = m_audioop
# -----------------------------------------------------------------------

import openai
import speech_recognition as sr
from gtts import gTTS
import tempfile
import os
import random

# --- 2. CONFIG (MUST BE FIRST) ---
st.set_page_config(
    page_title="FLUENT.AI 3000",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 3. FUTURE-UI DESIGN ENGINE (CSS) ---
st.markdown("""
<style>
    /* IMPORT FUTURISTIC FONT */
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&display=swap');

    /* GLOBAL THEME */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        color: #ffffff;
        font-family: 'Rajdhani', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Rajdhani', sans-serif;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #00d2ff;
        text-shadow: 0 0 10px rgba(0, 210, 255, 0.7);
    }

    /* GLASSMORPHISM CARDS */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    }

    /* CHAT BUBBLES */
    .bot-bubble {
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 0px 20px 20px 20px;
        margin-bottom: 10px;
        box-shadow: 0 0 15px rgba(0, 210, 255, 0.4);
        width: fit-content;
        max-width: 80%;
        animation: glow 2s infinite alternate;
    }

    .user-bubble {
        background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
        color: #0f0c29;
        font-weight: bold;
        padding: 15px 20px;
        border-radius: 20px 0px 20px 20px;
        margin-bottom: 10px;
        margin-left: auto;
        width: fit-content;
        max-width: 80%;
        box-shadow: 0 0 15px rgba(56, 239, 125, 0.4);
    }

    /* SIDEBAR STYLING */
    section[data-testid="stSidebar"] {
        background-color: #0a0a1a;
        border-right: 1px solid #00d2ff;
    }

    /* BUTTON STYLING */
    .stButton>button {
        background: transparent;
        border: 2px solid #00d2ff;
        color: #00d2ff;
        border-radius: 5px;
        text-transform: uppercase;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: #00d2ff;
        color: #000;
        box-shadow: 0 0 20px #00d2ff;
    }
    
    /* INPUT BOX STYLING */
    .stTextInput>div>div>input {
        background-color: rgba(255,255,255,0.1);
        color: white;
        border: 1px solid #3a7bd5;
    }

</style>
""", unsafe_allow_html=True)

# --- 4. APP LOGIC ---

# Sidebar Settings
with st.sidebar:
    st.markdown("## ⚙️ SYSTEM CORE")
    st.markdown("---")
    api_key = st.text_input("🔑 ACCESS TOKEN (API Key)", type="password")
    if api_key: openai.api_key = api_key
    
    st.markdown("### 💠 SELECT MODULE")
    mode = st.radio("Navigation", ["🗣️ NEURAL CHAT", "🧠 MEMORY UPLINK (Vocab)"], label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: gray; font-size: 0.8em;'>FLUENT.AI v3.0 // ONLINE</div>", unsafe_allow_html=True)

# Helper: Speak
def speak_text(text):
    if text:
        try:
            tts = gTTS(text=text, lang='en')
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                tts.save(fp.name)
                st.audio(fp.name, format="audio/mp3")
        except Exception:
            pass # Silent fail to keep UI clean

# --- MODE A: NEURAL CHAT ---
if mode == "🗣️ NEURAL CHAT":
    st.markdown("<h1>🗣️ NEURAL LINGUISTIC INTERFACE</h1>", unsafe_allow_html=True)
    st.markdown("<div class='glass-card'>Initialize conversation sequence. I will analyze and correct your syntax in real-time.</div>", unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": "You are a futuristic AI English tutor from the year 3000. Your name is 'Nexus'. You are helpful, kind, and you correct grammar mistakes gently but clearly."}]

    # Chat Container
    with st.container():
        for msg in st.session_state.messages:
            if msg["role"] != "system":
                style = "user-bubble" if msg["role"] == "user" else "bot-bubble"
                st.markdown(f'<div class="{style}">{msg["content"]}</div>', unsafe_allow_html=True)
                if msg["role"] == "assistant":
                    st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)

    # Input Zone
    st.markdown("---")
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.chat_input("Transmit data packet (Type here)...")
    
    with col2:
        if st.button("🎙️ VOX INPUT"):
            st.info("⚠️ Cloud Voice Sensor Active...")
            try:
                r = sr.Recognizer()
                with sr.Microphone() as source:
                    audio = r.listen(source, timeout=3)
                    text = r.recognize_google(audio)
                    user_input = text # Override input
            except:
                st.error("❌ AUDIO SENSOR OFFLINE. USE TEXT INPUT.")

    # Processing Logic
    if user_input:
        if not api_key:
            st.warning("⚠️ ACCESS DENIED: PLEASE ENTER API KEY IN SIDEBAR")
        else:
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.rerun()

    # AI Response Generation
    if st.session_state.messages[-1]["role"] == "user" and api_key:
        with st.spinner("⚡ PROCESSING NEURAL NET..."):
            try:
                response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
                ai_msg = response.choices[0].message['content']
                st.session_state.messages.append({"role": "assistant", "content": ai_msg})
                
                # Render latest response immediately
                st.markdown(f'<div class="bot-bubble">{ai_msg}</div>', unsafe_allow_html=True)
                speak_text(ai_msg)
            except Exception as e:
                st.error(f"SYSTEM ERROR: {e}")

# --- MODE B: VOCABULARY ---
elif mode == "🧠 MEMORY UPLINK (Vocab)":
    st.markdown("<h1>🧠 KNOWLEDGE UPLINK</h1>", unsafe_allow_html=True)
    st.markdown("Downloading daily linguistic enhancements...", unsafe_allow_html=True)
    
    # Futuristic Vocab List
    words = [
        {"word": "ETHEREAL", "meaning": "Extremely delicate and light in a way that seems too perfect for this world."},
        {"word": "NEBULOUS", "meaning": "In the form of a cloud or haze; hazy."},
        {"word": "LUMINESCENT", "meaning": "Emitting light not caused by heat."},
        {"word": "QUANTUM", "meaning": "A discrete quantity of energy proportional in magnitude to the frequency of the radiation it represents."},
        {"word": "SYNAPSE", "meaning": "A junction between two nerve cells, consisting of a minute gap across which impulses pass."}
    ]

    col1, col2 = st.columns(2)
    for i, w in enumerate(words):
        with col1 if i % 2 == 0 else col2:
            st.markdown(f"""
            <div class="glass-card">
                <h2 style="color: #38ef7d; margin:0;">{w['word']}</h2>
                <p style="color: #ccc;">{w['meaning']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"🔊 ACTIVATE: {w['word']}", key=w['word']):
                speak_text(w['word'])
