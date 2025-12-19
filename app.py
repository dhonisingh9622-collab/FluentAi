import sys
import types

# --- 1. CRITICAL FIX: PATCH FOR PYTHON 3.13 AUDIO ERRORS ---
# This mocks the missing 'aifc' and 'audioop' modules so the app doesn't crash
if sys.version_info >= (3, 13):
    # Fake 'aifc'
    m1 = types.ModuleType('aifc')
    m1.open = lambda *args, **kwargs: None
    m1.Error = Exception
    sys.modules['aifc'] = m1

    # Fake 'audioop'
    m2 = types.ModuleType('audioop')
    m2.add = lambda *args: b''
    m2.lin2lin = lambda *args: b''
    m2.bias = lambda *args: b''
    m2.mul = lambda *args: b''
    m2.rms = lambda *args: 0
    sys.modules['audioop'] = m2
# -----------------------------------------------------------

import streamlit as st
import openai
import speech_recognition as sr
from gtts import gTTS
import tempfile
import os
import random
from datetime import datetime

# --- 2. CONFIG MUST BE FIRST STREAMLIT COMMAND ---
st.set_page_config(
    page_title="FluentAI - Learn English",
    page_icon="🗣️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 3. APP LOGIC STARTS HERE ---

# Custom CSS for styling
st.markdown("""
<style>
    .chat-bubble {
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 10px;
        display: inline-block;
        max-width: 80%;
    }
    .user-bubble {
        background-color: #DCF8C6;
        color: black;
        float: right;
        clear: both;
    }
    .bot-bubble {
        background-color: #F1F0F0;
        color: black;
        float: left;
        clear: both;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar for API Key
with st.sidebar:
    st.title("🔧 Settings")
    api_key = st.text_input("Enter OpenAI API Key", type="password")
    if api_key:
        openai.api_key = api_key
    
    st.markdown("---")
    mode = st.radio("Choose Mode", ["🗣️ Practice Conversation", "📚 Vocabulary Builder"])

# Helper function: Text to Speech
def speak_text(text):
    if text:
        try:
            tts = gTTS(text=text, lang='en')
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                tts.save(fp.name)
                st.audio(fp.name, format="audio/mp3")
        except Exception as e:
            st.error(f"Audio Error: {e}")

# Helper function: Generate Vocabulary
def get_daily_vocab():
    # Simple list for demo purposes - in production, this could be a larger database
    vocab_db = [
        {"word": "Serendipity", "meaning": "Finding something good without looking for it.", "example": "It was pure serendipity that we met."},
        {"word": "Ephemeral", "meaning": "Lasting for a very short time.", "example": "Fashions are ephemeral, changing with every season."},
        {"word": "Resilient", "meaning": "Able to withstand or recover quickly from difficult conditions.", "example": "She is remarkably resilient to stress."},
        {"word": "Eloquent", "meaning": "Fluent or persuasive in speaking or writing.", "example": "He made an eloquent speech."},
        {"word": "Meticulous", "meaning": "Showing great attention to detail.", "example": "He was meticulous about his appearance."},
        {"word": "Pragmatic", "meaning": "Dealing with things sensibly and realistically.", "example": "We need a pragmatic approach to this problem."},
        {"word": "Ineffable", "meaning": "Too great or extreme to be expressed in words.", "example": "The beauty of the sunset was ineffable."},
        {"word": "Ubiquitous", "meaning": "Present, appearing, or found everywhere.", "example": "Smartphones are now ubiquitous."},
        {"word": "Alacrity", "meaning": "Brisk and cheerful readiness.", "example": "She accepted the invitation with alacrity."},
        {"word": "Magnanimous", "meaning": "Generous or forgiving, especially toward a rival.", "example": "He was magnanimous in victory."}
    ]
    # Use date to rotate words (or just show all 10 for demo)
    return vocab_db

# --- MODE A: CONVERSATION ---
if mode == "🗣️ Practice Conversation":
    st.header("🗣️ English Practice Partner")
    st.write("Start speaking or typing! I will correct your mistakes.")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "You are a helpful English tutor. Converse naturally. If the user makes a grammar mistake, gently correct it before continuing the topic."}
        ]

    # Display chat history
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            align = "user-bubble" if msg["role"] == "user" else "bot-bubble"
            st.markdown(f'<div class="chat-bubble {align}">{msg["content"]}</div>', unsafe_allow_html=True)
            if msg["role"] == "assistant":
                st.markdown("<div style='clear: both;'></div>", unsafe_allow_html=True)

    # Input Area
    user_input = st.chat_input("Type your message here...")

    # Voice Input Button (Simple Logic)
    if st.button("🎤 Record Voice (Experimental)"):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Listening...")
            try:
                audio = r.listen(source, timeout=5)
                text = r.recognize_google(audio)
                user_input = text
                st.success(f"You said: {text}")
            except Exception as e:
                st.warning("Could not recognize voice. Please type instead.")

    if user_input:
        if not api_key:
            st.warning("Please enter your OpenAI API Key in the sidebar first!")
        else:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.rerun()

    # Generate AI Response
    if st.session_state.messages[-1]["role"] == "user" and api_key:
        with st.spinner("Thinking..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=st.session_state.messages
                )
                ai_msg = response.choices[0].message['content']
                st.session_state.messages.append({"role": "assistant", "content": ai_msg})
                
                # Show latest message and speak it
                st.markdown(f'<div class="chat-bubble bot-bubble">{ai_msg}</div>', unsafe_allow_html=True)
                speak_text(ai_msg)
                
            except Exception as e:
                st.error(f"OpenAI Error: {e}")

# --- MODE B: VOCABULARY ---
elif mode == "📚 Vocabulary Builder":
    st.header("📚 Daily Vocabulary")
    st.write("Here are 10 sophisticated words to learn today.")
    
    vocab_list = get_daily_vocab()
    
    col1, col2 = st.columns(2)
    
    for i, item in enumerate(vocab_list):
        # Alternate columns
        with col1 if i % 2 == 0 else col2:
            with st.container(border=True):
                st.subheader(item['word'])
                st.markdown(f"**Meaning:** {item['meaning']}")
                st.markdown(f"_{item['example']}_")
                if st.button(f"🔊 Pronounce {item['word']}", key=f"btn_{i}"):
                    speak_text(item['word'])
