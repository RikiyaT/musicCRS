import os
import requests
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

SPOTIFY_CLIENT_ID = '6f94333728d9457ba9f6226a0fda413b'
SPOTIFY_CLIENT_SECRET = 'b493b61519ed4e7da5246481b0730b94'

class ActionFetchTopSong(Action):

    def name(self) -> Text:
        return "action_fetch_top_song"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        artist = tracker.get_slot("artist")
        top_song = self.get_top_song(artist)

        if top_song:
            dispatcher.utter_message(text=f"The most famous song by {artist} is '{top_song}'.")
        else:
            dispatcher.utter_message(text=f"Sorry, I couldn't find any song for '{artist}'.")

        return []

    def get_top_song(self, artist: str) -> str:
        access_token = self.get_spotify_access_token(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
        if not access_token:
            return None

        artist_id = self.search_artist(artist, access_token)
        if not artist_id:
            return None

        top_track = self.get_artist_top_track(artist_id, access_token)
        return top_track

    def get_spotify_access_token(self, client_id: str, client_secret: str) -> str:
        auth_url = 'https://accounts.spotify.com/api/token'

        auth_response = requests.post(
            auth_url,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            auth=(client_id, client_secret),
            data={'grant_type': 'client_credentials'}
        )

        if auth_response.status_code == 200:
            access_token = auth_response.json()['access_token']
            return access_token
        else:
            return None

    def search_artist(self, artist: str, access_token: str) -> str:
        search_url = 'https://api.spotify.com/v1/search'
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {
            'q': artist,
            'type': 'artist',
            'limit': 1
        }

        response = requests.get(search_url, headers=headers, params=params)
        if response.status_code == 200:
            results = response.json()['artists']['items']
            if results:
                return results[0]['id']
            else:
                return None
        else:
            return None

    def get_artist_top_track(self, artist_id: str, access_token: str) -> str:
        top_tracks_url = f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks'
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {
            'market': 'US'
        }

        response = requests.get(top_tracks_url, headers=headers, params=params)
        if response.status_code == 200:
            top_tracks = response.json()['tracks']
            if top_tracks:
                return top_tracks[0]['name']
            else:
                return None
        else:
            return None
