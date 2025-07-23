import os
import sys
import subprocess
import time
import vlc
import json
import speech_recognition as sr
import googletrans as Translator
import webbrowser
import requests
from urllib.parse import quote
from playsound import playsound
import pyaudio
import pyautogui
import pywhatkit as kit
import pvporcupine
import struct
import gtts
import geocoder
import eel
import threading
from engine.command import speak
from engine.config import ASSISTANT_NAME
from engine.helper import extract_yt_term,extract_ig_term,remove_words
from hugchat import hugchat
import google.generativeai as genai
import googletrans as gt
# api_key = "AIzaSyCrGKPhY0JzopMwyMc1nXAp3U-Xj5zKvHU"  # Replace with your actual API key
# genai.configure(api_key=api_key)
# model = genai.GenerativeModel("gemini-1.5-flash")

recognizer = sr.Recognizer()
player = None
song_playing = False
song_thread = None
stop_signal = False

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pyttsx3
import eel

stored_commands = {}
stored_web_commands = {}
stored_system_paths = {}
stored_chatbot_keys = {}
sp = None

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('voice', engine.getProperty('voices')[0].id)

def receiveLocalStorageData(data):
    global stored_commands, stored_web_commands, stored_system_paths, stored_chatbot_keys, sp

    # Initialize empty dictionaries
    stored_commands = {}
    stored_web_commands = {}
    stored_system_paths = {}
    stored_chatbot_keys = {}

    # Process phonebook data
    phonebook = data.get('Phonebook', [])
    for contact in phonebook:
        name = contact.get('name')
        number = contact.get('phoneNumber') or contact.get('number')
        if name and number:
            stored_commands[name] = number

    # Process websites data
    websites = data.get('Website', [])
    for site in websites:
        name = site.get('name')
        url = site.get('url')
        if name and url:
            stored_web_commands[name] = url

    # Process system paths data
    systempath = data.get('SystemPath', [])
    for path in systempath:
        name = path.get('name')
        path_value = path.get('path').strip('')
        if name and path_value:
            stored_system_paths[name] = path_value

    # Process chatbot keys
    chatbot_keys = data.get('ChatbotKeys', [])
    for key in chatbot_keys:
        if key.get('keyName') == 'chatbotkey':
            api_key = key.get('apiKey')
            if api_key:
                stored_chatbot_keys['chatbotkey'] = api_key
                # Configure genai dynamically
                print(f"Configuring genai with API key")
                try:
                    genai.configure(api_key=api_key)
                    global model
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    print("genai configured successfully.")
                except Exception as e:
                    print(f"Error configuring genai: {e}")
        
# Expose the function to JavaScript
eel.expose(receiveLocalStorageData)
    # Print updated stored data
    # print("Stored contacts:", stored_commands)
    # print("Stored web commands:", stored_web_commands)
    # print("Stored system paths:", stored_system_paths)
   
