
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

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
    ("..."))

    input_model = st.sidebar.selectbox(
    "Model",
    ("LogisticReg_Distance_Angle", "..."))

    input_version = st.sidebar.selectbox(
    "Version",
    ("lastest", "..."))

    # input_workspace = st.text_input("Workspace", "...")
    # input_model = st.text_input("Model", "...")
    # input_version = st.text_input("lastest", "...")

    if st.button("Download model", key="download_model"):
            with st.spinner("Loading model from CometML..."):
                time.sleep(1)
            st.success("Model Loaded!")


            # => Brandon : download_registry_model(workspace, model, version)
            # ? does it return 

        
    st.divider()


# ---------------------------

    
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.write("Selected Model")
    st.write( input_workspace, input_model, input_version)
    st.write("TODO : check if the workspace exists in the database")

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