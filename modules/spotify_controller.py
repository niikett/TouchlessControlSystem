import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

class SpotifyController:
    def __init__(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
            scope=os.getenv("SPOTIFY_SCOPE")
        ))

    def play_pause(self):
        try:
            playback = self.sp.current_playback()
            if playback and playback["is_playing"]:
                self.sp.pause_playback()
            else:
                self.sp.start_playback()
        except Exception as e:
            print(f"[SPOTIFY ERROR] {e}")

    def next(self):
        self.sp.next_track()

    def previous(self):
        self.sp.previous_track()

    def set_volume(self, volume):
        self.sp.volume(volume)

    def search_and_play(self, query):
        try:
            results = self.sp.search(q=query, type="track", limit=1)
            tracks = results["tracks"]["items"]

            if tracks:
                track_uri = tracks[0]["uri"]
                self.sp.start_playback(uris=[track_uri])
                return True
            else:
                print("[SPOTIFY] No results found")
                return False

        except Exception as e:
            print(f"[SPOTIFY ERROR] {e}")
            return False