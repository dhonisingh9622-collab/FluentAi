"""
FluentAI - Interactive English Language Learning Web App
========================================================

HOW TO RUN:
1. Install dependencies: pip install -r requirements.txt
2. Run the app: streamlit run main.py
3. Enter your OpenAI API key in the sidebar
4. Start learning!

Author: Expert Python Full-Stack Developer
"""

import streamlit as st
import openai
from gtts import gTTS
import speech_recognition as sr
from datetime import datetime
import random
import os
import base64
from io import BytesIO
import tempfile

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="FluentAI - Learn English",
    page_icon="🗣️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS STYLING
# ============================================================================
def load_custom_css():
    st.markdown("""
    <style>
    /* Main background with gradient */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #4facfe 0%, #00f2fe 100%);
    }
    
    /* Custom card styling */
    .vocab-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    
    .vocab-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.2);
    }
    
    /* Chat message styling */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 15px 15px 0 15px;
        margin: 10px 0;
        max-width: 80%;
        float: right;
        clear: both;
    }
    
    .ai-message {
        background: white;
        color: #333;
        padding: 15px;
        border-radius: 15px 15px 15px 0;
        margin: 10px 0;
        max-width: 80%;
        float: left;
        clear: both;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 30px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    }
    
    /* Title styling */
    .main-title {
        color: white;
        text-align: center;
        font-size: 3em;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }
    
    .subtitle {
        color: white;
        text-align: center;
        font-size: 1.3em;
        margin-bottom: 30px;
    }
    
    /* Input field styling */
    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 2px solid #667eea;
    }
    
    /* Clear float */
    .clearfix::after {
        content: "";
        clear: both;
        display: table;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
def init_session_state():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'mode' not in st.session_state:
        st.session_state.mode = 'home'
    if 'daily_words' not in st.session_state:
        st.session_state.daily_words = []

# ============================================================================
# TEXT-TO-SPEECH FUNCTION
# ============================================================================
def text_to_speech(text, lang='en'):
    """Convert text to speech and return audio player HTML"""
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_base64 = base64.b64encode(fp.read()).decode()
        audio_html = f'<audio autoplay controls><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
        return audio_html
    except Exception as e:
        st.error(f"Error generating speech: {e}")
        return None

# ============================================================================
# SPEECH-TO-TEXT FUNCTION
# ============================================================================
def speech_to_text():
    """Capture audio from microphone and convert to text"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening... Speak now!")
        try:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            st.success("✅ Processing your speech...")
            text = recognizer.recognize_google(audio)
            return text
        except sr.WaitTimeoutError:
            st.warning("⏱️ No speech detected. Please try again.")
            return None
        except sr.UnknownValueError:
            st.warning("❓ Could not understand audio. Please speak clearly.")
            return None
        except Exception as e:
            st.error(f"Error: {e}")
            return None

# ============================================================================
# OPENAI API INTERACTION
# ============================================================================
def get_ai_response(user_message, api_key):
    """Get response from OpenAI API with grammar correction capability"""
    try:
        openai.api_key = api_key
        
        # System prompt for the AI tutor
        system_prompt = """You are FluentAI, a friendly and patient English tutor. Your role is to:
        1. Have natural conversations with students learning English
        2. If you detect ANY grammatical errors, spelling mistakes, or awkward phrasing, GENTLY correct them first
        3. Use this format for corrections: "Just a small note: You said '[incorrect]', but it would be better to say '[correct]'. [Brief explanation]"
        4. After corrections, continue the conversation naturally
        5. Be encouraging, positive, and supportive
        6. Use simple language and explain complex words when needed
        7. Ask follow-up questions to keep the conversation flowing
        """
        
        # Prepare messages with chat history
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add chat history (last 10 messages to keep context)
        for msg in st.session_state.chat_history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Get response from OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        ai_message = response.choices[0].message.content
        return ai_message
    
    except Exception as e:
        return f"❌ Error connecting to AI: {str(e)}"

