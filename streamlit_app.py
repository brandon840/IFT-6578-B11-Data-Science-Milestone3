
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st


# Set the title of the app
st.title("Hockey Game Dashboard")

# st.write("Welcome to this simple Streamlit app!")

import time



    




# Store the initial value of widgets in session state
if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False


# ---------------------------


with st.sidebar:
    
    st.header("Model Selection")

    st.divider()
    
    input_workspace = st.text_input("Workspace", "...")
    input_model = st.text_input("Model", "...")
    input_version = st.text_input("Version", "...")


    if st.button("Download model", key="download_model"):
            with st.spinner("Loading model from CometML..."):
                time.sleep(1)
            st.success("Done!")

            st.write("TODO : checks ")

        
    st.divider()



# Using object notation
add_selectbox = st.sidebar.selectbox(
    "How would you like to be contacted?",
    ("Email", "Home phone", "Mobile phone")
)

# Using "with" notation
with st.sidebar:
    add_radio = st.radio(
        "Choose a shipping method",
        ("Standard (5-15 days)", "Express (2-5 days)")
    )

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
        st.write("TODO : checks ")




    
st.divider()




# =============================================================================





container = st.container(border=True)
container.write("Home and away team names")
container.write("Period, Time left in the period, Current score")
container.write("Sum of expected goals (xG) for the entire game so far for both teams (obtained from the game client)")






# =============================================================================








st.divider()


    
col1, col2 = st.columns(2)


with col1:


    st.checkbox("Disable text input widget", key="disabled")
    st.radio(
        "Set text input label visibility 👉",
        key="visibility",
        options=["visible", "hidden", "collapsed"],
    )
    st.text_input(
        "Placeholder for the other text input widget",
        "This is a placeholder",
        key="placeholder",
    )

with col2:
    


    text_input = st.text_input(
        "Enter some text 👇",
        label_visibility=st.session_state.visibility,
        disabled=st.session_state.disabled,
        placeholder=st.session_state.placeholder,
    )

    if text_input:
        st.write("You entered: ", text_input)






# Input Section
name = st.text_input("What's your name?")
if name:
    st.write(f"Hello, {name}!")

# Button to generate random data
if st.button("Generate Random Data"):
    # Create a DataFrame with random data
    data = pd.DataFrame({
        "X": np.arange(1, 11),
        "Y": np.random.randint(1, 100, size=10)
    })

    st.write("Here is your random data:")
    st.dataframe(data)

    # Plot the data
    st.write("Here's a chart of your random data:")
    fig, ax = plt.subplots()
    ax.plot(data["X"], data["Y"], marker="o")
    ax.set_title("Random Data Chart")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    st.pyplot(fig)



with st.expander("See explanation"):
    st.write("""
        The chart above shows some random data.
        The data is random because I said it was.
    """)


# with st.sidebar:
#     with st.echo():
#         st.write("This code will be printed to the sidebar.")

#     with st.spinner("Loading..."):
#         time.sleep(5)
#     st.success("Done!")



# ---------------------------------------------------------------

# X, idx, ... = game_client.ping_game(game_id, idx, ...)
# r = requests.post(
# 	"http://127.0.0.1:<PORT>/predict", 
# 	json=json.loads(X.to_json())
# )
# print(r.json())

# # use with docker