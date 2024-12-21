import requests
import json

# Define the endpoint URL
url = "http://127.0.0.1:8080/download_registry_model"

# Define the JSON payload to send to the Flask app
payload = {
    "workspace": "ds_b11",  # Replace with your actual workspace
    "model": "IFT6758.2024-B11/LogisticReg_Distance_Angle",  # Replace with the model name you want to load
    "version": "latest",  # Replace with the model version you're querying for
}

# Send the POST request to the /download_registry_model endpoint
response = requests.post(url, json=payload)

# Print the response from the Flask app
print(response.json())