# ============================================================================
# DAILY VOCABULARY GENERATOR
# ============================================================================
def generate_daily_vocabulary():
    """Generate 10 sophisticated vocabulary words for the day"""
    # Use today's date as seed for consistent daily words
    today = datetime.now().strftime("%Y-%m-%d")
    random.seed(today)
    
    # Sophisticated vocabulary database
    vocab_database = [
        {
            "word": "Ephemeral",
            "definition": "Lasting for a very short time; transitory.",
            "example": "The beauty of cherry blossoms is ephemeral, lasting only a few weeks each spring."
        },
        {
            "word": "Serendipity",
            "definition": "The occurrence of events by chance in a happy or beneficial way.",
            "example": "Finding that rare book in the old library was pure serendipity."
        },
        {
            "word": "Eloquent",
            "definition": "Fluent or persuasive in speaking or writing.",
            "example": "Her eloquent speech moved the entire audience to tears."
        },
        {
            "word": "Ubiquitous",
            "definition": "Present, appearing, or found everywhere.",
            "example": "Smartphones have become ubiquitous in modern society."
        },
        {
            "word": "Resilient",
            "definition": "Able to withstand or recover quickly from difficult conditions.",
            "example": "The resilient community rebuilt their town after the disaster."
        },
        {
            "word": "Enigmatic",
            "definition": "Difficult to interpret or understand; mysterious.",
            "example": "The Mona Lisa's enigmatic smile has puzzled viewers for centuries."
        },
        {
            "word": "Paradigm",
            "definition": "A typical example or pattern of something; a model.",
            "example": "The internet created a paradigm shift in how we communicate."
        },
        {
            "word": "Meticulous",
            "definition": "Showing great attention to detail; very careful and precise.",
            "example": "The surgeon's meticulous work ensured a successful operation."
        },
        {
            "word": "Ambiguous",
            "definition": "Open to more than one interpretation; not having one obvious meaning.",
            "example": "The politician's ambiguous statement left voters confused about her position."
        },
        {
            "word": "Benevolent",
            "definition": "Well-meaning and kindly; showing goodwill.",
            "example": "The benevolent billionaire donated millions to charity."
        },
        {
            "word": "Cacophony",
            "definition": "A harsh, discordant mixture of sounds.",
            "example": "The cacophony of car horns filled the busy street."
        },
        {
            "word": "Diligent",
            "definition": "Having or showing care and conscientiousness in one's work or duties.",
            "example": "Her diligent study habits helped her achieve excellent grades."
        },
        {
            "word": "Exacerbate",
            "definition": "Make a problem, bad situation, or negative feeling worse.",
            "example": "The heavy rain exacerbated the flooding in the valley."
        },
        {
            "word": "Fastidious",
            "definition": "Very attentive to accuracy and detail; hard to please.",
            "example": "He was fastidious about keeping his workspace clean and organized."
        },
        {
            "word": "Gregarious",
            "definition": "Fond of company; sociable.",
            "example": "Her gregarious nature made her popular at social gatherings."
        },
        {
            "word": "Idiosyncratic",
            "definition": "Relating to peculiar behavioral habits or mannerisms.",
            "example": "The artist had an idiosyncratic way of signing his paintings."
        },
        {
            "word": "Juxtapose",
            "definition": "Place or deal with close together for contrasting effect.",
            "example": "The museum juxtaposed ancient artifacts with modern art."
        },
        {
            "word": "Loquacious",
            "definition": "Tending to talk a great deal; talkative.",
            "example": "The loquacious host kept the dinner party lively with constant conversation."
        },
        {
            "word": "Nebulous",
            "definition": "In the form of a cloud or haze; unclear, vague, or ill-defined.",
            "example": "The company's plans for expansion remained nebulous."
        },
        {
            "word": "Ostentatious",
            "definition": "Characterized by vulgar or pretentious display; designed to impress.",
            "example": "His ostentatious mansion had gold-plated doorknobs and marble floors."
        }
    ]
    
    # Select 10 random words for today
    daily_words = random.sample(vocab_database, min(10, len(vocab_database)))
    return daily_words

