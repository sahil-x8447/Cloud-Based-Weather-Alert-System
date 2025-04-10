import tkinter as tk
from tkinter import messagebox
import requests
import boto3

# AWS Setup
sns = boto3.client("sns", region_name="ca-central-1")
SNS_TOPIC_ARN = "arn:aws:sns:ca-central-1:340752826531:WeatherAlerts"
LAMBDA_API_URL = "https://2zl99t62q4.execute-api.ca-central-1.amazonaws.com/WeatherAlertFunction"

# GUI Setup
root = tk.Tk()
root.title("☁️ Weather Alert System")
root.geometry("550x500")
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

# Weather display label (hidden until needed)
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

# Function to check weather only
def check_weather():
    city = city_var.get().strip()

    if not city:
        messagebox.showerror("Input Error", "Please enter a city.")
        return

    try:
        response = requests.get(f"{LAMBDA_API_URL}?city={city}")
        data = response.json()

        if response.status_code == 200:
            temp = data.get("temperature")
            cond = data.get("condition")
            loc = data.get("location")

            # Show the weather label only when content exists
            if not weather_label.winfo_ismapped():
                weather_label.pack(pady=20)

            weather_display.set(
                f"✅ Weather in {loc.title()}:\n"
                f"🌡 Temperature: {temp}°C\n"
                f"☁️ Condition: {cond.title()}"
            )
        else:
            weather_display.set(f"❌ Error: {data.get('error')}")

    except Exception as e:
        weather_display.set(f"⚠️ Failed to fetch weather:\n{str(e)}")
        if not weather_label.winfo_ismapped():
            weather_label.pack(pady=20)

# Function to register and check weather
def register_and_check():
    email = email_var.get().strip()
    city = city_var.get().strip()

    if not email or not city:
        messagebox.showerror("Input Error", "Please enter both email and city.")
        return

    try:
        # Subscribe the user to SNS
        sns.subscribe(
            TopicArn=SNS_TOPIC_ARN,
            Protocol="email",
            Endpoint=email
        )
    except Exception as e:
        messagebox.showerror("SNS Error", f"Could not subscribe email:\n{str(e)}")
        return

    try:
        response = requests.get(f"{LAMBDA_API_URL}?city={city}")
        data = response.json()

        if response.status_code == 200:
            temp = data.get("temperature")
            cond = data.get("condition")
            loc = data.get("location")

            if not weather_label.winfo_ismapped():
                weather_label.pack(pady=20)

            weather_display.set(
                f"✅ Weather in {loc.title()}:\n"
                f"🌡 Temperature: {temp}°C\n"
                f"☁️ Condition: {cond.title()}\n\n"
                f"📧 Confirmation email sent to:\n{email}\n"
                f"📨 *Please check your inbox AND spam folder to confirm subscription*"
            )
        else:
            weather_display.set(f"❌ Error: {data.get('error')}")

    except Exception as e:
        weather_display.set(f"⚠️ Failed to fetch weather:\n{str(e)}")
        if not weather_label.winfo_ismapped():
            weather_label.pack(pady=20)

# Buttons
tk.Button(root, text="🔍 Check Weather Only", command=check_weather,
          font=("Helvetica", 12), bg="#4CAF50", fg="white", width=25).pack(pady=5)

tk.Button(root, text="📧 Register & Get Weather", command=register_and_check,
          font=("Helvetica", 12), bg="#2196F3", fg="white", width=25).pack(pady=5)

root.mainloop()
