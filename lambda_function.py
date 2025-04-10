import json
import boto3
import requests
import os
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

# AWS setup
dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")

# Config
API_KEY = os.environ.get("OPENWEATHER_API_KEY")
SUBSCRIPTION_TABLE = "UserSubscriptions"
WEATHER_TABLE = "WeatherData"
SNS_TOPIC_ARN = "arn:aws:sns:ca-central-1:340752826531:WeatherAlerts"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

def lambda_handler(event, context):
    try:
        subs_table = dynamodb.Table(SUBSCRIPTION_TABLE)
        weather_table = dynamodb.Table(WEATHER_TABLE)

        # Get all subscribed users
        subs = subs_table.scan().get("Items", [])

        if not subs:
            return {
                "statusCode": 200,
                "body": json.dumps("No user subscriptions found.")
            }

        for sub in subs:
            email = sub.get("email")
            city = sub.get("city", "Ottawa")  # Fallback if city not provided

            # Fetch weather from OpenWeather
            url = f"{BASE_URL}?q={city}&appid={API_KEY}&units=metric"
            response = requests.get(url)

            if response.status_code != 200:
                continue  # Skip this user if weather fetch fails

            weather_data = response.json()
            temp_str = str(weather_data["main"]["temp"])
            temperature = Decimal(temp_str).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
            condition = weather_data["weather"][0]["description"]
            timestamp = datetime.utcnow().isoformat()

            # Store in WeatherData table
            weather_table.put_item(Item={
                "location": city,
                "timestamp": timestamp,
                "temperature": temperature,
                "condition": condition
            })

            # Check for alert-worthy conditions (including "few clouds")
            severe_keywords = [
                "thunderstorm", "storm", "snow", "heavy snow", "heavy rain",
                "extreme", "tornado", "hurricane", "hail", "sleet", "few clouds"
            ]
            condition_lower = condition.lower()
            should_alert = (
                temperature > Decimal(35) or
                temperature < Decimal(-10) or
                any(severe in condition_lower for severe in severe_keywords)
            )

            # Send alert if needed
            if should_alert:
                alert_message = (
                    f"⚠️ Severe Weather Alert for {city}!\n"
                    f"Condition: {condition}, Temp: {temperature}°C"
                )
                sns.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Message=alert_message,
                    Subject=f"🚨 Weather Alert for {city}"
                )

        return {
            "statusCode": 200,
            "body": json.dumps("Automated weather check completed.")
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Lambda function failed",
                "details": str(e)
            })
        }
