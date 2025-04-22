import streamlit as st
import sys
import tempfile
import os
import speech_recognition as sr
from ai.summarize import summarize_notes
from ai.sentiment import analyze_sentiment
from ai.flashcards import generate_flashcards
from voice.transcribe import transcribe_audio_google
from voice.speak import speak_text
from db.firebase_setup import save_journal_entry, fetch_journal_entries
import torch

# Exclude torch from being watched to avoid RuntimeError
sys.modules["torch.classes"] = None

# Force file watching to avoid update issues on some systems
os.environ["STREAMLIT_WATCH_USE_POLLING"] = "true"

# App Config
st.set_page_config(page_title="UniVerse - AI College Assistant")
st.title("🌌 UniVerse - AI-Powered College Assistant")
st.markdown("---")




# Initialize session state
if "recording" not in st.session_state:
    st.session_state.recording = False
if "audio_file" not in st.session_state:
    st.session_state.audio_file = None

# VOICE MODE
st.header("🎙️ Voice Mode")

mode = st.radio("Choose Input Mode:", ["Record Live", "Upload Audio"])

if mode == "Record Live":
    st.write("🎤 Live Voice Recorder (max 30 seconds or click to stop)")

    if not st.session_state.recording:
        if st.button("🟢 Start Recording"):
            st.session_state.recording = True
            st.rerun()

    if st.session_state.recording:
        st.info("🔴 Recording... Speak now. Click stop or wait 30s.")
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            audio_data = recognizer.listen(source, timeout=30, phrase_time_limit=30)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_data.get_wav_data())
            st.session_state.audio_file = temp_audio.name
        st.session_state.recording = False
        st.rerun()


    if st.session_state.audio_file and not st.session_state.recording:
        transcription = transcribe_audio_google(st.session_state.audio_file)
        st.success(f"You said: {transcription}")
        mood = analyze_sentiment(transcription)
        st.info(f"Detected Mood: {mood}")
        speak_text(f"Thanks for sharing! I sense you feel {mood}")
        st.session_state.audio_file = None

elif mode == "Upload Audio":
    audio_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "m4a"])
    if audio_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_file.read())
            temp_audio.flush()
            transcription = transcribe_audio_google(temp_audio.name)
            st.success(f"You said: {transcription}")
            sentiment = analyze_sentiment(transcription)
            st.info(f"Detected Mood: {sentiment}")
            speak_text(f"Thanks for sharing! I sense you feel {sentiment}")

# PDF Summarizer
st.markdown("---")
st.header("📄 Summarize Lecture Notes")
uploaded_file = st.file_uploader("Upload your notes (PDF)", type="pdf")
if uploaded_file:
    summary = summarize_notes(uploaded_file)
    st.subheader("📝 Summary:")
    st.write(summary)

    flashcards = generate_flashcards(summary)
    st.subheader("📚 Flashcards:")
    for i, (q, a) in enumerate(flashcards):
        st.markdown(f"**Q{i+1}:** {q}")
        st.markdown(f"**A:** {a}")

# Journal
st.markdown("---")
st.header("📔 Mental Health Journal")
user_id = "student_001"
journal_input = st.text_area("Write about your day")

col1, col2 = st.columns(2)
if col1.button("🧠 Analyze & Save Mood"):
    if journal_input.strip():
        mood = analyze_sentiment(journal_input)
        st.success(f"Your journal mood is: **{mood}**")
        save_journal_entry(user_id, journal_input, mood)
        st.info("📝 Entry saved to your journal.")
    else:
        st.warning("Please write something before analyzing.")

if col2.button("📖 Show My Journal"):
    entries = fetch_journal_entries(user_id)
    if entries:
        st.subheader("📘 Your Entries:")
        for entry in entries:
            st.markdown(f"**Mood:** {entry['mood']}")
            st.markdown(f"> {entry['text']}")
            st.markdown("---")
    else:
        st.info("No journal entries found.")
