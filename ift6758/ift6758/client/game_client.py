import json
import requests
import os
import pandas as pd
import logging
import numpy as np
import math

logger = logging.getLogger(__name__)

def distance_goal(x,y,shot_direction=True):
    if shot_direction == 'right':
        return np.sqrt((x-89)**2 + (y-0)**2)
    return np.sqrt((x+89)**2 + (y-0)**2)

def add_distance_col( row):
    shot_direction = ""
    if row['home_team_defending_side'] == 'right':
        if row['event_owner_team'] == row['home_team_id']:
            shot_direction = 'left'
        else:
            shot_direction = 'right'
    else:   
        if row['event_owner_team'] == row['home_team_id']:
            shot_direction = 'right'
        else:
            shot_direction = 'left'
        
    return distance_goal(row['x_coord'],row['y_coord'],shot_direction)

def get_measurements(x, y, event_owner_team, home_team_id, away_team_id, home_team_defending_side):
    """Get absolute values for base and height of theoretical right triangle to get shot angle"""
    
    # x_coords of left and right nets
    right_net = 89
    left_net = -89
    
    # Home team
    if event_owner_team == home_team_id:
        # Attack the right net
        if home_team_defending_side == 'left':
            base = x - right_net
        # Attacking the left net
        else:
            base = x - left_net
    # Away team        
    else:
        # Attack the left net
        if home_team_defending_side == 'left':
            base = x - left_net
        # Attacking the right net
        else:
            base = x - right_net
    height = 0 -y  # Height will be the same no matter which net we are targeting
    return abs(base), abs(height)

def get_shot_angle(row):
    if row['event_type'] in ['shot-on-goal', 'goal']:
        base, height = get_measurements(row['x_coord'], row['y_coord'], row['event_owner_team'], row['home_team_id'], row['away_team_id'], row['home_team_defending_side'])
        angle_radians = math.atan2(height, base)
        angle_degrees = math.degrees(angle_radians)
        if row['x_coord'] < -89 or row['x_coord'] > 89:
            return -round(angle_degrees, 2)
        return round(angle_degrees, 2)
    else:
        return None
    
