# %%

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import pandas as pd

# %%

pd.set_option("display.max_columns", None)

# %%

playlist_uris = [
    "spotify:playlist:0Key2CHMeBfBeX0PyEWjQT",  # to_sort, aka. Liked Songs
    "spotify:playlist:1Cf4ecd7gATNgAFunsOoal",  # Tropics
    "spotify:playlist:544GfoOgsaeS8hJQRGS0H1",  # dreamy
]

AUDIO_FEATURES = [
    "danceability",
    "energy",
    "key",
    "loudness",
    "mode",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
    "duration_ms",
    "time_signature",
]

TRACK_FEATURES = [
    "album",
    "artists",
    "explicit",
    "name",
    "popularity",
]

# %%

auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

# %%

liked_playlist = sp.playlist(playlist_uris[0])
liked_tracks = liked_playlist["tracks"]

# %%

playlists = sp.user_playlists("eazhi_zhane")
while playlists:
    playlist = playlists["items"][0]
    print(playlist["uri"], playlist["name"])

    if playlists["next"]:
        playlists = sp.next(playlists)
    else:
        playlists = None

# %%
playlists = sp.user_playlists("eazhi_zhane")
while playlists:
    for i, playlist in enumerate(playlists["items"]):
        print(
            "%4d %s %s"
            % (i + 1 + playlists["offset"], playlist["uri"], playlist["name"])
        )
    if playlists["next"]:
        playlists = sp.next(playlists)
    else:
        playlists = None
# %%
tracks = []

for i in range(50):
    tracks.append(liked_tracks["items"][i]["track"])
# %%


def get_tracks_from_playlist(playlist_uri):
    playlist_id = playlist_uri.split(":")[2]
    playlist = sp.playlist(playlist_uri)

    tracks = []

    offset = 0
    while True:
        results = sp.playlist_tracks(playlist_id, offset=offset)
        tracks += results["items"]
        if results["next"] is not None:
            offset += 100
        else:
            break

    return tracks


def track_extract_features(track_uri):
    audio_features = sp.audio_features(track_uri)[0]
    audio_features = {k: v for k, v in audio_features.items() if k in AUDIO_FEATURES}

    track_features = sp.track(track_uri)
    track_features = {k: v for k, v in track_features.items() if k in TRACK_FEATURES}

    return {**audio_features, **track_features, "track_uri": track_uri}


def extract_uri_from_track(track):
    return track["track"]["uri"]


FEATURES = AUDIO_FEATURES + [
    "artists",
    "explicit",
    "name",
    "popularity",
    "album.album_type",
    "album.name",
    "album.release_date",
    "track_uri",
]


def extract_artists(row):
    return row["artists"]["name"]


# %%
liked_tracks = get_tracks_from_playlist(playlist_uris[0])
liked_track_uris = map(extract_uri_from_track, liked_tracks)
liked_tracks_features = map(track_extract_features, liked_track_uris)

# %%
df_liked_tracks = pd.json_normalize(liked_tracks_features)
df_liked_tracks = df_liked_tracks[FEATURES]
df_liked_tracks["artists"] = df_liked_tracks.apply(
    lambda row: [artist["name"] for artist in row["artists"]], axis=1
)
df_liked_tracks = df_liked_tracks.explode("artists")
# %%
