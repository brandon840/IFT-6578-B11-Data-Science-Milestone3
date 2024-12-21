"""
If you are in the same directory as this file (app.py), you can run run the app using gunicorn:
    
    $ gunicorn --bind 0.0.0.0:<PORT> app:app

gunicorn can be installed via:

    $ pip install gunicorn

"""
import os
from pathlib import Path
import logging
from flask import Flask, jsonify, request, abort
import pandas as pd
import pickle
import joblib
import pickle
import wandb

LOG_FILE = os.environ.get("FLASK_LOG", "flask.log")
MODEL_FOLDER = os.path.dirname(os.getcwd()) + "/ift6758/ift6758/models/"

app = Flask(__name__)

model = None


with app.app_context():
    """
    Hook to handle any initialization before the first request (e.g. load model,
    setup logging handler, etc.)
    """
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO)
    model_path = MODEL_FOLDER + "LogisticReg_Distance_Angle.pkl"
    if Path(model_path).exists():
        with open(model_path, 'rb') as file:
            model = pickle.load(file)
        app.logger.info(f"Default model loaded: {model_path}")
    else:
        app.logger.warning(f"Default model not found: {model_path}")

@app.route("/logs", methods=["GET"])
def logs():
    """Reads data from the log file and returns them as the response"""
    
    if not Path(LOG_FILE).exists():
        return jsonify({"error": "Log file not found"}), 404
    
    with open(LOG_FILE, "r") as log_file:
        logs = log_file.read()
    
    response = {"logs":logs}
    return jsonify(response)  # response must be json serializable!


@app.route("/download_registry_model", methods=["POST"])
def download_registry_model():
    """
    Handles POST requests made to http://IP_ADDRESS:PORT/download_registry_model

    The comet API key should be retrieved from the ${COMET_API_KEY} environment variable.

    Recommend (but not required) json with the schema:

        {
            workspace: (required),
            model: (required),
            version: (required),
            ... (other fields if needed) ...
        }
    
    """
    # Get POST json data
    json = request.get_json()
    app.logger.info(json)
    
    workspace = json.get("workspace")
    model_name_full = json.get("model")
    model_name = model_name_full.split("/")[1] # Need to do tis because format is IFT6758.2024-B11/LogisticReg_Distance_Angle
    version = json.get("version")
    app.logger.info(f"Workpace: {workspace}, Model Name: {model_name}, Version: {version}")

    model_file = MODEL_FOLDER + f"{model_name}.pkl"
    model_file = Path(model_file)
    if model_file.exists():
        try:
            with open(model_file, 'rb') as file:
                model = pickle.load(file)
            log_message = f"Model {model_file} loaded from disk"
            app.logger.info(log_message)
            return jsonify({"message":log_message})
        
        except Exception as e:
            error_message = f"Failed to load model {model_file}: {str(e)}"
            app.logger.error(error_message)
            return jsonify({"error":error_message}), 500
        
       
    try:
        model_file_joblib = MODEL_FOLDER + f"{model_name}.joblib"

        # Get model from WandB
        model_file_joblib = MODEL_FOLDER + f"{model_name}.joblib"
        wandb_client = wandb.Api(api_key=os.environ.get("WANDB_API_KEY"))
        artifact = wandb_client.artifact(f"{workspace}/{model_name_full}:{version}")
        artifact.download(root=MODEL_FOLDER)
        
        # Convert .joblib to .pkl
        model = joblib.load(model_file_joblib)
        with open(model_file, 'wb') as file:
            pickle.dump(model_file, file)

        log_message = f"Model {model_file} downloaded and loaded successfully."
        app.logger.info(log_message)
        return jsonify({"message": log_message})
    
    except Exception as e:
        error_message = f"Failed to download/load model {model_file}: {str(e)}"
        app.logger.error(error_message)
        return jsonify({"error": error_message}), 500


@app.route("/predict", methods=["POST"])
def predict():
    """
    Handles POST requests made to http://IP_ADDRESS:PORT/predict

    Returns predictions
    """
    # Get POST json data
    json = request.get_json()
    app.logger.info(json)

    try:
        # Convert JSON input to DataFrame
        input_data = pd.read_json(json)
        predictions = model.predict_proba(input_data).tolist() if hasattr(model, "predict_proba") else model.predict(input_data).tolist()
        app.logger.info(f"Predictions made: {predictions}")
        return jsonify({"predictions": predictions})
    
    except Exception as e:    
        app.logger.error(f"Prediction failed: {str(e)}")
        return jsonify({"error": str(e)}), 500