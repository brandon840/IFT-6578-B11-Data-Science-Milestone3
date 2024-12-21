import streamlit as st
import pandas as pd
import numpy as np
from ift6758.client.game_client import GameClient  # Assuming GameClient is implemented
from ift6758.client.serving_client import ServingClient  # Assuming ServingClient is implemented

# Title of the app
st.title("Live NHL Game Dashboard")

serving_client = ServingClient(ip="127.0.0.1", port=8501)
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
            game_client = GameClient(ip="127.0.0.1", port=8501, game_id=game_id, tracker_file="event_tracker.csv")
            game_client.game_id = game_id
            game_data = game_client.fetch_game_data()
            all_events = game_client.get_events(game_data)  # DataFrame of all queried events
            new_events = game_client.filter_new_events(all_events)  # DataFrame of new events
            game_client.update_score(new_events)
            # game_client.update_event_tracker(new_events)

            # Extract game info
            home_team = all_events["home_team_name"].iloc[0]
            away_team = all_events["away_team_name"].iloc[0]
            period = all_events["period"].max()
            time_remaining = all_events["time_remaining"].iloc[-1]
            home_score = game_client.home_score
            away_score = game_client.away_score

            # Display game info
            st.subheader("Game Info")
            st.write(f"Home Team: {home_team}")
            st.write(f"Away Team: {away_team}")
            st.write(f"Period: {period}")
            st.write(f"Time Remaining: {time_remaining}")
            st.write(f"Current Score: {home_team} {home_score} - {away_team} {away_score}")  

            # Process predictions
            cleaned_events = game_client.extract_features(new_events)
            prediction_df = serving_client.predict(cleaned_events)

            # Convert predictions to DataFrame
            st.subheader("Event Predictions")
            
            # Concat with 
            shot_indices = list(cleaned_events.index)
            df_shots = new_events.iloc[shot_indices]
            df_info = pd.merge(df_shots,prediction_df, left_index=True, right_index=True, how='inner')
            df_info = pd.merge(df_info,cleaned_events,left_index=True, right_index=True, how='inner')
            
            print(df_info.columns)
            st.dataframe(df_info[['event_type', 'x_coord', 'y_coord', 'shot_type','shot_distance','shot_angle','goalie_in_net', 'no_goal_prob', 'goal_prob']])

            # Calculate xG stats
            xg_home = df_info[df_info['event_owner_team'] == df_info['home_team_id']]["goal_prob"].sum()
            xg_away = df_info[df_info['event_owner_team'] == df_info['away_team_id']]["goal_prob"].sum()            
            st.subheader("Expected Goals (xG)")
            st.write(f"Home Team ({home_team}) xG: {xg_home:.2f}")
            st.write(f"Away Team ({away_team}) xG: {xg_away:.2f}")
            st.write(f"Difference (Home xG - Goals): {xg_home - game_client.home_score:.2f}")
            st.write(f"Difference (Away xG - Goals): {xg_away - game_client.away_score:.2f}")

        except Exception as e:
            st.error(f"Error fetching game data: {e}")

# Main container for displaying prediction data
with st.container():
    st.header("Prediction Data")
    st.write("The table above shows the new shot events and their predicted goal probabilities.")
