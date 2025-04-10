import json
import boto3
import requests
import os
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

# Initialize AWS services
dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")

# Environment variables and constants
API_KEY = os.environ.get("OPENWEATHER_API_KEY")
DEFAULT_CITY = "Ottawa" # Default city/Will be overwritten accroding to users input
SNS_TOPIC_ARN = "arn:aws:sns:ca-central-1:340752826531:WeatherAlerts"
DYNAMODB_TABLE = "WeatherData"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

def lambda_handler(event, context):
    try:
        # Get city from query string, fallback to default
        city = event.get("queryStringParameters", {}).get("city", DEFAULT_CITY)

        # Fetch weather data from OpenWeather API
        url = f"{BASE_URL}?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)

        if response.status_code != 200:
            return {
                "statusCode": response.status_code,
                "body": json.dumps({
                    "error": "Failed to fetch weather data",
                    "details": response.text
                })
            }

        # Parse response safely using Decimal
        weather_data = response.json()
        temp_str = str(weather_data["main"]["temp"])
        temperature = Decimal(temp_str).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        condition = weather_data["weather"][0]["description"]
        timestamp = datetime.utcnow().isoformat()

        # Store to DynamoDB – KEEP temperature as Decimal
        table = dynamodb.Table(DYNAMODB_TABLE)
        table.put_item(Item={
            "location": city,
            "timestamp": timestamp,
            "temperature": temperature,
            "condition": condition
        })

        # Determine if alert should be triggered
        severe_keywords = [
            "thunderstorm", "storm", "snow", "heavy snow", "heavy rain",
            "extreme", "tornado", "hurricane", "hail", "sleet"
        ]
        condition_lower = condition.lower()
        should_alert = (
            temperature > Decimal(35) or
            temperature < Decimal(-10) or
            any(severe in condition_lower for severe in severe_keywords)
        )

        # If severe, publish alert
        if should_alert:
            alert_message = f"⚠️ Severe Weather Alert for {city}!\nCondition: {condition}, Temp: {temperature}°C"
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=alert_message,
                Subject="🚨 Weather Alert"
            )

        # Return response to frontend (safe to convert to float here)
        return {
            "statusCode": 200,
            "body": json.dumps({
                "temperature": float(temperature),
                "condition": condition,
                "location": city,
                "alert_sent": should_alert
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Lambda function failed",
                "details": str(e)
            })
        }
