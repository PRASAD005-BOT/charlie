import eel
import webbrowser

# Initialize global variables
user_location = None
google_maps_active = False

# Function to open Google Maps for navigation
def navigate_to_place(place):
    base_url = "https://www.google.com/maps/dir/?api=1"
    destination = place.replace(' ', '+')
    map_url = f"{base_url}&destination={destination}"
    webbrowser.open(map_url)
    return f"Navigating to {place}."

# Exposed function to be called from JavaScript for navigation
@eel.expose
def start_navigation(place):
    global google_maps_active
    google_maps_active = True
    return navigate_to_place(place)

# Function to stop navigation
@eel.expose
def stop_navigation():
    global google_maps_active
    google_maps_active = False
    return "Navigation stopped."

# Function to update the user's current location dynamically
@eel.expose
def update_user_location(latitude, longitude):
    global user_location
    if -90 <= latitude <= 90 and -180 <= longitude <= 180:
        user_location = (latitude, longitude)
        print(f"User location updated to: Latitude {latitude}, Longitude {longitude}")
        return f"User location updated to: Latitude {latitude}, Longitude {longitude}"
    else:
        return "Invalid latitude or longitude values."

# Function to provide the current location if asked
@eel.expose
def get_current_location():
    if user_location:
        return f"Your current location is: Latitude {user_location[0]}, Longitude {user_location[1]}"
    else:
        return "Location is not available."

# Function to show a specific location on the map
@eel.expose
def show_location_on_map(location):
    google_maps_url = "https://www.google.com/maps/search/?api=1&query="
    formatted_location = location.replace(" ", "+")
    map_url = google_maps_url + formatted_location
    webbrowser.open(map_url)
    return f"Showing location: {location}."

