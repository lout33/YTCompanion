from youtube_transcript_api import YouTubeTranscriptApi
import sys

def format_timestamp(seconds):
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    return f"{minutes:02d}:{remaining_seconds:02d}"

def get_video_transcript(video_url):
    try:
        # Extract video ID from URL
        if "youtube.com" in video_url:
            video_id = video_url.split("v=")[1].split("&")[0]
        elif "youtu.be" in video_url:
            video_id = video_url.split("/")[-1].split("?")[0]
        else:
            return "Error: Invalid YouTube URL"

        # Get transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Format transcript with timestamps
        formatted_transcript = []
        for entry in transcript:
            timestamp = format_timestamp(entry['start'])
            formatted_transcript.append({
                'text': entry['text'],
                'start': entry['start'],
                'timestamp': timestamp
            })
        
        return formatted_transcript

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python get_transcript.py <youtube_url>")
        sys.exit(1)
    
    video_url = sys.argv[1]
    print(get_video_transcript(video_url))
