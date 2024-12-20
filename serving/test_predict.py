import requests
import json
import pandas as pd

# Define the endpoint URL for the predict route
url = "http://127.0.0.1:8080/predict"

data_path = 'serving/feat_eng_ii_dataframe.csv'



df = pd.read_csv(data_path)
df = df.head()
X = df[['shot_distance','shot_angle']]
# Send the POST request to the /predict endpoint
response = requests.post(url, json=X.to_json())

# Print the response from the Flask app
print(response.json())
