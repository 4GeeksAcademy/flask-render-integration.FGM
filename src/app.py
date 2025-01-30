import os
from flask import Flask, request, render_template
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
import plotly.express as px

# Load .env variables from the correct path
load_dotenv(dotenv_path='/workspaces/flask-render-integration.FGM/src/templates/flask_project.env')

# Initialize Spotify API
client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")

# Initialize Spotify client
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
spy = spotipy.Spotify(auth_manager=auth_manager)

# Flask App
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    artist_info = None
    tracks = []
    graph = None

    if request.method == "POST":
        artist_id = request.form["artist_id"]
        print(f"Artist ID entered: {artist_id}")  # Log the entered artist ID

        try:
            # Get artist details
            artist_data = spy.artist(artist_id)
            print(f"Artist Data: {artist_data}")  # Log the response from the API
            artist_name = artist_data["name"]
            artist_image = artist_data["images"][0]["url"] if artist_data["images"] else "default_image_url.png"  # Use default if no image

            # Get top 10 tracks
            top_tracks = spy.artist_top_tracks(artist_id, country="US")

            tracks = []
            for track in top_tracks["tracks"][:10]:
                track_name = track["name"]
                duration_ms = track["duration_ms"]
                popularity = track["popularity"]

                tracks.append({
                    "track_name": track_name,
                    "duration_min": duration_ms // 60000,
                    "duration_sec": (duration_ms % 60000) // 1000,
                    "popularity": popularity
                })

            # Prepare data for chart
            track_names = []
            popularity_values = []

            for track in tracks:
                track_names.append(track["track_name"])
                popularity_values.append(track["popularity"])

            # Create a bar chart for top track popularity
            fig = px.bar(x=track_names, y=popularity_values, labels={'x': 'Track Name', 'y': 'Popularity'},
                         title=f"Top Tracks Popularity for {artist_name}")
            graph = fig.to_html(full_html=False)

            artist_info = {
                "name": artist_name,
                "image": artist_image,
            }

        except Exception as e:
            print(f"Error: {e}")  # Log the error for more details
            artist_info = {"error": "Invalid Artist ID or API error"}

    return render_template("index.html", artist_info=artist_info, tracks=tracks, graph=graph)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

