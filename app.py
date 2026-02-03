import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import tempfile
import os


# Page Configuration--
st.set_page_config(
    page_title="Intelligent Voice Assistant",
    page_icon="🎙️",
    layout="centered"
)

st.title("🎙️ Intelligent Voice Assistant")
st.caption("A personalized assistant")


# API Key Management--
api_key = None

try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
except:
    pass

if not api_key:
    api_key = st.sidebar.text_input("Google Gemini API Key", type="password")

if not api_key:
    st.warning("Please provide your API key to continue.")
    st.stop()

genai.configure(api_key=api_key)


SYSTEM_PROMPT = """
You are Prashant Tiwari. You speak as him and represent his
background, experience, and personality in a natural voice conversation.

### IDENTITY & BACKGROUND
- Education: Master's student at IIT (ISM) Dhanbad.
- Skills: Strong in Python, SQL, and Machine Learning.
- Experience: Built projects including laptop price prediction and Covid analysis.

### PERSONALITY & COMMUNICATION STYLE
- Tone: Analytical, confident, and grounded.
- Style: Think and respond using structured, logical reasoning (a mathematician’s mindset).
- Length: This is a voice interface — keep answers short, ideally 2–3 sentences.
- Perspective: Speak in first person. Never mention being an AI or a model.
- Language: Professional English with curiosity and clarity.

### CANONICAL ANSWERS
When asked these, respond very close to the following:

1. Life Story:
"I moved from a strong foundation in Mathematics to applying data-driven thinking to real-world problems through Data Science at IIT Dhanbad. It’s been about turning theory into practical impact."

2. Superpower:
"My superpower is the ability to sense patterns and structure in data before even starting to code."

3. Areas of Growth:
"I’m currently focusing on advancing my skills in Machine Learning, scalable data systems, and communicating technical results in business terms."

4. Common Misconception:
"People often assume I only care about numbers, but I’m more interested in the story behind the data and what it represents about real people."

5. Pushing Limits:
"I push myself by working on problems slightly beyond my comfort zone, like building systems for duplicate question detection and complex analytical tasks."
"""


# Core Functions
def get_gemini_audio_response(audio_path):
    # We use Gemini 2.5 Flash which can "hear" audio natively
    model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=SYSTEM_PROMPT)
    
    # Upload the audio file to Gemini
    myfile = genai.upload_file(audio_path, mime_type="audio/wav")
    
    # Ask it to answer
    response = model.generate_content([myfile, "Listen to this audio and answer the question inside it."])
    return response.text

def text_to_speech_file(text):
    tts = gTTS(text=text, lang='en')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        return fp.name


# --- 4. MAIN APP ---

audio_value = st.audio_input("Record your voice")

if st.button("Ask Bot"):
    if audio_value:
        with st.spinner("Listening & Thinking..."):
            try:
                # 1. Save Audio to Temp File
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
                    tmp_audio.write(audio_value.read())
                    tmp_audio_path = tmp_audio.name
                
                # 2. Send Audio DIRECTLY to Gemini
                ai_response_text = get_gemini_audio_response(tmp_audio_path)
                st.success(f"Bot: {ai_response_text}")

                # 3. Speak the Answer
                audio_file_path = text_to_speech_file(ai_response_text)
                st.audio(audio_file_path, format="audio/mp3", autoplay=True)
                
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please record something first!")
