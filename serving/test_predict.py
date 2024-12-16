import requests
import json
import pandas as pd

# Define the endpoint URL for the predict route
url = "http://127.0.0.1:8080/predict"

data_path = 'ift6758/ift6758/data/data.csv'

df = pd.read_csv(data_path)

# Send the POST request to the /predict endpoint
response = requests.post(url, json=df.to_json())

# Print the response from the Flask app
print(response.json())
