from pytube import YouTube, Playlist, Channel
from colorama import Fore, init
from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython import VideosSearch
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_audio

import spotipy
import time
import sys
import os
import re

options = Fore.RED + """
1. Youtube Video Downloader
2. Youtube To MP3 Downloader
3. Youtube Playlist Downloader
4. Spotify Song Downloader
5. YouTube Channel Video Downloader
0. Exit
"""

choices = [1, 2, 3, 4, 5, 0]

init(autoreset=True)
cwd = os.getcwd()

creds = os.path.join(cwd, "creds.txt")

yt_vid_output_folder = os.path.join(cwd, "content", "videos")
yt_audio_output_folder = os.path.join(cwd, "content", "audio")
yt_playlist_output_folder = os.path.join(cwd, "content", "yt_playlist_video")
spotify_audio_output_folder = os.path.join(cwd, "content", "spotify_audio")
channel_videos_output = os.path.join(cwd, "content", "channel_videos")

if not os.path.exists(yt_vid_output_folder):
    os.makedirs(yt_vid_output_folder)
if not os.path.exists(yt_audio_output_folder):
    os.makedirs(yt_audio_output_folder)
if not os.path.exists(yt_playlist_output_folder):
    os.makedirs(yt_playlist_output_folder)
if not os.path.exists(spotify_audio_output_folder):
    os.makedirs(spotify_audio_output_folder)
if not os.path.exists(channel_videos_output):
    os.makedirs(channel_videos_output)

def sanitize_filename(filename):
    invalid_chars = r'<>:"/\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    return filename

def yt_audio_downloader():
    try:
        audio_link = input(Fore.GREEN + "Enter YouTube Link >> ")
        yt = YouTube(audio_link)
        video = yt.streams.filter(only_audio=True).first()
        print(Fore.RED + f"Downloading {yt.streams[0].title} To {yt_audio_output_folder}")
        down = video.download(output_path=yt_audio_output_folder)
        base, extension = os.path.splitext(down)
        new_file = base + '.mp3'
        print(Fore.RED + "Encoding To mp3")
        original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

        ffmpeg_extract_audio(down, new_file)
        os.remove(down)
        sys.stdout = original_stdout
        print(Fore.GREEN +  f"{yt.streams[0].title} Downloaded to {yt_audio_output_folder}")
        time.sleep(1)
        start()

    except Exception as e:
        print(Fore.RED + f"{e}")
        print(Fore.RED + "Error could be caused due to no internet or an invalid link")
        time.sleep(1)
        start()

def yt_video_downloader():
    try:
        video_link = input(Fore.GREEN + "Enter YouTube Link >> ")
        yt = YouTube(video_link)
        print(Fore.RED + "Fetching Available Resolutions:")
        resolutions = set()
        for stream in yt.streams:
            if stream.resolution:
                resolutions.add(stream.resolution)

        sorted_resolutions = sorted(resolutions, key=lambda x: int(x[:-1]))

        for resolution in sorted_resolutions:
            print(Fore.BLUE + f"{resolution}")
        resolution_opt = input(Fore.RED + "Which Resolution: ")
        if resolution_opt in resolutions:
            try:
                sanitized_title = sanitize_filename(yt.title)
                print(Fore.RED + f"DOWNLOADING: {sanitized_title} in {resolution_opt}")
                
                output_path = os.path.join(yt_vid_output_folder, f"{sanitized_title}.{resolution_opt}.mp4")
                yt.streams.filter(res=resolution_opt).first().download(output_path)
                print(Fore.GREEN + f"{sanitized_title} Successfully Downloaded To {yt_vid_output_folder}")   
                time.sleep(1)
                start()
            except Exception as e:
                print(Fore.RED + f"{e}")
                time.sleep(1)
                start()
        else:
            print(Fore.RED + f"{resolution_opt} isn't an option")
            time.sleep(1)
            start()

    except Exception as e:
        print(Fore.RED + f"{e}")
        print(Fore.RED + "Error could be caused due to no internet or an invalid link")
        time.sleep(1)
        start()
        
def yt_playlist_downloader():
    playlist_url = input(Fore.GREEN + "Enter YouTube playlist URL: ")
    resolution = input(Fore.GREEN + "Enter Resolution (e.g., 720, 1080) dont add the p: ")
    print(Fore.RED + f"This Will Try To Download Your playlist Videos In {resolution}p However It May Have To Compromise For another Resolution")
    input(Fore.RED + "Press Enter To Continue")
    playlist = Playlist(playlist_url)

    resolution_stream = None

    for video in playlist.video_urls:
        yt = YouTube(video)
        stream = yt.streams.filter(res=f'{resolution}p', progressive=True).first()
        if stream:
            resolution_stream = stream
            break

    for video_url in playlist.video_urls:
        yt = YouTube(video_url)
        print(Fore.RED + f"Downloading {yt.title}")
        resolution_stream = yt.streams.filter(res=f'{resolution}p', progressive=True).first()

        if resolution_stream:
            download_path = os.path.join(yt_playlist_output_folder, f"{yt.title}.mp4")
            resolution_stream.download(yt_playlist_output_folder)
            print(Fore.GREEN + f"{yt.title} Downloaded to {download_path}")
        else:
            print(Fore.YELLOW + f"Unable to find suitable resolution for {yt.title}. Skipping.")
            continue

def spotify_song_downloader_keywords():

    print(Fore.RED + "Takes Spotify Song Input (Not Url) As Keywords")
    input(Fore.RED + "Press Enter To Continue")

    def get_spotify_track_keywords(user_input, client_id, client_secret):
        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
        search = sp.search(q=user_input, type="track", limit=1)

        if search['tracks']['items']:
            track_info = search['tracks']['items'][0]
            return track_info
        else:
            return None
    try:
        if not os.path.exists(creds):
            print(Fore.RED + f"Creds.txt Doesnt Exist In {cwd}, Creating it now")
            client_id_inp = input(Fore.GREEN + "Spotify Developer Client ID: ")
            client_secret_inp = input(Fore.GREEN + "Spotify Developer Client Secret: ")
            with open("creds.txt", "w") as o:
                o.write(f"{client_id_inp}\n")
                o.write(client_secret_inp)
                o.close()
        else: 
            pass
        
        with open("creds.txt", "r") as o:
            content = o.readlines()
            client_id = content[0].strip('\n')
            client_secret = content[1]

            user_input = input(Fore.GREEN + "Enter the name of the Spotify song (add artist name for extra filtering - e.g. song artist): ")
            track_info = get_spotify_track_keywords(user_input, client_id, client_secret)

            if track_info:
                artist_name = track_info['artists'][0]['name']
                track_name = track_info['name']
                query = f"{artist_name} {track_name}"

                videos_search = VideosSearch(query, limit = 1)
                results = videos_search.result()

                if results['result']:
                    video_url = results['result'][0]['link']
                    
                    try:
                        audio_link = video_url
                        yt = YouTube(audio_link)
                        video = yt.streams.filter(only_audio=True).first()
                        print(Fore.RED + f"Downloading {user_input} To {spotify_audio_output_folder}")
                        down = video.download(output_path=spotify_audio_output_folder)
                        base, extension = os.path.splitext(down)
                        new_file = base + '.mp3'
                        print(Fore.RED + "Encoding To mp3")
                        original_stdout = sys.stdout
                        sys.stdout = open(os.devnull, 'w')
                        
                        ffmpeg_extract_audio(down, new_file)
                        os.remove(down)
                        sys.stdout = original_stdout
                        print(Fore.GREEN +  f"{user_input} Downloaded to {spotify_audio_output_folder}")
                        time.sleep(1)
                        start()

                    except Exception as e:
                        print(Fore.RED + f"{e}")
                        print(Fore.RED + "Error could be caused due to no internet or an invalid link")
                        time.sleep(1)
                        start()
                else:
                    print(Fore.RED + "No Results Found On YouTube For The Given Track")
                    time.sleep(1)
                    start()
            else:
                print(Fore.RED + "Track Not Found On Spotify")
                time.sleep(1)
                start()       
    except Exception as e:
        print(Fore.RED + e)
        time.sleep(1)
        start()

def get_spotify_track_url():

    print(Fore.RED + "Takes Spotify Song Input URL")
    input(Fore.RED + "Press Enter To Continue")

    def get_spotify_track_by_url(client_id, client_secret):
        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
        URL = input(Fore.GREEN + "Spotify Track URL: ")

        track_id_match = re.search(r'/track/([a-zA-Z0-9]+)', URL)
        if not track_id_match:
            raise ValueError("Invalid Spotify track URL")
        track_id = track_id_match.group(1)
        track_info = sp.track(track_id)

        song_name = track_info['name']
        artists = ', '.join([artist['name'] for artist in track_info['artists']])

        return song_name, artists

    try:
        if not os.path.exists(creds):
            print(Fore.RED + f"Creds.txt Doesnt Exist In {cwd}, Creating it now")
            client_id_inp = input(Fore.GREEN + "Spotify Developer Client ID: ")
            client_secret_inp = input(Fore.GREEN + "Spotify Developer Client Secret: ")
            with open("creds.txt", "w") as o:
                o.write(f"{client_id_inp}\n")
                o.write(client_secret_inp)
                o.close()
        else: 
            pass
        
        with open("creds.txt", "r") as o:
            content = o.readlines()
            client_id = content[0].strip('\n')
            client_secret = content[1]

            song_name, artists = get_spotify_track_by_url(client_id, client_secret)

            query = f"{song_name} {artists}"

            videos_search = VideosSearch(query, limit = 1)
            results = videos_search.result()

            if results['result']:
                video_url = results['result'][0]['link']

            try:
                audio_link = video_url
                yt = YouTube(audio_link)
                video = yt.streams.filter(only_audio=True).first()
                print(Fore.RED + f"Downloading {song_name} by {artists} To {spotify_audio_output_folder}")
                down = video.download(output_path=spotify_audio_output_folder)
                base, extension = os.path.splitext(down)
                new_file = base + '.mp3'
                print(Fore.RED + "Encoding To mp3")
                original_stdout = sys.stdout
                sys.stdout = open(os.devnull, 'w')

                ffmpeg_extract_audio(down, new_file)
                os.remove(down)
                sys.stdout = original_stdout
                print(Fore.GREEN + f"{song_name} by {artists} Downloaded to {spotify_audio_output_folder}")
                time.sleep(1)
                start()

            except Exception as e:
                print(Fore.RED + f"{e}")
                print(Fore.RED + "Error could be caused due to no internet or an invalid link")
                time.sleep(1)
                start()

    except Exception as e:
        print(Fore.RED + f"{e}")
        time.sleep(1)
        start()

