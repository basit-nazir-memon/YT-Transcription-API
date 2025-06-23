from fastapi import FastAPI, HTTPException, Query
from youtube_transcript_api import YouTubeTranscriptApi
import re
import math

app = FastAPI()

def extract_video_id(youtube_url: str) -> str:
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"youtu\.be\/([0-9A-Za-z_-]{11})"
    ]
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    raise ValueError("Invalid YouTube URL.")

def format_time(seconds: float) -> str:
    """Convert seconds to hh:mm:ss format."""
    total_seconds = int(math.floor(seconds))
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def get_captions_with_timestamps(youtube_url: str, language: str = 'en') -> str:
    video_id = extract_video_id(youtube_url)
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])

    formatted_captions = []

    for i, entry in enumerate(transcript):
        start = entry['start']
        duration = entry.get('duration', 0)
        end = start + duration
        start_str = format_time(start)
        end_str = format_time(end)
        text = entry['text'].replace('\n', ' ')
        formatted_captions.append(f"{start_str}-{end_str}:  {text}")

    result = "\n".join(formatted_captions)

    return result

@app.get("/")
def root():
    return {"message": "YouTube Caption Extractor API"}

@app.get("/captions/")
def extract_captions(youtube_url: str = Query(..., description="Full YouTube video URL")):
    try:
        captions = get_captions_with_timestamps(youtube_url)
        return {"captions": captions}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
