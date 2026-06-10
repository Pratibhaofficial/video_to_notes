import yt_dlp
import os

def download_youtube_audio(url: str, output_dir: str = "uploads") -> str:
    """Downloads audio from a YouTube URL, returns path to .mp3 file"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "yt_audio")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return output_path + ".mp3"
    
    except Exception as e:
        raise Exception(f"Failed to download YouTube video: {str(e)}")