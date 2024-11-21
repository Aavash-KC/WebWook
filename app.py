from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# OpenWeatherMap API key and base URL
API_KEY = os.getenv("OPENWEATHERMAP_API_KEY", "1e71fdd19387e5fff63d1659da6ab297")  
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

@app.route("/", methods=["GET"])
def home():
    return jsonify({"student_number": "200573779"})  

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    # Extract parameters from Dialogflow request
    intent = data.get('queryResult', {}).get('intent', {}).get('displayName', '')
    parameters = data.get('queryResult', {}).get('parameters', {})
    city = parameters.get('geo-city') 
    
    # Fulfillment text
    fulfillment_text = ""

    if intent == "get_weather_update":
        # Fetch weather information using OpenWeatherMap API
        weather_response = get_weather(city)

        if weather_response:
            fulfillment_text = weather_response
        else:
            fulfillment_text = f"Sorry, I couldn't fetch the weather for {city}. Please try again later."

    return jsonify({"fulfillmentText": fulfillment_text})

def get_weather(city):
    try:
        # Construct the request URL with city and API key
        url = f"{BASE_URL}?q={city}&appid={API_KEY}&units=metric"

        # Send a GET request to OpenWeatherMap API
        response = requests.get(url)
        data = response.json()

        # Check if the response contains valid data
        if data.get('cod') != 200:
            return None  # If the city is not found or there's another issue

        # Extract relevant weather data
        weather_description = data['weather'][0]['description']
        temperature = data['main']['temp']
        city_name = data['name']

        return (
            f"The weather in {city_name} today is {weather_description} "
            f"with a current temperature of {temperature}°C."
        )

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return None

if __name__ == "__main__":
    app.run(debug=True)
