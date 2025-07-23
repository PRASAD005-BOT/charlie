import eel
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
from engine.alaram import alarm
from engine.language import *
from engine.Googlemaps import navigate_to_place, show_location_on_map
from engine.schedule_module import schedule
from engine.spotify import control_spotify
from engine.powerpoint import powerpoint
from engine.weather import main
from engine.subway import subway
from engine.steering2 import *
# Initialize Eel for UI interface
eel.init('web')

# Set Chrome as the default web browser


sing_a_song_active = False
google_maps_active = False
user_location = None  # Assuming user_location will be set elsewhere in your code
language_change_active = False

def speak(text, language='en'):
    try:
        engine = pyttsx3.init('sapi5')
        voices = engine.getProperty('voices') 
        engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', 174)
        eel.DisplayMessage(text)
        engine.say(text)
        eel.receiverText(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error in speak function: {e}")

def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('Listening...')
        eel.DisplayMessage('Listening...')
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        
        try:
            audio = r.listen(source, timeout=10, phrase_time_limit=6)  # Adjust timeout as needed
        except Exception as e:
            print(f"Error during listening: {e}")
            return ""

    try:
        print('Recognizing...')
        eel.DisplayMessage('Recognizing...')
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}")
        eel.DisplayMessage(query)
        return query
    except sr.UnknownValueError:
        speak("Sorry, I couldn't understand that. Please try again.")
        return ""
    except sr.RequestError as e:
        speak("There seems to be an issue with the speech recognition service.")
        return ""
    except Exception as e:
        print(f"An error occurred during recognition: {e}")
        return ""

@eel.expose
def wish_me():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Good Morning Boss")
    elif hour >= 12 and hour < 18:
        speak("Good Afternoon Boss")
    else:
        speak('Good Evening Boss')

