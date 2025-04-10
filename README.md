# 🌩️ Cloud-Based Weather Alert System

A real-time weather alert system built using AWS services and OpenWeather API, allowing users to receive email alerts for severe weather conditions. It features a simple and interactive GUI built with Python's Tkinter framework.

---

## 📦 Project Overview

This system allows users to:

- 🔍 Check live weather conditions for any city
- 📧 Subscribe to weather alerts via email (using AWS SNS)
- ❌ Unsubscribe easily through the email link
- 🧠 Receive alerts only for extreme weather using smart condition logic

---

## 🛠️ Technologies Used

- **Python** (Tkinter GUI + Lambda)
- **AWS Lambda** (backend processing)
- **AWS SNS** (email notifications)
- **AWS DynamoDB** (weather data storage)
- **AWS API Gateway** (frontend-to-backend connection)
- **OpenWeather API** (real-time weather data)
- **Boto3** (Python SDK for AWS)

---

## 📁 Repository Contents

| File/Folder         | Description |
|---------------------|-------------|
| `lambda_function.py` | This is the AWS Lambda code that runs in the cloud. It is deployed and not executed locally. |
| `weather_gui_lambda.py` | Python GUI app to check weather or register for alerts |
| `requirements.txt` (optional) | Required Python packages |
| `README.md`         | You’re reading it! |

---

## 🚀 How It Works

1. The GUI sends a request to your deployed AWS Lambda via API Gateway.
2. Lambda fetches weather data from OpenWeather API.
3. If a severe condition is detected, it triggers an alert using AWS SNS.
4. The weather data is also stored in DynamoDB.
5. Users receive an email and can unsubscribe via a link.

---

## 📌 Important Note

The `lambda_function.py` in this repo is a copy of the actual Lambda function deployed on AWS.  
To run this system fully, you must have:

- Your Lambda deployed on AWS
- An active API Gateway endpoint
- A configured SNS topic and DynamoDB table

The GUI connects to these services live.

---




---

## 📄 License

MIT License – for academic use only.