# ============================================================================
# HOME PAGE
# ============================================================================
def show_home():
    st.markdown('<h1 class="main-title">🗣️ FluentAI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Your Personal English Language Learning Assistant</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style='background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3);'>
            <h2 style='text-align: center; color: #667eea;'>Welcome to FluentAI! 👋</h2>
            <p style='text-align: center; font-size: 1.1em; color: #555;'>
                Choose a mode to start your English learning journey:
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        st.write("")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("💬 Practice Conversation", use_container_width=True):
                st.session_state.mode = 'conversation'
                st.rerun()
            st.markdown("""
            <div style='background: #f0f7ff; padding: 15px; border-radius: 10px; margin-top: 10px;'>
                <p style='text-align: center; color: #555;'>
                    Chat with AI tutor<br>Voice enabled<br>Grammar corrections
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_b:
            if st.button("📚 Daily Vocabulary", use_container_width=True):
                st.session_state.mode = 'vocabulary'
                st.rerun()
            st.markdown("""
            <div style='background: #fff0f5; padding: 15px; border-radius: 10px; margin-top: 10px;'>
                <p style='text-align: center; color: #555;'>
                    Learn 10 new words<br>Hear pronunciations<br>See examples
                </p>
            </div>
            """, unsafe_allow_html=True)

# ============================================================================
# MODE A: PRACTICE CONVERSATION
# ============================================================================
def show_conversation_mode(api_key):
    st.markdown('<h2 style="color: white; text-align: center;">💬 Practice Conversation</h2>', unsafe_allow_html=True)
    
    if not api_key:
        st.error("⚠️ Please enter your OpenAI API key in the sidebar to use this feature.")
        return
    
    # Display chat history
    st.markdown('<div class="clearfix">', unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-message">👤 You: {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ai-message">🤖 FluentAI: {msg["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.write("")
    st.write("")
    
    # Input methods
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_input = st.text_input("Type your message:", key="text_input", placeholder="Start typing or click the microphone...")
    
    with col2:
        use_voice = st.button("🎤 Speak", use_container_width=True)
    
    # Handle voice input
    if use_voice:
        spoken_text = speech_to_text()
        if spoken_text:
            user_input = spoken_text
            st.info(f"You said: {spoken_text}")
    
    # Send button
    if st.button("Send ✉️", use_container_width=True) and user_input:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Get AI response
        with st.spinner("🤔 FluentAI is thinking..."):
            ai_response = get_ai_response(user_input, api_key)
        
        # Add AI response to history
        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
        
        # Generate speech for AI response
        audio_html = text_to_speech(ai_response)
        if audio_html:
            st.markdown(audio_html, unsafe_allow_html=True)
        
        st.rerun()
    
    # Clear chat button
    if st.button("🔄 Clear Conversation"):
        st.session_state.chat_history = []
        st.rerun()

# ============================================================================
# MODE B: DAILY VOCABULARY
# ============================================================================
def show_vocabulary_mode():
    st.markdown('<h2 style="color: white; text-align: center;">📚 Daily Vocabulary Builder</h2>', unsafe_allow_html=True)
    st.markdown(f'<p style="color: white; text-align: center; font-size: 1.1em;">Today\'s Date: {datetime.now().strftime("%B %d, %Y")}</p>', unsafe_allow_html=True)
    
    # Generate daily vocabulary
    if not st.session_state.daily_words:
        st.session_state.daily_words = generate_daily_vocabulary()
    
    st.write("")
    
    # Display vocabulary cards
    for i, word_data in enumerate(st.session_state.daily_words):
        with st.container():
            st.markdown(f"""
            <div class="vocab-card">
                <h3 style="color: #667eea; margin-bottom: 10px;">
                    {i+1}. {word_data['word']}
                </h3>
                <p style="color: #666; font-style: italic; margin-bottom: 10px;">
                    <strong>Definition:</strong> {word_data['definition']}
                </p>
                <p style="color: #333; background: #f8f9fa; padding: 10px; border-radius: 8px; border-left: 4px solid #667eea;">
                    <strong>Example:</strong> "{word_data['example']}"
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Pronunciation button
            if st.button(f"🔊 Play Pronunciation", key=f"play_{i}"):
                audio_html = text_to_speech(word_data['word'])
                if audio_html:
                    st.markdown(audio_html, unsafe_allow_html=True)
                
                # Also play the example sentence
                st.info("Playing example sentence...")
                example_audio = text_to_speech(word_data['example'])
                if example_audio:
                    st.markdown(example_audio, unsafe_allow_html=True)
            
            st.write("")

# ============================================================================
# SIDEBAR
# ============================================================================
def show_sidebar():
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        # API Key input
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Enter your OpenAI API key to enable conversation features"
        )
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### 🧭 Navigation")
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.mode = 'home'
            st.rerun()
        
        if st.button("💬 Conversation", use_container_width=True):
            st.session_state.mode = 'conversation'
            st.rerun()
        
        if st.button("📚 Vocabulary", use_container_width=True):
            st.session_state.mode = 'vocabulary'
            st.rerun()
        
        st.markdown("---")
        
        # Info section
        st.markdown("### ℹ️ About FluentAI")
        st.info("""
        **FluentAI** is your personal English learning assistant powered by AI.
        
        **Features:**
        - 💬 Natural conversations
        - ✏️ Grammar corrections
        - 🎤 Voice input/output
        - 📚 Daily vocabulary
        - 🔊 Pronunciation practice
        """)
        
        st.markdown("---")
        st.markdown("Made with ❤️ by FluentAI Team")
        
        return api_key

# ============================================================================
# MAIN APPLICATION
# ============================================================================
def main():
    # Load custom CSS
    load_custom_css()
    
    # Initialize session state
    init_session_state()
    
    # Show sidebar and get API key
    api_key = show_sidebar()
    
    # Route to appropriate mode
    if st.session_state.mode == 'home':
        show_home()
    elif st.session_state.mode == 'conversation':
        show_conversation_mode(api_key)
    elif st.session_state.mode == 'vocabulary':
        show_vocabulary_mode()

# ============================================================================
# RUN APPLICATION
# ============================================================================
if __name__ == "__main__":
    main()
