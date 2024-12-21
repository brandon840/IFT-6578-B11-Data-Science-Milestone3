
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

from ift6758.client.game_client import GameClient  # Assuming GameClient is implemented
from ift6758.client.serving_client import ServingClient  # Assuming ServingClient is implemented

import requests
import json


# Set the title of the app
st.title("Hockey Game Dashboard")


with st.sidebar:
    
    st.header("Model Selection")
    st.divider()

#     add_selectbox = st.sidebar.selectbox(
#     "How would you like to be contacted?",
#     ("Email", "Home phone", "Mobile phone")
# )


    input_workspace = st.sidebar.selectbox(
    "Workspace?",
    ("ds_b11","..."))

    input_model = st.sidebar.selectbox(
    "Model",
    ("Logistic Regression Distance and Angle", "Logistic Regression Distance Only","..."))

    input_version = st.sidebar.selectbox(
    "Version",
    ("lastest","v0","..."))

    # input_workspace = st.text_input("Workspace", "...")
    # input_model = st.text_input("Model", "...")
    # input_version = st.text_input("lastest", "...")

    if st.button("Download model", key="download_model"):


        if input_workspace == 'ds_b11':

            model = None
            if input_model == 'Logistic Regression Distance and Angle':
                model =  "IFT6758.2024-B11/LogisticReg_Distance_Angle"
            if input_model == 'Logistic Regression Distance Only':
                model =  "IFT6758.2024-B11/LogisticReg_Distance_Only"
            else:
                st.failure("Model not found")

            if model:

                # Define the endpoint URL
                url = "http://127.0.0.1:8080/download_registry_model"

                # Define the JSON payload to send to the Flask app
                payload = {
                    "workspace": input_workspace,
                    "model": model,
                    "version": input_version,
                }

                
            
                with st.spinner("Loading model from Wandb..."):
                    # Send the POST request to the /download_registry_model endpoint
                    response = requests.post(url, json=payload)
            
                if response.status_code == 200:
                    st.success("Success Model Loaded")
                else:
                    st.failure("Something went wrong. Error:", response.status_code, response.json())

        else:
            st.failure("Workspace not found")


        
    st.divider()


# ---------------------------

    
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.write("Selected Model")
    st.write( input_workspace, input_model, input_version)

with col2:
    input_workspace = st.text_input("Game ID", placeholder="eg: 2021020329",)

    if st.button("Ping Game"):
        st.write("Fetching game data...")
        try:
            game_client = GameClient(ip="serving", port=8080, game_id=game_id, tracker_file="event_tracker.csv")
            game_data = game_client.fetch_game_data()
            all_events = game_data.get("liveData", {}).get("plays", {}).get("allPlays", [])
            new_events = game_client.filter_new_events(all_events)
            game_client.update_event_tracker(new_events)

            # Extract game info
            home_team = game_data["gameData"]["teams"]["home"]["name"]
            away_team = game_data["gameData"]["teams"]["away"]["name"]
            period = game_data["liveData"]["linescore"]["currentPeriod"]
            time_remaining = game_data["liveData"]["linescore"]["currentPeriodTimeRemaining"]
            current_score = game_data["liveData"]["linescore"]["teams"]

            # Display game info
            st.subheader("Game Info")
            st.write(f"Home Team: {home_team}")
            st.write(f"Away Team: {away_team}")
            st.write(f"Period: {period}")
            st.write(f"Time Remaining: {time_remaining}")
            st.write(f"Current Score: {current_score['home']['goals']} - {current_score['away']['goals']}")

            # Process predictions
            predictions = []
            for event in new_events:
                features = game_client.extract_features(event)
                prediction = game_client.query_prediction_service(features)
                event["goal_probability"] = prediction["goal_probability"]
                predictions.append(event)

            # Convert predictions to DataFrame
            prediction_df = pd.DataFrame(predictions)
            st.subheader("Event Predictions")
            st.dataframe(prediction_df)

            # Calculate xG stats
            xg_home = prediction_df[prediction_df["team"] == home_team]["goal_probability"].sum()
            xg_away = prediction_df[prediction_df["team"] == away_team]["goal_probability"].sum()
            st.subheader("Expected Goals (xG)")
            st.write(f"Home Team xG: {xg_home:.2f}")
            st.write(f"Away Team xG: {xg_away:.2f}")
            st.write(f"Difference (Home xG - Goals): {xg_home - current_score['home']['goals']:.2f}")
            st.write(f"Difference (Away xG - Goals): {xg_away - current_score['away']['goals']:.2f}")

        except Exception as e:
            st.error(f"Error fetching game data: {e}")

    
st.divider()




# =============================================================================



st.header("GameID HomeTeam vs AwayTeam")

container = st.container(border=True)

container.write("Period, Time left in the period, Current score")

col1, col2 = container.columns(2)

container.write("Sum of expected goals (xG) for the entire game so far for both teams (obtained from the game client)")

HomeTeam = col1.container(height=120)
HomeTeam.title("HomeTeam")

AwayTeam = col2.container(height=120)
AwayTeam.title("AwayTeam")


# =============================================================================


st.header("Input Data & Predictions")

container = st.container(border=True)
container.write("add data frame here")




# # use with docker