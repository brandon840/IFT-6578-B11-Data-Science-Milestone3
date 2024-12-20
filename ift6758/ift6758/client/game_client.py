import json
import requests
import os
import pandas as pd
import logging


logger = logging.getLogger(__name__)


class GameClient:
    
    def __init__(self, ip: str = "0.0.0.0", port: int = 8080, game_id = None, tracker_file=None):
        self.base_url = f"http://{ip}:{port}"
        self.game_id = game_id
        logger.info(f"Initializing game client; base URL: {self.base_url} for game {self.game_id}")
        
        if os.path.exists(tracker_file):
            self.processed_events = pd.read_csv(tracker_file)
        else:
            self.processed_events = pd.DataFrame()
            
        # Check if there's a game ID provided
        if not self.game_id:
            raise ValueError("Game ID must be provided.")
        
    def fetch_game_data(self):
        """
        Fetch live game data for the specified game ID from the API.
        """
        url = f"{self.base_url}/games/{self.game_id}/feed/live"
        try:
            response = requests.get(url)
            response.raise_for_status()
            game_data = response.json()
            logger.info(f"Fetched live game data for game {self.game_id}")
            return game_data
        except requests.RequestException as e:
            logger.error(f"Failed to fetch game data: {e}")
            raise

    def filter_new_events(self, events):
        """
        Filter out events that have already been processed.

        Args:
            events (list): List of all events from the live game data.

        Returns:
            list: List of new events that have not been processed.
        """
        if self.processed_events.empty:
            return events

        processed_event_ids = set(self.processed_events["event_id"])
        new_events = [event for event in events if event["event_id"] not in processed_event_ids]
        logger.info(f"Filtered {len(new_events)} new events from {len(events)} total events.")
        return new_events

    def update_event_tracker(self, events):
        """
        Update the tracker with new events.

        Args:
            events (list): The list of new events to be added to the tracker.
        """
        try:
            new_event_data = pd.DataFrame(
                [{"event_id": event["event_id"], "timestamp": event["timestamp"]} for event in events]
            )
            self.processed_events = pd.concat([self.processed_events, new_event_data], ignore_index=True)
            self.processed_events.to_csv(self.tracker_file, index=False)
            logger.info(f"Updated event tracker with {len(events)} new events.")
        except Exception as e:
            logger.error(f"Failed to update event tracker: {e}")
            raise

    def process_new_events(self):
        """
        Fetch live game data, filter new events, process them, and update the tracker.
        """
        try:
            game_data = self.fetch_game_data()
            all_events = game_data.get("liveData", {}).get("plays", {}).get("allPlays", [])

            # Filter out new events
            new_events = self.filter_new_events(all_events)

            # Process each new event (replace with your feature extraction and prediction logic)
            for event in new_events:
                # Example processing: log the event and send it to the prediction service
                logger.info(f"Processing event: {event}")
                self.process_event(event)

            # Update the event tracker with newly processed events
            self.update_event_tracker(new_events)
        except Exception as e:
            logger.error(f"Error processing new events: {e}")
            raise

    def process_event(self, event):
        """
        Process a single event: produce features, query the prediction service, and store results.

        Args:
            event (dict): The event to process.
        """
        try:
            # Extract features (replace with actual feature extraction logic)
            features = self.extract_features(event)

            # Query the prediction service
            prediction = self.query_prediction_service(features)

            # Store the prediction (replace with actual storage logic)
            logger.info(f"Stored prediction for event {event['event_id']}: {prediction}")
        except Exception as e:
            logger.error(f"Failed to process event {event}: {e}")

    def extract_features(self, event):
        """
        Extract features required by the model from an event.

        Args:
            event (dict): The event to extract features from.

        Returns:
            dict: Extracted features.
        """
        # Example: Replace with actual feature extraction logic
        return {
            "event_type": event.get("result", {}).get("eventTypeId"),
            "coordinates": event.get("coordinates"),
            "team": event.get("team", {}).get("name"),
        }

    def query_prediction_service(self, features):
        """
        Query the prediction service with the extracted features.

        Args:
            features (dict): The features to send to the prediction service.

        Returns:
            dict: Prediction results from the service.
        """
        try:
            url = f"{self.base_url}/predict"
            response = requests.post(url, json=features)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to query prediction service: {e}")
            raise
