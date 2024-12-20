import json
import requests
import os
import pandas as pd
import logging


logger = logging.getLogger(__name__)


class GameClient:
    
    def __init__(self, ip: str = "0.0.0.0", port: int = 5000, game_id = None, tracker_file=None):
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
        
    
    def update_event_tracker(self,events) -> dict:
        """
        Updates the tracker with new events
        
        Args:
            events (list): The list of new events 
        """
        
        try:
            
            
        except Exception as e:
