import os
import yt_dlp as ydlp
from datetime import datetime

def download_audio_from_youtube(url):
    video_id = url.split("v=")[-1]
    current_date = datetime.now().strftime("%Y%m%d")

    output_directory = f"result/{current_date}"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_directory, f'{video_id}_{current_date}'),
        'ffmpeg_location': '/opt/homebrew/bin'  # ffmpeg 경로를 여기에 추가합니다.
    }

    with ydlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

if __name__ == "__main__":
    youtube_url = input("Enter the YouTube video URL: ")
    download_audio_from_youtube(youtube_url)
