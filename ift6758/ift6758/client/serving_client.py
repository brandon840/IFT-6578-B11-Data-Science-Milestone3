import json
import requests
import pandas as pd
import logging


logger = logging.getLogger(__name__)


class ServingClient:
    def __init__(self, ip: str = "127.0.0.1", port: int = 8080, features=None):
        self.base_url = f"http://{ip}:{port}"
        logger.info(f"Initializing client; base URL: {self.base_url}")

        if features is None:
            features = ["shot_distance","shot_angle"]
        self.features = features

        # any other potential initialization

    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Formats the inputs into an appropriate payload for a POST request, and queries the
        prediction service. Retrieves the response from the server, and processes it back into a
        dataframe that corresponds index-wise to the input dataframe.
        
        Args:
            X (Dataframe): Input dataframe to submit to the prediction service.
        """
        try:
            url = self.base_url + "/predict"
            X = X[self.features]
            payload = X.to_json(orient='records')
            response = requests.post(url, json=json.loads(payload))
            if response.status_code == 200:
                predictions = response.json().get("predictions", [])
                return pd.DataFrame(predictions, columns=["prediction"], index=X.index)
            else:
                logger.error(f"Prediction failed: {response.json()}")
                response.raise_for_status()
                
        except Exception as e:
            logger.error(f"Error in predict: {str(e)}")
            raise
        
    def logs(self) -> dict:
        """Get server logs"""
        try:
            url = self.base_url + "/logs"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to fetch logs: {response.json()}")
                response.raise_for_status()
                
        except Exception as e:
            logger.error(f"Error in logs: {str(e)}")
            raise
        

    def download_registry_model(self, workspace: str, model: str, version: str) -> dict:
        """
        Triggers a "model swap" in the service; the workspace, model, and model version are
        specified and the service looks for this model in the model registry and tries to
        download it. 

        See more here:

            https://www.comet.ml/docs/python-sdk/API/#apidownload_registry_model
        
        Args:
            workspace (str): The Comet ML workspace
            model (str): The model in the Comet ML registry to download
            version (str): The model version to download
        """
        try:
            url = self.base_url + "/download_registry_model"
            payload = {
                "workspace": workspace,
                "model": model,
                "version": version,
            }
            
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to download model: {response.json()}")
                response.raise_for_status()
                
        except Exception as e:
            logger.error(f"Error in download_registry_model: {str(e)}")
            raise