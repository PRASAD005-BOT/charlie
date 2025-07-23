import pyttsx3
import speech_recognition as sr
import gtts
import vlc
from googletrans import Translator
import eel
import threading
import time
import google.generativeai as genai

# # Configure the API key for Gemini AI
# api_key = "AIzaSyCrGKPhY0JzopMwyMc1nXAp3U-Xj5zKvHU"
# genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Initialize recognizer and translator
recognizer = sr.Recognizer()
translator = Translator()
stored_chatbot_keys={}
# Global variable to store the current language
current_language = 'en-IN'
should_exit = False

# Initialize eel
# eel.init('web')  # Ensure you have a 'web' folder with your HTML/JS files
def receiveLocalStorageData(data):
    global stored_chatbot_keys
    stored_chatbot_keys = {}
    chatbot_keys = data.get('ChatbotKeys', [])
    for key in chatbot_keys:
        if key.get('keyName') == 'chatbotkey':
            api_key = key.get('apiKey')
            if api_key:
                stored_chatbot_keys['chatbotkey'] = api_key

                # Configure genai dynamically
                print(f"Configuring genai with API key: ")
                try:
                    genai.configure(api_key=api_key)
                except Exception as e:
                    print(f"Error configuring genai: {e}")
def speak(text, language='en-IN'):
    """Generate speech from text and play it."""
    try:
        tts = gtts.gTTS(text, lang=language.split('-')[0])
        tts.save("response.mp3")
        player = vlc.MediaPlayer("response.mp3")
        player.play()
        while player.get_state() != vlc.State.Ended:
            time.sleep(0.1)
    except Exception as e:
        print(f"An error occurred while speaking: {e}")

def take_voice_command(language=None):
    """Take a voice command from the user."""
    if language is None:
        language = current_language

    with sr.Microphone() as source:
        eel.DisplayMessage("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        query = recognizer.recognize_google(audio, language=language)
        eel.DisplayMessage(f"User said: {query}")
        print(f"User said: {query}")
        return query
    except sr.UnknownValueError:
        eel.DisplayMessage("Sorry, I did not understand that.")
        print("Sorry, I did not understand that.")
        return ""
    except sr.RequestError:
        eel.DisplayMessage("Could not request results from Google Speech Recognition service.")
        print("Could not request results from Google Speech Recognition service.")
        return ""

def ask_language():
    """Ask the user to select a language."""
    global current_language
    eel.DisplayMessage("Select your language: English, Hindi, Telugu, or Tamil.")
    speak("Select your language: English, Hindi, Telugu, or Tamil.", language='en-IN')
    language = take_voice_command().lower()
    if 'hindi' in language:
        current_language = 'hi-IN'
    elif 'telugu' in language:
        current_language = 'te-IN'
    elif 'tamil' in language:
        current_language = 'ta-IN'
    else:
        current_language = 'en-IN'
    eel.DisplayMessage(f"Language selected: {current_language}")

def translate_to_english(text, src_language):
    """Translate text to English."""
    return translator.translate(text, src=src_language, dest='en').text

def translate_text(text, dest_language):
    """Translate text to the target language."""
    return translator.translate(text, dest=dest_language).text

def process_chatbot_response(response, language):
    """Process the chatbot response and speak/display it in the selected language."""
    if language != 'en-IN':
        translated_response = translate_text(response, language.split('-')[0])
        eel.DisplayMessage(f"Translated response: {translated_response}")
        print(f"Translated response: {translated_response}")
        speak(translated_response, language)
    else:
        eel.DisplayMessage(f"Response: {response}")
        print(f"Response: {response}")
        speak(response, language)

def chatBot(query):
    """Chatbot response using Gemini AI."""
    try:
        if not query.strip():
            error_message = "No relevant content extracted."
            eel.DisplayMessage(error_message)
            print(error_message)
            speak(error_message)
            return error_message

        detailed_query = f"Please provide a  response to the following query:\n\n{query}"
        response = model.generate_content([detailed_query])
        response_text = response.text if hasattr(response, 'text') else "No response received."
        response_text = response_text.replace('*', '')
        eel.DisplayMessage(f"Chatbot response: {response_text}")
        print(f"Chatbot response: {response_text}")
        return response_text
    except Exception as e:
        error_message = "Sorry, I encountered an issue while processing your request."
        eel.DisplayMessage(error_message)
        print(f"An error occurred in chatbot: {e}")
        speak(error_message)
        return error_message

@eel.expose
def process_command(language='en-IN'):
    """Process user commands based on the selected language."""
    global should_exit
    query = take_voice_command(language)
    if query:
        eel.DisplayMessage(f"Processing command in {language}: {query}")
        print(f"Processing command in {language}: {query}")
        if language != 'en-IN':
            translated_query = translate_to_english(query, language.split('-')[0])
        else:
            translated_query = query

        if "exit" in translated_query.lower():
            eel.DisplayMessage("Exiting to run other commands.")
            speak("Exiting to run other commands.")
            should_exit = True
            return True

        if "change language" in translated_query.lower():
            ask_language()
            return False

        response = chatBot(translated_query)
        process_chatbot_response(response, language)
    else:
        eel.DisplayMessage(f"No command received in {language}.")
        print(f"No command received in {language}.")
    return False

def command_thread():
    """Run the command processing loop."""
    global should_exit
    while not should_exit:
        print(f"Waiting for a voice command in {current_language}...")
        eel.DisplayMessage(f"Waiting for a voice command in {current_language}...")
        if process_command(current_language):
            break

def language():
    """Ask the user for their language preference and start processing commands."""
    ask_language()
    command_thread_handle = threading.Thread(target=command_thread)
    command_thread_handle.start()
    command_thread_handle.join()

# Start the application
# eel.start('index.html', block=False)
# language()
