import json
import os
import requests
from decimal import Decimal, ROUND_HALF_UP

API_KEY = os.environ.get("OPENWEATHER_API_KEY")
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
DEFAULT_CITY = "Ottawa"

def lambda_handler(event, context):
    try:
        # Get the city from the query string parameters, default to "Ottawa" if not provided
        city = event.get("queryStringParameters", {}).get("city", DEFAULT_CITY)

        # Build the API request URL
        url = f"{BASE_URL}?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)

        # Check if the API request was successful
        if response.status_code != 200:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Failed to fetch weather data", "details": response.text})
            }

        # Parse the response JSON from OpenWeather API
        weather_data = response.json()
        temp = Decimal(str(weather_data["main"]["temp"])).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        condition = weather_data["weather"][0]["description"]

        # Return the weather data as a stringified JSON
        return {
            "statusCode": 200,
            "body": json.dumps({
                "location": city,
                "temperature": float(temp),
                "condition": condition
            })
        }

    except Exception as e:
        # In case of an error, return a 500 status code and error details as stringified JSON
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Lambda failed",
                "details": str(e)
            })
        }
