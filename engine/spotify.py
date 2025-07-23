import pyttsx3
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import speech_recognition as sr
import webbrowser
import time
import os
import eel
import threading

stored_chatbot_keys = {}
sp = None

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('voice', engine.getProperty('voices')[0].id)

def spotify(data):
    global stored_chatbot_keys
    stored_chatbot_keys = {}
    chatbot_keys = data.get('ChatbotKeys', [])
    for key in chatbot_keys:
        if key.get('keyName') == 'spotifyid':
            api_key = key.get('apiKey')
            if api_key:
                stored_chatbot_keys['spotifyid'] = api_key
        elif key.get('keyName') == 'secretid':
            secret_id = key.get('apiKey')
            if secret_id:
                stored_chatbot_keys['secretid'] = secret_id

    # Initialize Spotipy
    SPOTIPY_CLIENT_ID = stored_chatbot_keys.get('spotifyid')
    SPOTIPY_CLIENT_SECRET = stored_chatbot_keys.get('secretid')
    SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'
    SCOPE = 'user-library-read user-read-playback-state user-modify-playback-state user-read-currently-playing'

    if SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET:
        global sp
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI,
            scope=SCOPE
        ))
        print("spotify connected")
    else:
        print("Spotify credentials are missing.")

# Expose the function to JavaScript
eel.expose(spotify)

def speak_and_print(text: str) -> None:
    """Function to speak out and print the given text."""
    print(text)
    engine.say(text)
    engine.runAndWait()

def open_spotify() -> None:
    """Function to open Spotify in the web browser."""
    webbrowser.open('https://open.spotify.com')
    time.sleep(10)  # Wait for Spotify to open

def get_song_name() -> str:
    """Function to prompt for a song name and return it."""
    speak_and_print("Please say the name of the song you'd like to play.")
    return listen_for_commands()

def get_playlist_choice() -> str:
    """Prompt the user to choose between a specific playlist or their saved playlist."""
    speak_and_print("Would you like to play a specific playlist by name or your saved playlists?")
    response = listen_for_commands().lower()
    if 'specific' in response:
        return 'specific'
    elif 'my playlist' in response or 'saved' in response:
        return 'saved'
    else:
        speak_and_print("I didn't catch that. Please say 'specific playlist' or 'my playlist'.")
        return get_playlist_choice()

