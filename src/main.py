from time import sleep, time
import jellyfin_apiclient_python as jap
from jellyfin_apiclient_python.connection_manager import CONNECTION_STATE
from assets_handler import upload_image
from constants import ADDRESS, CLIENT_VERSION, PASSWORD, USER_APP_NAME, USERNAME
from presence import connect_presence


client = jap.JellyfinClient()
client.config.app(USER_APP_NAME, CLIENT_VERSION, "Discord Rich Presence", "1a2b3c4d")
client.config.data["auth.ssl"] = False
client.auth.connect_to_address(ADDRESS)
result = client.auth.login(ADDRESS, USERNAME, PASSWORD)
credentials = client.get_credentials()


server = credentials["Servers"][0]
user_id = server["UserId"]
state = client.authenticate({"Servers": [server]}, discover=False)
if state["State"] == CONNECTION_STATE["SignedIn"]:
    client.start(websocket=True)

paused_image = (
    "https://cdn.discordapp.com/app-assets/463097721130188830/493061640296595456.png"
)
playing_image = (
    "https://cdn.discordapp.com/app-assets/463097721130188830/493061639994867714.png"
)
presence = connect_presence()

last_id = None

while True:
    session = client.jellyfin.get_sessions()[0]

    try:
        now_playing = session["NowPlayingItem"]
        is_paused = session["PlayState"]["IsPaused"]
        try:
            series_name = now_playing["SeriesName"]
            series_season = now_playing["SeasonName"]
            series_episode = (
                "Ep." + str(now_playing["IndexNumber"]) + " - " + now_playing["Name"]
            )
            series_id = now_playing["SeriesId"]
            if series_id != last_id:
                series_image = upload_image(client, series_id)
                last_id = series_id

            if is_paused:
                presence.update(
                    details=series_name + " - " + series_season,
                    state=series_episode,
                    large_image=series_image,
                    large_text=series_name,
                    small_image=paused_image,
                    small_text="Paused",
                )
            else:
                time_ticks = session["PlayState"]["PositionTicks"]
                runtime_ticks = now_playing["RunTimeTicks"]
                epoch_end_time = int(time()) + (runtime_ticks - time_ticks) / 10000000
                presence.update(
                    details=series_name + " - " + series_season,
                    state=series_episode,
                    large_image=series_image,
                    large_text=series_name,
                    small_image=playing_image,
                    small_text="Playing",
                    end=epoch_end_time,
                )

        except KeyError:
            movie_id = now_playing["Id"]
            if movie_id != last_id:
                movie_image = upload_image(client, movie_id)
                last_id = movie_id

            if is_paused:
                presence.update(
                    details=now_playing["Name"],
                    large_image=movie_image,
                    large_text=now_playing["Name"],
                    small_image=paused_image,
                    small_text="Paused",
                )
            else:
                time_ticks = session["PlayState"]["PositionTicks"]
                runtime_ticks = now_playing["RunTimeTicks"]
                epoch_end_time = int(time()) + (runtime_ticks - time_ticks) / 10000000
                presence.update(
                    details=now_playing["Name"],
                    large_image=movie_image,
                    large_text=now_playing["Name"],
                    small_image=playing_image,
                    small_text="Playing",
                    end=epoch_end_time,
                )

    except KeyError:
        presence.clear()
        sleep(5)
