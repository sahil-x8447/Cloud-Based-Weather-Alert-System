import tkinter as tk
from tkinter import messagebox
import requests
import boto3
import json

# AWS Setup
sns = boto3.client("sns", region_name="ca-central-1")
dynamodb = boto3.resource("dynamodb", region_name="ca-central-1")
SNS_TOPIC_ARN = "arn:aws:sns:ca-central-1:340752826531:WeatherAlerts"

# Lambda API URLs
REALTIME_WEATHER_URL = "https://fuey7peaej.execute-api.ca-central-1.amazonaws.com/weather"
ALERT_WEATHER_URL = "https://2zl99t62q4.execute-api.ca-central-1.amazonaws.com/WeatherAlertFunction"

# GUI Setup
root = tk.Tk()
root.title("☁️ Weather Alert System")
root.geometry("550x520")
root.configure(bg="#e6f2ff")

# Title
tk.Label(root, text="☁️ Cloud Weather Alert System", font=("Helvetica", 20, "bold"), bg="#e6f2ff", fg="#003366").pack(pady=15)

# Email Input
tk.Label(root, text="📧 Enter Your Email (optional):", bg="#e6f2ff", font=("Helvetica", 12)).pack()
email_var = tk.StringVar()
tk.Entry(root, textvariable=email_var, width=40, font=("Helvetica", 12)).pack(pady=5)

# City Input
tk.Label(root, text="🏙️ Enter Your City:", bg="#e6f2ff", font=("Helvetica", 12, "bold")).pack()
city_var = tk.StringVar()
tk.Entry(root, textvariable=city_var, width=40, font=("Helvetica", 12)).pack(pady=5)

# Weather display label
weather_display = tk.StringVar()
weather_label = tk.Label(
    root,
    textvariable=weather_display,
    wraplength=450,
    bg="#ffffff",
    font=("Helvetica", 12),
    relief="solid",
    bd=1,
    padx=10,
    pady=10
)

# ✅ Function to check real-time weather (Lambda v2)
def check_weather():
    city = city_var.get().strip()

    if not city:
        messagebox.showerror("Input Error", "Please enter a city.")
        return

    try:
        response = requests.get(f"{REALTIME_WEATHER_URL}?city={city}")
        try:
            raw_data = response.json()
        except json.JSONDecodeError:
            raise Exception("Empty or invalid response from real-time Lambda.")

        if isinstance(raw_data, str):
            data = json.loads(raw_data)
        elif "body" in raw_data and isinstance(raw_data["body"], str):
            data = json.loads(raw_data["body"])
        else:
            data = raw_data

        temp = data.get("temperature")
        cond = data.get("condition")
        loc = data.get("location")

        location_display = loc.title() if loc else "Unknown"
        condition_display = cond.title() if cond else "Unavailable"
        temperature_display = f"{temp}°C" if temp is not None else "Unavailable"

        if not weather_label.winfo_ismapped():
            weather_label.pack(pady=20)

        weather_display.set(
            f"✅ Weather in {location_display}:\n"
            f"🌡 Temperature: {temperature_display}\n"
            f"☁️ Condition: {condition_display}"
        )

    except Exception as e:
        if not weather_label.winfo_ismapped():
            weather_label.pack(pady=20)
        weather_display.set(f"⚠️ Failed to fetch weather:\n{str(e)}")

# ✅ Function to subscribe to weather alerts without showing current weather
def register_and_check():
    email = email_var.get().strip()
    city = city_var.get().strip()

    if not email or not city:
        messagebox.showerror("Input Error", "Please enter both email and city.")
        return

    try:
        # Subscribe the user to the weather alerts SNS topic
        sns.subscribe(
            TopicArn=SNS_TOPIC_ARN,
            Protocol="email",
            Endpoint=email
        )

        # Save the subscription information to DynamoDB for future reference
        subs_table = dynamodb.Table("UserSubscriptions")
        subs_table.put_item(Item={
            "email": email,
            "city": city
        })

        # After successful subscription, show a confirmation message
        weather_display.set(
            f"✅ You have successfully subscribed for weather alerts for {city}.\n"
            f"📧 Confirmation email sent to: {email}\n"
            f"📨 Please check your inbox AND spam folder to confirm subscription.\n\n"
            f"🗂 Your preferences have been saved for automatic weather alerts.\n"
            f"❌ To unsubscribe, click the ‘Unsubscribe’ link at the bottom of the alert email."
        )
        
    except Exception as e:
        messagebox.showerror("Subscription Error", f"Could not complete subscription:\n{str(e)}")

# Buttons
tk.Button(root, text="🔍 Check Weather Only", command=check_weather,
          font=("Helvetica", 12), bg="#4CAF50", fg="white", width=25).pack(pady=5)

tk.Button(root, text="📧 Subscribe for Weather Alerts", command=register_and_check,
          font=("Helvetica", 12), bg="#2196F3", fg="white", width=25).pack(pady=5)

# Start GUI
root.mainloop()