def control_spotify(command: str) -> None:
    """Function to control Spotify playback based on the command."""
    command = command.lower()  # Convert command to lowercase for uniformity
    print(f"Processing command: {command}")

    # Get available devices
    devices = sp.devices()
    if not devices['devices']:
        speak_and_print("No Spotify devices found. Opening Spotify in the browser.")
        open_spotify()
        devices = sp.devices()  # Re-check devices after opening Spotify
        if not devices['devices']:
            speak_and_print("Still no Spotify devices found. Please ensure Spotify is running.")
            return

    device_id = devices['devices'][0]['id']  # Use the first available device

    try:
        if 'play' in command:
            if 'playlist' in command:
                choice = get_playlist_choice()  # Get the user's choice

                if choice == 'specific':
                    playlist_name = get_song_name().strip()  # Prompt for the playlist name
                    print(f"Searching for playlist: {playlist_name}")
                    results = sp.search(q=playlist_name, type='playlist', limit=1)
                    if results['playlists']['items']:
                        playlist_id = results['playlists']['items'][0]['id']
                        sp.start_playback(context_uri=f'spotify:playlist:{playlist_id}', device_id=device_id)
                        speak_and_print(f"Playing playlist: {playlist_name}")
                        check_playlist_progress(device_id)  # Start checking the playlist progress after playback starts
                    else:
                        speak_and_print(f"Playlist {playlist_name} not found.")
                elif choice == 'saved':
                    results = sp.current_user_playlists(limit=1)
                    if results['items']:
                        playlist_id = results['items'][0]['id']
                        sp.start_playback(context_uri=f'spotify:playlist:{playlist_id}', device_id=device_id)
                        speak_and_print(f"Playing your saved playlist.")
                        check_playlist_progress(device_id)  # Start checking the playlist progress after playback starts
                    else:
                        speak_and_print("No saved playlists found.")
            elif 'song' in command:
                song_name = get_song_name().strip()  # Prompt for song name
                print(f"Searching for song: {song_name}")
                results = sp.search(q=song_name, type='track', limit=1)
                if results['tracks']['items']:
                    track_id = results['tracks']['items'][0]['id']
                    sp.start_playback(uris=[f'spotify:track:{track_id}'], device_id=device_id)
                    speak_and_print(f"Playing song: {song_name}")
                    check_song_progress(device_id)  # Start checking the song progress after playback starts
                else:
                    speak_and_print(f"Song {song_name} not found.")
            else:
                sp.start_playback(device_id=device_id)
                speak_and_print("Playback started.")
                check_playlist_progress(device_id)  # Start checking the playlist progress after playback starts
        elif 'pause' in command:
            sp.pause_playback(device_id=device_id)
            speak_and_print("Playback paused.")
        elif 'stop' in command:
            sp.pause_playback(device_id=device_id)  # No direct stop method, so pausing playback.
            speak_and_print("Playback stopped.")
        elif 'next somebody' in command:
            sp.next_track(device_id=device_id)
            speak_and_print("Playing next track.")
        elif 'previous somebody' in command:
            sp.previous_track(device_id=device_id)
            speak_and_print("Playing previous track.")
        elif 'resume' in command:
            sp.start_playback(device_id=device_id)
            speak_and_print("Resuming playback.")
            
        else:
            speak_and_print("Sorry, I didn't understand that command.")
    except Exception as e:
        speak_and_print("An error occurred while processing your request.")
        print(f"Error: {e}")

def check_song_progress(device_id):
    """Check the song's progress, pause at 30 seconds, and prompt for further commands."""
    while True:
        playback = sp.current_playback()
        if playback and playback['is_playing']:
            progress_ms = playback['progress_ms']
            if progress_ms >= 30000:  # 30 seconds in milliseconds
                sp.pause_playback(device_id=device_id)  # Pause the song at 30 seconds
                speak_and_print("30 seconds have passed. Do you want to perform another action?")
                response = listen_for_commands()
                if 'yes buddy' in response.lower():
                    speak_and_print("Okay, what would you like to do?")
                    query = listen_for_commands()
                    control_spotify(query)
                else:
                    speak_and_print("Continuing with the current song.")
                    sp.start_playback(device_id=device_id)  # Resume playback
                break
        time.sleep(1)

def check_playlist_progress(device_id):
    """Check the playlist's progress, pause after 40 seconds, and prompt for further commands."""
    while True:
        playback = sp.current_playback()
        if playback and playback['is_playing']:
            progress_ms = playback['progress_ms']
            if progress_ms >= 40000:  # 40 seconds in milliseconds
                sp.pause_playback(device_id=device_id)  # Pause the song at 40 seconds
                speak_and_print("40 seconds have passed. Do you want to perform another action?")
                response = listen_for_commands()
                if 'yes buddy' in response.lower():
                    speak_and_print("Okay, what would you like to do?")
                    query = listen_for_commands()
                    control_spotify(query)
                else:
                    speak_and_print("Continuing with the current playlist.")
                    sp.start_playback(device_id=device_id)  # Resume playback
                break
        time.sleep(1)
        

def listen_for_commands() -> str:
    """Function to listen for commands using the microphone."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command
        except sr.UnknownValueError:
            speak_and_print("Sorry, I didn't understand. Please repeat the command.")
            return ""
        except sr.RequestError:
            speak_and_print("Sorry, there was an issue with the request.")
            return ""

if __name__ == "__main__":
    try:
        speak_and_print("Hello, I'm Buddy. I'm now listening for your commands.")
        while True:
            query = listen_for_commands()
            if query:
                control_spotify(query)
    except KeyboardInterrupt:
        print("Program stopped by user.")
        speak_and_print("Program stopped by user.")