class GameClient:
    
    def __init__(self, ip: str = "127.0.0.1", port: int = 8080, game_id = None, tracker_file=None):
        self.base_url = f"http://{ip}:{port}"
        self.game_id = game_id
        logger.info(f"Initializing game client; base URL: {self.base_url} for game {self.game_id}")
        self.tracker_file = tracker_file
        self.processed_events = pd.DataFrame
        self.away_score = 0
        self.home_score = 0

        # Check if there's a game ID provided
        if not self.game_id:
            raise ValueError("Game ID must be provided.")
        
    def fetch_game_data(self):
        """
        Fetch live game data for the specified game ID from the API.
        """
        url = f"https://api-web.nhle.com/v1/gamecenter/{self.game_id}/play-by-play"
        try:
            response = requests.get(url)
            response.raise_for_status()
            game_data = response.json()
            logger.info(f"Fetched live game data for game {self.game_id}")
            return game_data
        except requests.RequestException as e:
            logger.error(f"Failed to fetch game data: {e}")
            raise
    
    def get_events(self, data):
        # Extract game ID
        game_id = data.get('id', None)
        
        # Extract team ids
        home_team_id = data['homeTeam'].get('id',None)
        away_team_id = data['awayTeam'].get('id',None)

        # Extract team names
        common_name_home = data['homeTeam'].get('commonName', None)
        common_name_away = data['awayTeam'].get('commonName', None)
        home_team_name = common_name_home.get('default',None)
        away_team_name = common_name_away.get('default',None)
        
        # Extract plays
        plays = data.get('plays', [])

        # Create a list to store the parsed data
        parsed_data = []

        # Loop through each play and extract relevant details
        for play in plays:
            event_id = play.get('eventId', None)
            period = play['periodDescriptor'].get('number', None)
            time_in_period = play.get('timeInPeriod', None)
            time_remaining = play.get('timeRemaining', None)
            event_type = play.get('typeDescKey', None)
            event_details = play.get('details', {})
            home_team_defending_side = play.get('homeTeamDefendingSide', None)
            
            # Extract coordinates if available
            x_coord = event_details.get('xCoord', None)
            y_coord = event_details.get('yCoord', None)
            
            # Goalie in net?
            gaolie_in_net = event_details.get('goalieInNetId', None)
            
            # Extract shot type if available
            shot_type = event_details.get('shotType', None)

            # Extract team and player details
            event_owner_team = event_details.get('eventOwnerTeamId', None)
            shooting_player_id = event_details.get('shootingPlayerId', None)
            goalie_in_net_id = event_details.get('goalieInNetId', None)
            zone_code = event_details.get('zoneCode',None)
            
            # Get score
            home_score = event_details.get('homeScore', None)
            away_score = event_details.get('awayScore', None)
            
            # Extract penalty duration
            penalty_duration = event_details.get('duration',None)

            # Append the parsed data to the list
            parsed_data.append({
                'game_id' : game_id,
                'event_id': event_id,
                'period': period,
                'time_in_period': time_in_period,
                'time_remaining': time_remaining,
                'event_type': event_type,
                'x_coord': x_coord,
                'y_coord': y_coord,
                'shot_type' : shot_type,
                'event_owner_team': event_owner_team,
                'shooting_player_id': shooting_player_id,
                'goalie_in_net_id': goalie_in_net_id,
                'away_score' : away_score,
                'home_score' : home_score,
                'home_team_id': home_team_id,
                'away_team_id': away_team_id,
                'home_team_name': home_team_name,
                'away_team_name': away_team_name,
                'home_team_defending_side': home_team_defending_side,
                'zone_code': zone_code,
                'penalty_duration': penalty_duration,
                'goalie_in_net': gaolie_in_net,
            })
        # Return DataFrame
        return pd.DataFrame(parsed_data)
        
    def filter_new_events(self, df_events):
        """
        Filter out events that have already been processed.

        Args:
            df_events (pd.DataFrame): DataFrame of all events from the live game data.

        Returns:
            df_new: DataFrame of new events that have not been processed.
        """
        if self.processed_events.empty:
            return df_events
        events_old = set(self.processed_events['event_id'])
        df_new = df_events[~df_events['event_id'].isin(events_old)].copy()        
        return df_new   

    def update_score(self, df_new_events):
        df_goals = df_new_events[df_new_events['event_type'] == 'goal']
        
        if len(df_goals) > 0:
            self.home_score = int(df_goals['home_score'].iloc[-1])
            self.away_score = int(df_goals['away_score'].iloc[-1])
        
    
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

    def extract_features(self, df_events):
        """
        Extract features required by the model from an event. 
        We need the following:
            - Distance from net
            - Angle from net
            - Is Goal
            - Empty Net
        Obviously, we will only be getting "goals" and "shot-on-goal" events    
        
        Args:
            df_events (): Dataframe of events to extract features from.

        Returns:
            df_events: Dataframe with extracted features of interest.
        """
        df_shots = df_events[df_events['event_type'].isin(['goal','shot-on-goal'])].copy()
        df_shots['shot_distance'] = df_shots.apply(add_distance_col, axis=1)
        df_shots['shot_angle'] = df_shots.apply(get_shot_angle, axis=1)   
        df_shots['is_goal'] = df_shots.apply(lambda row: int(row['event_type'] == 'goal'), axis=1)
        df_shots['empty_net'] = df_shots.apply(lambda row: int(not np.isnan(row['goalie_in_net'])) ,axis=1)
        
        return df_shots[['shot_distance','shot_angle','empty_net','is_goal']]

    def query_prediction_service(self, df_cleaned_events):
        """
        Query the prediction service with the extracted features.

        Args:
            df_cleaned_events (pd.DataFrame): Datafram with the features to send to the prediction service.

        Returns:
            pd.DataFrame: Prediction results from the service.
        """
        try:
            url = f"{self.base_url}/predict"
            response = requests.post(url, json=df_cleaned_events.to_json(orient='records'))
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to query prediction service: {e}")
            raise
