import sys
import types
import streamlit as st

# --- 1. THE ULTIMATE PATCH (Fixes aifc, audioop, AND distutils) ---
# This "tricks" the app into thinking the old Python files still exist.
if sys.version_info >= (3, 12):
    # Fix 1: Mock 'distutils' (Required for Microphone)
    if 'distutils' not in sys.modules:
        m_dist = types.ModuleType('distutils')
        m_dist.version = types.ModuleType('version')
        
        class LooseVersion:
            def __init__(self, v): self.v = v
            def __ge__(self, other): return True  # Always pretend we are new enough
            
        m_dist.version.LooseVersion = LooseVersion
        sys.modules['distutils'] = m_dist
        sys.modules['distutils.version'] = m_dist.version

    # Fix 2: Mock 'aifc' (Removed in Py 3.13)
    m_aifc = types.ModuleType('aifc')
    m_aifc.open = lambda *args, **kwargs: None
    m_aifc.Error = Exception
    sys.modules['aifc'] = m_aifc

    # Fix 3: Mock 'audioop' (Removed in Py 3.13)
    m_audioop = types.ModuleType('audioop')
    m_audioop.add = lambda *args: b''
    sys.modules['audioop'] = m_audioop
# ------------------------------------------------------------------

import openai
import speech_recognition as sr
from gtts import gTTS
import tempfile
import os
from datetime import datetime

# --- 2. PAGE CONFIG ---
st.set_page_config(
    page_title="FluentAI - Learn English",
    page_icon="🗣️",
    layout="wide"
)

# --- 3. APP LOGIC ---
st.markdown("""
<style>
    .chat-bubble { padding: 15px; border-radius: 15px; margin-bottom: 10px; display: inline-block; max-width: 80%; }
    .user-bubble { background-color: #DCF8C6; color: black; float: right; clear: both; }
    .bot-bubble { background-color: #F1F0F0; color: black; float: left; clear: both; }
    .vocab-card { padding: 20px; background-color: #f0f2f6; border-radius: 10px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🔧 Settings")
    api_key = st.text_input("Enter OpenAI API Key", type="password")
    if api_key: openai.api_key = api_key
    mode = st.radio("Choose Mode", ["🗣️ Practice Conversation", "📚 Vocabulary Builder"])

def speak_text(text):
    if text:
        try:
            tts = gTTS(text=text, lang='en')
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                tts.save(fp.name)
                st.audio(fp.name, format="audio/mp3")
        except Exception as e:
            st.error(f"Audio Error: {e}")

# --- MODE A: CONVERSATION ---
if mode == "🗣️ Practice Conversation":
    st.header("🗣️ English Practice Partner")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": "You are a helpful English tutor. Correct grammar mistakes gently."}]

    for msg in st.session_state.messages:
        if msg["role"] != "system":
            align = "user-bubble" if msg["role"] == "user" else "bot-bubble"
            st.markdown(f'<div class="chat-bubble {align}">{msg["content"]}</div>', unsafe_allow_html=True)
            if msg["role"] == "assistant":
                st.markdown("<div style='clear: both;'></div>", unsafe_allow_html=True)

    user_input = st.chat_input("Type your message here...")

    # Voice Input with SAFEGUARD
    if st.button("🎤 Record Voice (Beta)"):
        st.info("Listening... (Note: This may fail on Cloud servers without a mic attached)")
        try:
            r = sr.Recognizer()
            with sr.Microphone() as source:
                audio = r.listen(source, timeout=3)
                text = r.recognize_google(audio)
                user_input = text
        except OSError:
            st.error("⚠️ No Microphone Found: Since this app is running on the Cloud, it cannot access your phone's microphone directly using this method. Please use the Text Input box below!")
        except Exception as e:
            st.warning(f"Voice Error: {e}")

    if user_input:
        if not api_key:
            st.warning("Please enter your OpenAI API Key first!")
        else:
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.rerun()

    if st.session_state.messages[-1]["role"] == "user" and api_key:
        with st.spinner("Thinking..."):
            try:
                response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
                ai_msg = response.choices[0].message['content']
                st.session_state.messages.append({"role": "assistant", "content": ai_msg})
                st.markdown(f'<div class="chat-bubble bot-bubble">{ai_msg}</div>', unsafe_allow_html=True)
                speak_text(ai_msg)
            except Exception as e:
                st.error(f"OpenAI Error: {e}")

# --- MODE B: VOCABULARY ---
elif mode == "📚 Vocabulary Builder":
    st.header("📚 Daily Vocabulary")
    words = [
        {"word": "Serendipity", "meaning": "Good luck in finding valuable things unintentionally."},
        {"word": "Resilient", "meaning": "Able to withstand or recover quickly from difficult conditions."},
        {"word": "Eloquent", "meaning": "Fluent or persuasive in speaking or writing."},
        {"word": "Ephemeral", "meaning": "Lasting for a very short time."},
        {"word": "Ubiquitous", "meaning": "Present, appearing, or found everywhere."}
    ]
    
    col1, col2 = st.columns(2)
    for i, w in enumerate(words):
        with col1 if i % 2 == 0 else col2:
            # FIX: Removed 'border=True' and used custom CSS class instead
            st.markdown(f"""
            <div class="vocab-card">
                <h3>{w['word']}</h3>
                <p><strong>Meaning:</strong> {w['meaning']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"🔊 Listen", key=w['word']):
                speak_text(w['word'])
