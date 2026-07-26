import math
from datetime import datetime
from geopy.geocoders import Nominatim
import sqlite3
import requests
from geopy.exc import GeocoderServiceError
import threading
import sys
from pathlib import Path

base_fare = 36
rate = 18

GEOFABRIK_REGIONS = {
    "northern-zone": {
        "Delhi", "Haryana", "Punjab", "Himachal Pradesh",
        "Jammu and Kashmir", "Ladakh",
        "Uttarakhand", "Uttar Pradesh", "Chandigarh"
    },

    "western-zone": {
        "Rajasthan", "Gujarat",
        "Maharashtra", "Goa",
        "Dadra and Nagar Haveli and Daman and Diu"
    },

    "central-zone": {
        "Madhya Pradesh",
        "Chhattisgarh"
    },

    "eastern-zone": {
        "Bihar",
        "Jharkhand",
        "West Bengal",
        "Odisha",
        "Andaman and Nicobar Islands"
    },

    "north-eastern-zone": {
        "Assam",
        "Arunachal Pradesh",
        "Manipur",
        "Meghalaya",
        "Mizoram",
        "Nagaland",
        "Sikkim",
        "Tripura"
    },

    "southern-zone": {
        "Karnataka",
        "Kerala",
        "Tamil Nadu",
        "Andhra Pradesh",
        "Telangana",
        "Puducherry",
        "Lakshadweep"
    }
}

def location(location_name):
    conn = sqlite3.connect("locations.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS locations (name TEXT, latitude REAL, longitude REAL)")

    c.execute("SELECT latitude, longitude FROM locations WHERE name=?", (location_name,))
    result = c.fetchone()
    if result:
        conn.close()
        return result[0], result[1]

    try:
        geolocator = Nominatim(user_agent="auto_fare")
        loc = geolocator.geocode(location_name)
    except Exception:
        conn.close()
        print("Error: Unable to connect to the geocoding service. Please check your internet connection or try again later.")
        sys.exit()
        #return None, None


    if loc is None:
        conn.close()
        print("Error: Unable to connect to the geocoding service. Please check your internet connection or try again later.")
        sys.exit()

    c.execute("INSERT INTO locations VALUES (?, ?, ?)", (location_name, loc.latitude, loc.longitude))
    conn.commit()
    conn.close()
    return (loc.latitude, loc.longitude)

def fare(dist, time, wait, bag):
    global base_fare, rate
    multiplier = 1.5
    if dist >=2:
        distance_fare = (dist-2)* rate
    else:
        distance_fare = 0
    if bag >50:
        print("Maximum baggage weight exceeded. Please reduce the weight of your baggage.")
        return None
    if bag > 20:
        baggage_fare = (bag-20) * 10
    else:
        baggage_fare = 0
    if wait > 5:
        wait_fare = math.ceil(wait/15) * 10
    else:
        wait_fare = 0
    if time >=22 or time < 6:
        print("Night time travel fare applied.")
        travel_fare = (base_fare + distance_fare) * multiplier
    else:
        travel_fare = base_fare + distance_fare

    return f"Rs {travel_fare + baggage_fare + wait_fare}"

def find_region(lat, lon): #AI GENERATED FUNCTION

    try:
        geolocator = Nominatim(user_agent="my_state_finder_app")
        location = geolocator.reverse(f"{lat}, {lon}")

        if location and 'address' in location.raw:
            address = location.raw['address']
            # Fetch the state safely using the dict .get() method
            state = address.get('state', 'State not found')
            print(state)
            if state in GEOFABRIK_REGIONS["northern-zone"]:
                return "northern-zone"
            elif state in GEOFABRIK_REGIONS["western-zone"]:
                return "western-zone"
            elif state in GEOFABRIK_REGIONS["central-zone"]:
                return "central-zone"
            elif state in GEOFABRIK_REGIONS["eastern-zone"]:
                return "eastern-zone"
            elif state in GEOFABRIK_REGIONS["north-eastern-zone"]:
                return "north-eastern-zone"
            elif state in GEOFABRIK_REGIONS["southern-zone"]:
                return "southern-zone"
        else:
            return None

    except GeocoderServiceError as e:
        print("Please check your internet connection or try again later. \nState is being taken as southern-zone by default.")
        return "southern-zone" 

def find_state(lat, lon):

    try:
        geolocator = Nominatim(user_agent="my_state_finder_app")
        location = geolocator.reverse(f"{lat}, {lon}")

        if location and 'address' in location.raw:
            address = location.raw['address']
            state = address.get('state', 'State not found')
            return state

    except GeocoderServiceError as e:
        print("Please check your internet connection or try again later. \nState is being taken as Karnataka by default.")
        return "Karnataka" 

def download_map(region):
    if region not in GEOFABRIK_REGIONS:
        raise ValueError(f"Unknown Geofabrik region: {region}")

    url = f"https://download.geofabrik.de/asia/india/{region.lower()}-latest.osm.pbf"
    local_filename = f"{region.lower()}-latest.osm.pbf"
    try:
        with requests.get(url, stream=True, timeout=60) as response:
            response.raise_for_status()
            with open(local_filename, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
    except requests.exceptions.RequestException as e:
        print("Error downloading map data:")
        #print(e)
        return

def maps(origin, dest): 
    try:
        lat1, lon1 = origin
        lat2, lon2 = dest
        OSRM_URL = "https://router.project-osrm.org/route/v1/driving/"
        params = {
        "overview": "false",  # Exclude geometry string
        "steps": "true"       # Include step-by-step navigation instructions
    }

        response = requests.get(f"{OSRM_URL}{lon1},{lat1};{lon2},{lat2}", params=params)
        data = response.json()
        if response.status_code == 200:
            route = data['routes'][0]
            return route['distance'], route['duration']/60  # Convert duration from seconds to minutes
        else:
            raise Exception(f"Error querying OSRM server: {data.get('message')}")
    except Exception as e:
        print("Error in maps function:", str(e))
        if Path("southern-zone-latest.osm.pbf").exists():
            print("Using local map data for southern-zone.")
            return get_route("southern-zone-latest.osm.pbf", lat1, lon1, lat2, lon2)

if __name__ == "__main__":
    start = input("Enter your starting location: ")
    origin = location(start)
    destination = input("Enter your destination: ")
    travel_time = int(input("Enter your travel time (in minutes) \nIf unsure, enter 0 \nTravel time: "))
    weight = int(input("Enter the weight of your baggage (in kg): "))
    dest = location(destination)
    thread1 = threading.Thread(target=download_map, args=(find_region(origin[0], origin[1]),))
    #thread1.start()
    #print("Downloading map data in the background...")
    #thread1.join()  # Wait for the map download to complete before proceeding
    #print("Map data download completed.")
    location_distance, location_duration = maps(origin, dest)
    print("distance :", location_distance/1000)
    print("duration :", location_duration)
    if input("The default fare structure is for Bangalore,Karnataka,India\nWould u like to enter custom auto fare pricing details? (y/n) : ") == "y":
        base_fare = int(input("Enter base fare: "))
        rate = int(input("Enter rate of Rs per km: "))
    print(fare(location_distance/1000, datetime.now().hour, travel_time - location_duration if travel_time > location_duration else 0, weight))
