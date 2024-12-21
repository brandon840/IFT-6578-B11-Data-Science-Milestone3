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
from dotenv import load_dotenv

load_dotenv()

LOG_FILE = os.environ.get("FLASK_LOG", "flask.log")
MODEL_FOLDER = Path("ift6758/ift6758/models")  # Adjusted for Docker

app = Flask(__name__)

global model

with app.app_context():
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO)
    model_path = MODEL_FOLDER / "LogisticReg_Distance_Angle_new.pkl"
    if model_path.exists():
        with open(str(model_path), 'rb') as file:
            model = joblib.load(file)
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
    """
    try:
        # Parse and validate the JSON payload
        json_data = request.get_json()
        if not json_data:
            error_message = "Invalid JSON: No data received."
            app.logger.error(error_message)
            return jsonify({"error": error_message}), 400
        
        app.logger.info(f"Received JSON: {json_data}")

        # Extract and validate required fields
        workspace = json_data.get("workspace")
        model_name_full = json_data.get("model")
        version = json_data.get("version")

        if not workspace or not model_name_full or not version:
            error_message = "Missing required fields: 'workspace', 'model', or 'version'."
            app.logger.error(error_message)
            return jsonify({"error": error_message}), 400

        # Extract the model name from the full name
        model_name = model_name_full.split("/")[1] if "/" in model_name_full else model_name_full
        app.logger.info(f"Workspace: {workspace}, Model Name: {model_name}, Version: {version}")

        # Paths for model files
        model_file = MODEL_FOLDER / f"{model_name}.pkl"
        model_file_joblib = MODEL_FOLDER / f"{model_name}.joblib"

        # Step 1: Check if the .pkl model file already exists
        if model_file.exists():
            try:
                with open(model_file, 'rb') as file:
                    model = pickle.load(file)
                log_message = f"Model {model_file} loaded from disk."
                app.logger.info(log_message)
                return jsonify({"message": log_message})
            except NotImplementedError as e:
                error_message = f"Model file incompatible: {str(e)}. Please re-save the file using a Linux system."
                app.logger.error(error_message)
                return jsonify({"error": error_message}), 500
            except Exception as e:
                error_message = f"Failed to load model {model_file}: {str(e)}"
                app.logger.error(error_message)
                return jsonify({"error": error_message}), 500

        # Step 2: Download and process the model from WandB
        try:
            # Initialize WandB client
            wandb_api_key = os.environ.get("WANDB_API_KEY")
            if not wandb_api_key:
                error_message = "WANDB_API_KEY environment variable is not set."
                app.logger.error(error_message)
                return jsonify({"error": error_message}), 500

            wandb_client = wandb.Api(api_key=wandb_api_key)
            artifact = wandb_client.artifact(f"{workspace}/{model_name_full}:{version}")
            app.logger.info(f"Attempting to download artifact: {workspace}/{model_name_full}:{version}")

            # Download the artifact to the specified folder
            artifact.download(root=str(MODEL_FOLDER))
            app.logger.info(f"Artifact {model_name_full}:{version} downloaded successfully.")

            # Step 3: Check and convert the joblib model to pickle format
            if model_file_joblib.exists():
                model = joblib.load(model_file_joblib)
                with open(model_file, 'wb') as file:
                    pickle.dump(model, file)
                log_message = f"Model {model_file} downloaded, converted to .pkl, and saved successfully."
                app.logger.info(log_message)
                return jsonify({"message": log_message})
            else:
                error_message = f"Joblib model file {model_file_joblib} not found after download."
                app.logger.error(error_message)
                return jsonify({"error": error_message}), 500

        except wandb.errors.CommError as e:
            error_message = f"Failed to connect to WandB: {str(e)}"
            app.logger.error(error_message)
            return jsonify({"error": error_message}), 500
        except FileNotFoundError as e:
            error_message = f"Downloaded model file not found: {str(e)}"
            app.logger.error(error_message)
            return jsonify({"error": error_message}), 500
        except Exception as e:
            error_message = f"Failed to download or process model {model_name_full}:{version} - {str(e)}"
            app.logger.error(error_message)
            return jsonify({"error": error_message}), 500

    except Exception as e:
        # Catch any unexpected errors
        error_message = f"Unexpected server error: {str(e)}"
        app.logger.error(error_message, exc_info=True)
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
        with open(MODEL_FOLDER / "LogisticReg_Distance_Angle.pkl", 'rb') as f:
            model = pickle.load(f)
        input_data = pd.read_json(json)
        input_data = input_data[model.feature_names_in_]
        predictions = model.predict_proba(input_data) if hasattr(model, "predict_proba") else model.predict(input_data)
        app.logger.info(f"Predictions made: {predictions}")
        return jsonify({"predictions": predictions.tolist()})
    
    except Exception as e:    
        app.logger.error(f"Prediction failed: {str(e)}")
        return jsonify({"error": str(e)}), 500
    

if __name__ == "__main__":
    # Run the Flask app on 0.0.0.0 to make it accessible within Docker containers
    app.run(host="127.0.0.1", port=8501)