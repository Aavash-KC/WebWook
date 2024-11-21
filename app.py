from flask import Flask, request, jsonify
import python_weather
import asyncio
from datetime import datetime

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"student_number": "12345678"})  # Replace with your student number

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    # Extract parameters from Dialogflow request
    intent = data.get('queryResult', {}).get('intent', {}).get('displayName', '')
    parameters = data.get('queryResult', {}).get('parameters', {})
    city = parameters.get('geo-city', 'Barrie')  # Default to "Barrie" if no city is provided
    date_time = parameters.get('date-time', None)
    
    # Fulfillment text
    fulfillment_text = ""

    if intent == "get_weather_update":
        # Handle async call to fetch weather
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        weather_response = loop.run_until_complete(get_weather(city))
        loop.close()

        if weather_response:
            fulfillment_text = weather_response
        else:
            fulfillment_text = f"Sorry, I couldn't fetch the weather for {city}. Please try again later."

    return jsonify({"fulfillmentText": fulfillment_text})

async def get_weather(city):
    try:
        async with python_weather.Client() as client:
            # Fetch weather information
            weather = await client.get(city)

            # Fetch today's weather details
            today = datetime.now().date()
            for forecast in weather.forecasts:
                if forecast.date.date() == today:
                    description = forecast.sky_text
                    temp = forecast.temperature
                    return (
                        f"The weather in {city} today is {description.lower()} "
                        f"with a current temperature of {temp}°C."
                    )
            return f"No specific forecast found for {city} today."
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return None

if __name__ == "__main__":
    app.run(debug=True)
