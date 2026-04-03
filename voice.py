import speech_recognition as sr
import os
import requests
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


# =========================
# GREETINGS (INSTANT MATCH)
# =========================
GREETINGS = ["hello", "hi", "hey", "good morning", "good afternoon"]

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
        recognizer.adjust_for_ambient_noise(source, duration=0.3)

        try:
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=6)
        except:
            return ""

    try:
        text = recognizer.recognize_google(audio)
        print("User:", text)
        return text.lower()
    except:
        return ""


# =========================
# GREETING CHECK (FAST)
# =========================
def check_greeting(user_input):
    for word in GREETINGS:
        if word in user_input:
            return "Hello! How can I assist you today?"
    return None


# =========================
# FAQ MATCH (FAST)
# =========================
def match_faq(user_input):
    match, score, _ = process.extractOne(
        user_input,
        list(FAQ.keys()),
        scorer=fuzz.token_sort_ratio
    )

    if score > 70:
        return FAQ[match]

    return None


# =========================
# AI FALLBACK (OPENROUTER)
# =========================
def ask_ai(question):
    if not API_KEY:
        return "API key not configured."

    try:
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
            }
        )

        data = response.json()

        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        else:
            return data.get("error", {}).get("message", "AI error occurred.")

    except Exception as e:
        return f"System error: {str(e)}"


# =========================
# MAIN RESPONSE ENGINE
# =========================
def respond(user_input):

    # 1. Greeting (instant)
    greeting = check_greeting(user_input)
    if greeting:
        speak(greeting)
        return

    # 2. FAQ (fast)
    faq = match_faq(user_input)
    if faq:
        speak(faq)
        return

    # 3. AI fallback (smart)
    ai_response = ask_ai(user_input)
    speak(ai_response)


# =========================
# MAIN LOOP
# =========================
if __name__ == "__main__":
    speak("System ready. How can I help you?")
    
    while True:
        user_input = listen()
        if user_input:
            respond(user_input)