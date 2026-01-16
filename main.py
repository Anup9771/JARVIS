import os
import time
import requests
import speech_recognition as sr
import pyttsx3
import webbrowser

# ---------------- Configuration ----------------
WAKE_WORDS = ("jarvis", "hey jarvis")
LANG = "en-US"

# 🔹 Hardcoded Gemini API key (replace with your own)
GEMINI_API_KEY = "AIzaSyBfgEe-0cnJ7AP49ETKXPv-Cvf0DGsPPzc"

# Fixed Gemini endpoint
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

# ---------------- TTS Setup ----------------
tts_engine = pyttsx3.init()
def speak(text):
    try:
        tts_engine.say(text)
        tts_engine.runAndWait()
    except Exception as e:
        print("[Jarvis] TTS error:", e)

# ---------------- Gemini API Call ----------------
def call_gemini(prompt, max_tokens=256, temperature=0.7):
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}
    }
    try:
        resp = requests.post(GEMINI_API_URL, headers=headers, params=params, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print("[Jarvis] Error contacting Gemini API:", e)
        return "Sorry, I couldn't reach the assistant."

# ---------------- Speech Recognition ----------------
recognizer = sr.Recognizer()
mic = sr.Microphone()

def listen_for_speech(timeout=None, phrase_time_limit=None):
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.4)
        print("[Jarvis] Listening...")
        audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
    try:
        return recognizer.recognize_google(audio, language=LANG)
    except:
        return ""

# ---------------- Local Commands ----------------
def handle_local_commands(query):
    query = query.lower()
    if "youtube" in query:
        speak("Opening YouTube.")
        webbrowser.open("https://www.youtube.com")
        return True
    if "google" in query:
        speak("Opening Google.")
        webbrowser.open("https://www.google.com")
        return True
    if "time" in query:
        from datetime import datetime
        now = datetime.now().strftime("%H:%M")
        speak(f"The time is {now}")
        return True
    return False  # No local command matched

# ---------------- Main Assistant Loop ----------------
def run_assistant():
    print("[Jarvis] Jarvis is awake. Say the wake word ('jarvis').")
    while True:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.4)
            audio = recognizer.listen(source, timeout=None, phrase_time_limit=4)
        try:
            text = recognizer.recognize_google(audio, language=LANG).lower()
        except:
            text = ""

        if any(w in text for w in WAKE_WORDS):
            speak("Yes, how can I help?")
            user_query = listen_for_speech(timeout=8, phrase_time_limit=25)
            if not user_query:
                speak("I didn't catch that. Try again.")
                continue

            print("[Jarvis] Query ->", user_query)
            # First check local commands
            if handle_local_commands(user_query):
                continue

            # Otherwise, send to Gemini API
            speak("Let me think...")
            response = call_gemini(user_query)
            print("[Jarvis] Assistant:", response)
            speak(response)

# ---------------- Run ----------------
if __name__ == "__main__":
    run_assistant()