@eel.expose
def resource_path(relative_path):
    """Get the absolute path to a resource, works for both development and bundled executables."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def playAssistantSound():
    sound_path = resource_path("www/assets/audio/start_sound.mp3")
    
    # Play the sound asynchronously to avoid blocking other processes
    threading.Thread(target=playsound, args=(sound_path,), daemon=True).start()

@eel.expose
def findContact(query):
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'whatsapp', 'video']
    query = remove_words(query, words_to_remove).strip().lower()
    
    print(f"Processed query: '{query}'")  # Debugging line

    try:
        # Check if the query matches any contact name
        for name, mobile_no in stored_commands.items():
            if query in name.lower():
                mobile_number_str = str(mobile_no)
                if not mobile_number_str.startswith('+91'):
                    mobile_number_str = '+91' + mobile_number_str
                return mobile_number_str, name
        
        speak('Contact does not exist')
        return None, None

    except Exception as e:
        speak(f"Error: {e}")
        return None, None
 # Ensure your Eel frontend files are in the 'web' directory
def sing_a_song():
    global player, song_playing, song_thread, stop_signal

    # Stop any currently playing song
    if player:
        player.stop()

    song_url = 'D:\\pytho\\jarvis\\www\\assets\\audio\\song.mp3'

    # Define a function to play the song in a separate thread
    def play_song():
        global player, song_playing, stop_signal

        # Create the player and play the song
        player = vlc.MediaPlayer(song_url)
        player.play()
        song_playing = True
        stop_signal = False

        # Let the song play for a while
        time.sleep(5)  # Adjust this time as needed

        # # Prompt the user to stop or continue the song
        # eel.DisplayMessage("Would you like to stop the song or continue?")
        # speak("Would you like to stop the song or continue?")

        # Continuously check for "stop" command or song end
        while player.get_state() != vlc.State.Ended and not stop_signal:
            command = takecommand('en').lower()  # Simulating voice command
            if "stop" in command:
                stop_song()  # Stop the song if the user says "stop"
                break
            time.sleep(0.5)  # Pause before checking again

    # Create and start a new thread for playing the song
    song_thread = threading.Thread(target=play_song)
    song_thread.start()

# Define a function to stop the song
def stop_song():
    global player, song_playing, stop_signal

    if player and song_playing:
        player.stop()  # Stop the player
        song_playing = False
        stop_signal = True
        print("Song stopped.")
        speak("Song stopped Boss")

# The eel.DisplayMessage function should be connected to your UI.
# If you're just testing without the UI, you can mock it with a print statement.
def eel_DisplayMessage(message):
    print(message)

def takecommand(language='en'):
    # For now, you can simulate this with input for testing purposes
    return input(f"Enter command in {language}: ")
def PlayYoutube(query):
    search_term = extract_yt_term(query)
    speak("Playing " + search_term + " on YouTube")
    kit.playonyt(search_term)
def PlayInstagramReels(query):
    search_term = extract_ig_term(query)
    speak("Playing " + search_term + " on Instagram reels")
    url = f"https://www.instagram.com/reels/"
    webbrowser.open(url)
    print(f"Instagram reels search URL: {url}")

def hotword():
    porcupine = None
    paud = None
    audio_stream = None
    try:
        porcupine = pvporcupine.create(keywords=["jarvis", "alexa"])
        paud = pyaudio.PyAudio()
        audio_stream = paud.open(rate=porcupine.sample_rate, channels=1, format=pyaudio.paInt16, input=True, frames_per_buffer=porcupine.frame_length)
        
        while True:
            keyword = audio_stream.read(porcupine.frame_length)
            keyword = struct.unpack_from("h" * porcupine.frame_length, keyword)
            keyword_index = porcupine.process(keyword)

            if keyword_index >= 0:
                print("Hotword detected")
                pyautogui.hotkey('space')
                time.sleep(2)
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if porcupine:
            porcupine.delete()
        if audio_stream:
            audio_stream.close()
        if paud:
            paud.terminate()



def extract_contact_number(query):
    for name, mobile_no in stored_commands.items():
        if name.lower() in query.lower():
            return mobile_no
    return None  # Return None if no match is found

def extract_contact_name(query):
    for name in stored_commands.keys():
        if name.lower() in query.lower():
            return name
    return None  # Return None if no match is found



def process_whatsapp_action(query, language):
    contact_no = extract_contact_number(query)
    name = extract_contact_name(query)

    if "send message" in query:
        message = 'message'
        speak("What message to send?", language)
        query = takecommand(language)
        if not query:
            speak("No message provided.")
            return
    elif "call" in query:
        message = 'call'
    elif "video call" in query:
        message = 'video call'
    else:
        speak("Unknown action. Please specify whether to send a message, make a phone call, or start a video call.")
        return

    if not contact_no or not name:
        speak("Error: Missing contact information.")
        return

    whatsApp(contact_no, query, message, name)

def whatsApp(mobile_no, message, flag, name):
    

    if flag == 'message':
        target_tab = 13
        jarvis_message = "message send successfully to "+name

    elif flag == 'call':
        target_tab = 7
        message = ''
        jarvis_message = "calling to "+name

    else:
        target_tab = 6
        message = ''
        jarvis_message = "staring video call with "+name


    # Encode the message for URL
    encoded_message = quote(message)
    print(encoded_message)
    # Construct the URL
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"

    # Construct the full command
    full_command = f'start "" "{whatsapp_url}"'

    # Open WhatsApp with the constructed URL using cmd.exe
    subprocess.run(full_command, shell=True)
    time.sleep(5)
    subprocess.run(full_command, shell=True)
    
    pyautogui.hotkey('ctrl', 'f')

    for i in range(1, target_tab):
        pyautogui.hotkey('tab')

    pyautogui.hotkey('enter')
    speak(jarvis_message)

def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "").replace("open", "").strip().lower()
    try:
        if query in stored_system_paths:
            command_path = stored_system_paths[query]
            speak("Opening " + query)
            os.startfile(command_path)

        elif query in stored_web_commands:
            url = stored_web_commands[query]
            speak("Opening " + query)
            webbrowser.open(url)

        else:
            speak("Opening " + query)
            os.system('start ' + query)

    except Exception as e:
        speak("Something went wrong: " + str(e))

def load_cookies(file_path):
    with open(file_path, 'r') as file:
        cookies = json.load(file)
    return {cookie['name']: cookie['value'] for cookie in cookies}



def chatBot(query):
    try:
        # Ensure the query is not empty
        if not query.strip():
            error_message = "No relevant content extracted."
            print(error_message)
            speak(error_message)
            return error_message

        # Create a detailed query for better responses
        detailed_query = f"Please provide a response to the following query:\n\n{query}"

        # Generate content using the Gemini AI model
        response = model.generate_content([detailed_query])

        # Ensure response is a string and clean it up
        response_text = response.text if hasattr(response, 'text') else "No response received."
        response_text = response_text.replace('*', '')  # Remove asterisks if present

        # Print the response for debugging
        print(f"Chatbot response: {response_text}")

        # Speak the response
        speak(response_text)

        return response_text  # Return the cleaned response
    except Exception as e:
        # Handle errors during processing
        error_message = "Sorry, I encountered an issue while processing your request."
        print(f"An error occurred in chatbot: {e}")
        speak(error_message)
        return error_message



# def chatBot(query):
#     try:
#         user_input = query.lower()  # Convert the query to lowercase for consistency
#         chatbot = hugchat.ChatBot(cookie_path="engine\\cookie.json")
#         conversation_id = chatbot.new_conversation()  # Create a new conversation
#         chatbot.change_conversation(conversation_id)  # Switch to the new conversation
#         response = chatbot.chat(user_input)  # Get the chatbot's response
        
#         response_text = str(response)  # Ensure response is a string
#         response_text = response_text.replace('*', '')  # Remove asterisks from the response
        
#         print(f"Chatbot response: {response_text}")  # Print response for debugging
#         speak(response_text)  # Use the speak function to output the response
#         return response_text  # Return the response text

#     except Exception as e:
#         error_message = "Sorry, I encountered an issue while processing your request."
#         print(f"An error occurred in chatbot: {e}")  # Print error message for debugging
#         speak(error_message)  # Inform the user about the error
#         return error_message  # Return the error message

def makeCall(name, mobileNo):
    mobileNo = mobileNo.replace(" ", "")
    speak("Calling " + name)
    command = 'adb shell am start -a android.intent.action.CALL -d tel:' + mobileNo
    os.system(command)

def sendMessage(message, mobileNo, name):
    from engine.helper import replace_spaces_with_percent_s, goback, keyEvent, tapEvents, adbInput
    message = replace_spaces_with_percent_s(message)
    mobileNo = replace_spaces_with_percent_s(mobileNo)
    speak("Sending message")
    goback(4)
    time.sleep(1)
    keyEvent(3)
    tapEvents(136, 2220)
    tapEvents(819, 2192)
    adbInput(mobileNo)
    tapEvents(601, 574)
    tapEvents(390, 2270)
    adbInput(message)
    tapEvents(957, 1546)
    speak("Message sent successfully to " + name)