@eel.expose
def allCommands(message=1):
    global google_maps_active, language_change_active, sing_a_song_active
    wish_me()
    while True:
        if language_change_active:
            speak("Language change is currently active. Please wait until the process is complete.")
            continue  # Keep waiting if language change is active

        # Get the command from user input or use the provided message
        if message == 1:
            query = takecommand()
            print(query)
            eel.senderText(query)
        else:
            query = message
            eel.senderText(query)

        try:
            if query and isinstance(query, str):
                query = query.lower()  # Convert to lowercase to normalize commands
                from engine.features import findContact, whatsApp, makeCall, openCommand, PlayInstagramReels, PlayYoutube, sing_a_song, stop_song,sendMessage
                # if "image scanner" in query:
                #     # Open the Flask application in a web browser (change the port if needed)
                #     speak("Opening scanner for document upload.")
                #     webbrowser.open("http://localhost:5000/")
                if "play games" in query:
                    speak("Would you like to play a running game or a driving game?")
                    game_type = takecommand().lower()
                    
                    if "running" in game_type:
                        speak("Which running game would you like to play? Subway Surfers or Temple Run?")
                        running_game = takecommand().lower()
                        if "subway surfers" in running_game:
                            webbrowser.open("https://poki.com/en/g/subway-surfers")
                            speak("Activating virtual controls for Subway Surfers...")
                            speak("Enjoy your game, boss!")
                            subway()
                              # Activate Subway Surfers virtual controls
                              # Apply any additional mask function you may have
                            
                        elif "temple run" in running_game:
                            webbrowser.open("https://poki.com/en/g/temple-run-2")
                            speak("Activating virtual controls for Temple Run...")
                            speak("Enjoy your game, boss!")
                            subway()  # Activate Temple Run virtual controls (same function used here, can be customized)
                              # Apply mask function
                            
                        else:
                            speak("Sorry, I didn't understand which game you want to play. Please try again.")
                    
                    elif "driving" in game_type:
                        webbrowser.open("https://poki.com/en/g/mr-racer-car-racing")
                        speak("Activating virtual driving controls...")
                        speak("Enjoy your game, boss!")
                        steering_control()# Add any additional functions for driving controls if required
                        
                    
                    else:
                        speak("I couldn't understand your choice. Please say running or driving.")

                if "location" in query:
                    if "my location" in query:
                        if user_location:
                            show_location_on_map(user_location)
                            speak("Here is your current location.")
                        else:
                            speak("Sorry, I couldn't retrieve your current location. Please enable location services.")
                    else:
                        speak("Which location would you like to see?")
                        location_name = takecommand()
                        if location_name:
                            show_location_on_map(location_name)
                            speak(f"Here is the location for {location_name}.")
                        else:
                            speak("Sorry, I didn't catch the location name. Please try again.")
                        
                    
                    
                elif 'schedule on' in query:
                    for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                        if day in query:
                            schedule(day)
                            break
                    else:
                        speak("Sorry, I didn't catch which day you meant.")
                
                elif "open" in query:
                    openCommand(query)

                elif "on youtube" in query:
                    PlayYoutube(query)

                elif "on instagram" in query:
                    PlayInstagramReels(query)

                elif "sing a song" in query:
                    sing_a_song()  # Invoke the sing_a_song function properly
                    sing_a_song_active = True
                
                elif "stop the song" in query and sing_a_song_active:
                    stop_song()  # Properly invoke stop_song function
                    sing_a_song_active = False
                
                elif "set an alarm" in query:
                    alarm()

                elif 'play music' in query:
                    speak('What would you like to play?')
                    music_command = takecommand()
                    if music_command:
                        response = control_spotify(music_command)
                        speak(response)
                    else:
                        speak("Sorry, I didn't catch that. Please try again.")
                        
                elif 'change language' in query:
                    speak('Starting language change process...')
                    language_change_active = True
                    language()  # This should handle the language change process
                    language_change_active = False  # Set back to False when done

                elif "navigate to" in query:
                    place = query.replace("navigate to", "").strip()
                    if place:
                        navigated_location = navigate_to_place(place)
                        if navigated_location:
                            google_maps_active = True
                            speak(f"Navigating to {place}.")
                        else:
                            google_maps_active = False
                            speak(f"Sorry, I couldn't navigate to {place}. Please check the location and try again.")
                    else:
                        speak("Sorry, I didn't catch the place name. Please try again.")

                elif "send message" in query or "phone call" in query or "video call" in query:
                    contact_no, name = findContact(query)
                    if contact_no:
                        speak("Which mode do you want to use: WhatsApp or mobile?")
                        preference = takecommand().lower()
                        if "mobile" in preference:
                            if "send message" in query:
                                speak("What message to send?")
                                message_text = takecommand()
                                sendMessage(message_text, contact_no, name)
                            elif "phone call" in query:
                                makeCall(name, contact_no)
                        elif "whatsapp" in preference:
                            if "send message" in query:
                                speak("What message to send?")
                                message_text = takecommand()
                                whatsApp(contact_no, message_text, 'message', name)
                            elif "phone call" in query:
                                whatsApp(contact_no, '', 'call', name)
                            elif "video call" in query:
                                whatsApp(contact_no, '', 'video call', name)
                        else:
                            speak("Invalid preference. Please specify either WhatsApp or mobile.")
                    else:
                        speak("Contact not found. Please try again.")

                elif 'your master' in query:
                    speak('Prasadengineer is my master. He is running me right now.')
                elif 'search in google' in query:
                    speak('What do you want to search for?')
                    search = takecommand()  
                    if search:
                        url = f'https://google.com/search?q={search}'  
                        webbrowser.open_new_tab(url) 
                    speak(f'Here is what I found for {search}')

                elif "tell weather" in query:
                    main()
                elif "powerpoint generator" in query:
                    powerpoint() 
                
                elif 'your name' in query:
                    speak('My name is Charlie.')

                elif 'who made you' in query:
                    speak('I was created by my AI master in 2024.')

                elif "exit" in query:
                    if language_change_active:
                        speak("Language change is currently active. Please wait until the process is complete before exiting.")
                    else:
                        speak("Exiting the application.")
                        eel.ShowHood()  # Navigate back to the home screen or main view
                        break  # Exit the loop, stop listening for commands

                else:
                    from engine.features import chatBot
                    chatBot(query)  # Fallback to chatbot for unrecognized commands

        except Exception as e:
            print(f"An error occurred: {e}")
            speak("An error occurred. Please try again later.")
            eel.ShowHood()


