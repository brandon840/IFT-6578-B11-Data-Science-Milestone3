
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

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
            if input_model == 'LogisticReg_Distance_Angle':
                model =  "IFT6758.2024-B11/LogisticReg_Distance_Angle"
            if input_model == 'LogisticReg_Distance_Only':
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

    if st.button("Ping game"):
        st.write("TODO : connect with game_client.ping_game ")

        # X, idx, ... = game_client.ping_game(game_id, idx, ...)
        # r = requests.post(
        #     "http://127.0.0.1:<PORT>/predict", 
        #     json=json.loads(X.to_json())
        # )
        # print(r.json())


        # 1. get update on game from game_client
        # 2. get predirctions on new events
        # 3. update dashboard with new data

    
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