def download_channel_videos():
    url = input(Fore.GREEN + 'To Get Url - YouTube Channel Homepage -> Scroll Down To "Videos > Play All" -> Right Click Play All -> Copy Link Address: ')
    try:
        resolution = input(Fore.GREEN + "Enter Resolution (e.g., 720, 1080) dont add the p: ")
        print(Fore.RED + f"This Will Try To Download Your Channel Videos In {resolution}p However It May Have To Compromise For another Resolution")
        input(Fore.RED + "Press Enter To Continue")
    except Exception as e:
        print(Fore.RED + f"{e}")
        
    channel = Playlist(url)

    for video in channel.video_urls:
        try:
            yt = YouTube(video)
            print(Fore.RED + f"DOWNLOADING {yt.title} to {channel_videos_output}")
            yt.streams.filter(res=f"{resolution}p", progressive=True).first().download(output_path=channel_videos_output)
            print(Fore.GREEN + f"{yt.title} Successfully Downloaded to {channel_videos_output}")

        except:
            try:
                yt = YouTube(video)
                try:
                    os.remove(f"{channel_videos_output}{yt.title}")
                except Exception as e:
                    print(Fore.RED + f"{e}")
                print(Fore.RED + f"DOWNLOADING {yt.title} to {channel_videos_output} In Alternative Resolution")
                yt.streams.filter(progressive=True).first().download(output_path=channel_videos_output)
                print(Fore.GREEN + f"{yt.title} Successfully Downloaded to {channel_videos_output}")
            except Exception as e:
                print(Fore.RED + f"{e}")
                time.sleep(1)
                start()

def main(choice):
    if choice in choices:
        try:
            if choice == 1:
                yt_video_downloader()
            elif choice == 2:
                yt_audio_downloader()
            elif choice == 3:
                yt_playlist_downloader()
            elif choice == 4:
                print(Fore.RED + """
1. Download From Keywords
2. Download From URL (For More Precision)
0. Back
""")
                try:
                    choice = int(input(Fore.GREEN + ">> "))
                except Exception as e:
                    print(Fore.RED + f"{e}")
                    time.sleep(1)
                    start()
                
                if choice == 1:
                    spotify_song_downloader_keywords()
                elif choice == 2:
                    get_spotify_track_url()
                elif choice == 0:
                    start()
                else:
                    print(Fore.RED + f"{choice} Isnt An Option")
                    time.sleep(1)
                    start()
                
            elif choice == 5:
                download_channel_videos()
            elif choice == 0:
                exit()
        except Exception as e:
            print(Fore.RED + f"{e}")    
    else:
        print(Fore.RED + f"{choice} isnt an option")
        time.sleep(1)
        start()

def start():
    print(options)
    try:
        choice = int(input(Fore.GREEN + ">> "))
        main(choice)
    except Exception as e:
        print(Fore.RED + f"{e}")
        time.sleep(1)
        start()

if __name__ == "__main__":

    print(Fore.RED + """

███████╗██████╗  ██████╗ ████████╗██╗████████╗██╗   ██╗██████╗ ███████╗
██╔════╝██╔══██╗██╔═══██╗╚══██╔══╝██║╚══██╔══╝██║   ██║██╔══██╗██╔════╝
███████╗██████╔╝██║   ██║   ██║   ██║   ██║   ██║   ██║██████╔╝█████╗  
╚════██║██╔═══╝ ██║   ██║   ██║   ██║   ██║   ██║   ██║██╔══██╗██╔══╝  
███████║██║     ╚██████╔╝   ██║   ██║   ██║   ╚██████╔╝██████╔╝███████╗
╚══════╝╚═╝      ╚═════╝    ╚═╝   ╚═╝   ╚═╝    ╚═════╝ ╚═════╝ ╚══════╝
                                                                       
                    written by: https://github.com/3022-2
            """)
    input(Fore.RED + """some video resolutions may not play (namely 240p and 480p). However these files are not corrupted 
          - try them in your browser. Press enter to continue""")
    start()