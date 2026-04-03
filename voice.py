import speech_recognition as sr
import os
import requests
import random
from rapidfuzz import process, fuzz
from dotenv import load_dotenv

load_dotenv()
# =========================
# LOAD ENV
# =========================
API_KEY = os.getenv("OPENROUTER_API_KEY")
print("API Key Loaded:", API_KEY)

# =========================
# SPEAK (FAST macOS)
# =========================
def speak(text):
    print(f"Robot: {text}")
    os.system(f'say "{text}"')


# =========================
# INIT MIC
# =========================
recognizer = sr.Recognizer()
mic = sr.Microphone()

# Tune recognizer to capture short words and longer sentences more reliably.
recognizer.pause_threshold = 0.9
recognizer.phrase_threshold = 0.2
recognizer.non_speaking_duration = 0.5


def calibrate_microphone():
    with mic as source:
        print("[INFO] Calibrating microphone for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=0.6)
        print(f"[INFO] Energy threshold set to: {recognizer.energy_threshold:.0f}")


# =========================
# GREETINGS (INSTANT MATCH)
# =========================
GREETINGS = {
    "hello": "Hello. Welcome to PCPS College. How may I assist you??",
    "hi": "Hi there. Welcome to PCPS College. How can I help you today?",
    "hey": "Hey. Welcome to PCPS College. What do you need help with?",
    "good morning": "Good morning. Welcome to PCPS College. How may I assist you?",
    "good afternoon": "Good afternoon. Welcome to PCPS College. How may I assist you?"
}

SMALL_TALK = {
    "how are you": [
        "I am doing well, thank you. How may I assist you?",
        "I am functioning properly and ready to help you.",
        "I am great. How can I help you today?"
    ],
    "what's going on": [
        "Everything is running smoothly. How may I assist you?",
        "I am here and ready to help you.",
        "Not much, I am waiting to assist visitors."
    ],
    "what is going on": [
        "Everything is running smoothly. How may I assist you?",
        "I am here and ready to help you.",
        "Not much, I am waiting to assist visitors."
    ],
    "how is it going": [
        "It is going well. How can I help you today?",
        "All systems are working fine. How may I assist you?",
        "I am doing well and ready to assist you."
    ],
    "who are you": [
        "I am the AI powered Robo Receptionist of PCPS College.",
        "I am your smart reception assistant.",
        "I am here to welcome and guide visitors at PCPS College."
    ],
    "what can you do": [
        "I can answer basic questions, guide visitors, and provide information.",
        "I can help with directions, schedules, and general college information.",
        "I can listen, respond, and assist you with common queries."
    ],
    "thank you": [
        "You are welcome.",
        "My pleasure.",
        "Glad I could help."
    ],
    "thanks": [
        "You are welcome.",
        "Anytime.",
        "Glad I could help."
    ],
    "bye": [
        "Goodbye. Have a nice day.",
        "See you later.",
        "Thank you for visiting PCPS College."
    ],
    "goodbye": [
        "Goodbye. Have a nice day.",
        "Take care.",
        "Thank you for visiting PCPS College."
    ],
    "nice to meet you": [
        "Nice to meet you too.",
        "It is a pleasure to meet you.",
        "I am pleased to assist you."
    ]
}

# =========================
# FAQ DATABASE (FAST)
# =========================
FAQ = {
    "software engineering": "Software Engineering is a 4 year program covering web, mobile, and cloud development.",
    "bba": "BBA is a 3 year program focused on business, finance, and marketing.",
    "fees": "Software Engineering costs around 4 lakhs per year, and BBA around 1.5 lakhs.",
    "admission": "Admission is based on merit. Please visit the admission office or website.",
    "library": "The library is open from 8 AM to 8 PM and has over 50,000 books.",
    "it department": "The IT department is located on the third floor, room 306."
}


# =========================
# LISTEN (FAST)
# =========================
def listen():
    with mic as source:
        print("Listening...")

        try:
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=7)
        except sr.WaitTimeoutError:
            print("[DEBUG] No speech detected within timeout")
            return ""
        except Exception as e:
            print(f"[ERROR] Listen failed: {e}")
            return ""

    try:
        text = recognizer.recognize_google(audio)
        print("User:", text)
        return text.lower()
    except sr.UnknownValueError:
        print("[DEBUG] Could not understand audio")
        return ""
    except sr.RequestError as e:
        print(f"[ERROR] Google API error: {e}")
        return ""
    except Exception as e:
        print(f"[ERROR] Recognition failed: {e}")
        return ""


