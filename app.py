import sys
import types
import streamlit as st
import random
from datetime import datetime

# --- 1. STABILITY PATCHES (Required for Python 3.12+) ---
if sys.version_info >= (3, 12):
    if 'distutils' not in sys.modules:
        m_dist = types.ModuleType('distutils')
        m_dist.version = types.ModuleType('version')
        class LooseVersion:
            def __init__(self, v): self.v = v
            def __ge__(self, other): return True
        m_dist.version.LooseVersion = LooseVersion
        sys.modules['distutils'] = m_dist
        sys.modules['distutils.version'] = m_dist.version

    m_aifc = types.ModuleType('aifc')
    m_aifc.open = lambda *args, **kwargs: None
    m_aifc.Error = Exception
    sys.modules['aifc'] = m_aifc
    
    m_audioop = types.ModuleType('audioop')
    m_audioop.add = lambda *args: b''
    sys.modules['audioop'] = m_audioop

# --- IMPORTS ---
import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
import tempfile
import os

# --- 2. CONFIG ---
st.set_page_config(
    page_title="FLUENT.AI 3000",
    page_icon="💎",
    layout="wide"
)

# --- 3. FUTURISTIC CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        color: white;
        font-family: 'Rajdhani', sans-serif;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        text-align: center;
    }
    .glass-card:hover { border-color: #00d2ff; }
    .bot-bubble { background: rgba(0, 210, 255, 0.1); border: 1px solid #00d2ff; padding: 15px; border-radius: 0 20px 20px 20px; margin-bottom: 10px; width: fit-content; max-width: 80%; }
    .user-bubble { background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%); color: #000; font-weight: bold; padding: 15px; border-radius: 20px 0 20px 20px; margin-bottom: 10px; margin-left: auto; width: fit-content; max-width: 80%; }
    .visual-icon { font-size: 80px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 4. LOGIC & DATA ---
with st.sidebar:
    st.markdown("## 💎 SYSTEM CORE")
    
    # DEBUG: Show the library version to confirm the fix worked
    st.caption(f"System Version: {genai.__version__}")
    
    api_key = st.text_input("🔑 GOOGLE API KEY", type="password")
    if api_key: 
        genai.configure(api_key=api_key)
    
    st.markdown("### 💠 MODULE SELECTOR")
    mode = st.radio("Navigation", ["🗣️ CHAT PRACTICE", "📚 DAILY VOCAB", "👁️ VISUAL LEARNING"], label_visibility="collapsed")
    st.markdown("---")
    st.info(f"📅 Date: {datetime.now().strftime('%B %d, %Y')}")

def speak_text(text):
    if text:
        try:
            tts = gTTS(text=text, lang='en')
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                tts.save(fp.name)
                st.audio(fp.name, format="audio/mp3")
        except: pass

# --- SEED FOR DAILY CONTENT ---
today_seed = int(datetime.now().strftime("%Y%m%d"))
random.seed(today_seed)

# --- MODE A: CHAT ---
if mode == "🗣️ CHAT PRACTICE":
    st.markdown("<h1>🗣️ NEURAL INTERFACE</h1>", unsafe_allow_html=True)
    if "messages" not in st.session_state: st.session_state.messages = []

    for msg in st.session_state.messages:
        style = "user-bubble" if msg["role"] == "user" else "bot-bubble"
        st.markdown(f'<div class="{style}">{msg["content"]}</div>', unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🎙️ ACTIVATE VOX SENSOR"):
        st.info("⚠️ Listening...")
        try:
            r = sr.Recognizer()
            with sr.Microphone() as source:
                audio = r.listen(source, timeout=3)
                text = r.recognize_google(audio)
                st.session_state.messages.append({"role": "user", "content": text})
                st.rerun()
        except: st.error("❌ SENSOR OFFLINE. TYPE BELOW.")

    user_input = st.chat_input("Transmit data packet...")
    if user_input:
        if not api_key: st.warning("⚠️ ENTER GOOGLE API KEY IN SIDEBAR")
        else:
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.rerun()

    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user" and api_key:
        with st.spinner("💎 PROCESSING..."):
            try:
                # Using the most stable current model
                model = genai.GenerativeModel('gemini-1.5-flash')
                chat = model.start_chat(history=[])
                response = chat.send_message(f"Correct any grammar mistakes, then reply naturally to: {st.session_state.messages[-1]['content']}")
                st.session_state.messages.append({"role": "model", "content": response.text})
                st.rerun()
            except Exception as e: 
                st.error(f"ERROR: {e}")
                st.error("Tip: Check if your API Key is correct in the sidebar!")

# --- MODE B: DAILY VOCAB ---
elif mode == "📚 DAILY VOCAB":
    st.markdown(f"<h1>📚 VOCAB FOR {datetime.now().strftime('%B %d')}</h1>", unsafe_allow_html=True)
    
    full_vocab_db = [
        {"word": "Articulate", "meaning": "To express an idea clearly.", "ex": "She can articulate complex ideas."},
        {"word": "Mitigate", "meaning": "To make less severe.", "ex": "We must mitigate the risks."},
        {"word": "Lucrative", "meaning": "Producing profit.", "ex": "A lucrative business."},
        {"word": "Pragmatic", "meaning": "Dealing with things realistically.", "ex": "A pragmatic approach."},
        {"word": "Collaborate", "meaning": "To work together.", "ex": "They collaborated on the project."},
        {"word": "Resilient", "meaning": "Able to recover quickly.", "ex": "She is resilient."},
        {"word": "Ambiguous", "meaning": "Open to more than one interpretation.", "ex": "The ending was ambiguous."},
        {"word": "Candid", "meaning": "Truthful and straightforward.", "ex": "A candid interview."},
        {"word": "Diligent", "meaning": "Having or showing care in one's work.", "ex": "A diligent student."},
        {"word": "Empathy", "meaning": "The ability to understand feelings of others.", "ex": "He showed great empathy."},
        {"word": "Innovative", "meaning": "Featuring new methods.", "ex": "An innovative design."},
        {"word": "Meticulous", "meaning": "Showing great attention to detail.", "ex": "He was meticulous."},
        {"word": "Nuance", "meaning": "A subtle difference in meaning.", "ex": "The nuances of the language."},
        {"word": "Obsolete", "meaning": "No longer produced or used.", "ex": "The machine is obsolete."},
        {"word": "Plausible", "meaning": "Seeming reasonable or probable.", "ex": "A plausible explanation."}
    ]
    
    todays_words = random.sample(full_vocab_db, 4)
    col1, col2 = st.columns(2)
    for i, w in enumerate(todays_words):
        with col1 if i % 2 == 0 else col2:
            st.markdown(f"""<div class="glass-card"><h2 style="color:#00d2ff; margin:0">{w['word']}</h2><p><strong>Meaning:</strong> {w['meaning']}</p><p style="font-style:italic; color:#aaa;">"{w['ex']}"</p></div>""", unsafe_allow_html=True)
            if st.button(f"🔊 Pronounce: {w['word']}", key=w['word']): speak_text(w['word'])

# --- MODE C: VISUAL LEARNING ---
elif mode == "👁️ VISUAL LEARNING":
    st.markdown("<h1>👁️ VISUAL DATABASE</h1>", unsafe_allow_html=True)
    category = st.selectbox("SELECT DATASET:", ["🍎 Fruits & Veggies", "💻 Tech & Tools", "🪐 Space & Planets", "🐶 Animals"])
    
    full_visual_db = {
        "🍎 Fruits & Veggies": [{"name": "Avocado", "icon": "🥑"}, {"name": "Broccoli", "icon": "🥦"}, {"name": "Strawberry", "icon": "🍓"}, {"name": "Pineapple", "icon": "🍍"}, {"name": "Carrot", "icon": "🥕"}, {"name": "Eggplant", "icon": "🍆"}, {"name": "Corn", "icon": "🌽"}, {"name": "Chili", "icon": "🌶️"}],
        "💻 Tech & Tools": [{"name": "Microchip", "icon": "💾"}, {"name": "Satellite", "icon": "📡"}, {"name": "Smartphone", "icon": "📱"}, {"name": "Telescope", "icon": "🔭"}, {"name": "Microscope", "icon": "🔬"}, {"name": "Robot", "icon": "🤖"}, {"name": "Battery", "icon": "🔋"}, {"name": "Joystick", "icon": "🕹️"}],
        "🪐 Space & Planets": [{"name": "Saturn", "icon": "🪐"}, {"name": "Rocket", "icon": "🚀"}, {"name": "Alien", "icon": "👽"}, {"name": "Meteor", "icon": "☄️"}, {"name": "Moon", "icon": "🌙"}, {"name": "Star", "icon": "⭐"}, {"name": "Sun", "icon": "☀️"}, {"name": "Earth", "icon": "🌍"}],
        "🐶 Animals": [{"name": "Fox", "icon": "🦊"}, {"name": "Whale", "icon": "🐋"}, {"name": "Owl", "icon": "🦉"}, {"name": "Tiger", "icon": "🐯"}, {"name": "Butterfly", "icon": "🦋"}, {"name": "Octopus", "icon": "🐙"}, {"name": "Sloth", "icon": "🦥"}, {"name": "Flamingo", "icon": "🦩"}]
    }
    
    category_items = full_visual_db[category]
    todays_items = random.sample(category_items, min(len(category_items), 6))
    
    c1, c2, c3 = st.columns(3)
    for i, item in enumerate(todays_items):
        col = [c1, c2, c3][i % 3]
        with col:
            st.markdown(f"""<div class="glass-card"><div class="visual-icon">{item['icon']}</div><h3 style="margin:0">{item['name']}</h3></div>""", unsafe_allow_html=True)
            if st.button(f"🔊 Say {item['name']}", key=f"vis_{item['name']}"): speak_text(item['name'])
