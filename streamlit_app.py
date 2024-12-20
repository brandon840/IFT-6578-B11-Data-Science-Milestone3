import streamlit as st
import pandas as pd
import numpy as np
from ift6758.client.game_client import GameClient  # Assuming GameClient is implemented
from ift6758.client.serving_client import ServingClient  # Assuming ServingClient is implemented

# Title of the app
st.title("Live NHL Game Dashboard")

# Sidebar inputs
with st.sidebar:
    st.header("Model Configuration")
    workspace = st.text_input("Workspace")
    model = st.text_input("Model")
    version = st.text_input("Version")

    if st.button("Download Model"):
        if not workspace or not model or not version:
            st.error("Please provide valid inputs for Workspace, Model, and Version")
        else:
            try:
                serving_client = ServingClient(ip="serving", port=8080)
                response = serving_client.download_registry_model(workspace, model, version)
                st.success(f"Model downloaded: {response}")
            except Exception as e:
                st.error(f"Error downloading model: {e}")


# Main container for Game ID input
with st.container():
    st.header("Game Selection")
    game_id = st.text_input("Enter Game ID (e.g., 2021020329):")

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

# Main container for displaying prediction data
with st.container():
    st.header("Prediction Data")
    st.write("The table above shows the new shot events and their predicted goal probabilities.")