# =========================
# GREETING CHECK (FAST)
# =========================
def check_greeting(user_input):
    normalized_input = user_input.lower().strip()

    # Check exact phrases first so short inputs like "hi" or "hey" stay accurate.
    if normalized_input in GREETINGS:
        print(f"[DEBUG] Matched greeting: {normalized_input}")
        return GREETINGS[normalized_input]

    # Fall back to phrase containment for inputs like "hello there"
    for greeting_word, response in GREETINGS.items():
        if greeting_word in normalized_input:
            print(f"[DEBUG] Matched greeting: {greeting_word}")
            return response
    return None


# =========================
# SMALL TALK CHECK (FAST)
# =========================
def check_small_talk(user_input):
    normalized_input = user_input.lower().strip()

    if normalized_input in SMALL_TALK:
        print(f"[DEBUG] Matched small talk: {normalized_input} (score: 100)")
        return random.choice(SMALL_TALK[normalized_input])

    for phrase in SMALL_TALK:
        if phrase in normalized_input:
            print(f"[DEBUG] Matched small talk: {phrase} (score: 100)")
            return random.choice(SMALL_TALK[phrase])

    match = process.extractOne(
        normalized_input,
        list(SMALL_TALK.keys()),
        scorer=fuzz.token_sort_ratio,
        score_cutoff=70
    )

    if match:
        matched_phrase, score, _ = match
        response = random.choice(SMALL_TALK[matched_phrase])
        print(f"[DEBUG] Matched small talk: {matched_phrase} (score: {score})")
        return response

    return None


# =========================
# FAQ MATCH (FAST)
# =========================
def match_faq(user_input):
    normalized_input = user_input.lower().strip()

    if normalized_input in FAQ:
        print(f"[DEBUG] Matched FAQ: {normalized_input} (score: 100)")
        return FAQ[normalized_input]

    for phrase in FAQ:
        if phrase in normalized_input:
            print(f"[DEBUG] Matched FAQ: {phrase} (score: 100)")
            return FAQ[phrase]

    match = process.extractOne(
        normalized_input,
        list(FAQ.keys()),
        scorer=fuzz.token_sort_ratio,
        score_cutoff=70
    )

    if match:
        matched_phrase, score, _ = match
        print(f"[DEBUG] Matched FAQ: {matched_phrase} (score: {score})")
        return FAQ[matched_phrase]

    return None


# =========================
# AI FALLBACK (OPENROUTER)
# =========================
def ask_ai(question):
    if not API_KEY:
        print("[ERROR] API key not configured")
        return "API key not configured."

    try:
        print(f"[DEBUG] Calling AI fallback with: {question}")
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost",
                "X-Title": "Robo Receptionist"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are a helpful college receptionist. Answer briefly and clearly."},
                    {"role": "user", "content": question}
                ]
            },
            timeout=10
        )

        data = response.json()

        if "choices" in data:
            result = data["choices"][0]["message"]["content"]
            print(f"[DEBUG] AI response received")
            return result
        else:
            error_msg = data.get("error", {}).get("message", "AI error occurred.")
            print(f"[ERROR] API error: {error_msg}")
            return error_msg

    except requests.Timeout:
        print("[ERROR] API request timed out")
        return "API request timed out. Please try again."
    except requests.RequestException as e:
        print(f"[ERROR] Network error: {e}")
        return f"Network error: {str(e)}"
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return f"System error: {str(e)}"


# =========================
# MAIN RESPONSE ENGINE
# =========================
def respond(user_input):
    if not user_input or user_input.strip() == "":
        print("[DEBUG] Empty input, skipping")
        return

    print(f"[DEBUG] Processing input: '{user_input}'")

    # 1. Greeting (instant)
    greeting = check_greeting(user_input)
    if greeting:
        speak(greeting)
        return

    # 2. Small Talk (fast)
    small_talk = check_small_talk(user_input)
    if small_talk:
        speak(small_talk)
        return

    # 3. FAQ (fast)
    faq = match_faq(user_input)
    if faq:
        speak(faq)
        return

    # 4. AI fallback (smart)
    print("[DEBUG] Using AI fallback")
    ai_response = ask_ai(user_input)
    speak(ai_response)


# =========================
# MAIN LOOP
# =========================
if __name__ == "__main__":
    calibrate_microphone()
    speak("System ready. How can I help you?")
    
    while True:
        try:
            user_input = listen()
            if user_input and user_input.strip():
                respond(user_input)
        except KeyboardInterrupt:
            print("\n[INFO] System shutting down")
            break
        except Exception as e:
            print(f"[ERROR] Main loop error: {e}")