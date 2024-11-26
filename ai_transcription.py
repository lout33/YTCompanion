import os
import tempfile
import subprocess
from datetime import timedelta
from openai import OpenAI
import yt_dlp
from dotenv import load_dotenv
from pydub import AudioSegment

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def download_audio(video_id):
    """Download audio from YouTube video."""
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Create temp directory if it doesn't exist
        temp_dir = os.path.join(tempfile.gettempdir(), 'yt_transcripts')
        os.makedirs(temp_dir, exist_ok=True)
        
        output_template = os.path.join(temp_dir, f"{video_id}.%(ext)s")
        
        # Configure yt-dlp with multiple fallback options
        ydl_opts = {
            'format': 'bestaudio/best',  # Try best audio first
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_template,
            'quiet': False,
            'no_warnings': False,
            # Add multiple user agents to rotate
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            # Add fallback formats
            'format_sort': ['acodec:mp3', 'acodec:m4a', 'acodec:aac', 'acodec:*'],
            # Add network settings
            'socket_timeout': 30,
            'retries': 10,
            'fragment_retries': 10,
            'retry_sleep_functions': {'fragment': lambda n: 3 * (n + 1)},
            # Add more detailed error reporting
            'verbose': True,
            'extract_flat': False,
            # Add age gate bypass
            'age_limit': 25,
            'cookiesfrombrowser': None,  # Disable browser cookies on Heroku
        }
        
        # Try multiple download attempts with different settings
        exceptions = []
        
        # First attempt: Try with best audio
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            exceptions.append(f"Best audio attempt failed: {str(e)}")
            
            # Second attempt: Try with different format
            ydl_opts['format'] = 'worstaudio/worst'
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            except Exception as e:
                exceptions.append(f"Worst audio attempt failed: {str(e)}")
                
                # Third attempt: Try without postprocessing
                ydl_opts.pop('postprocessors')
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                except Exception as e:
                    exceptions.append(f"No postprocessing attempt failed: {str(e)}")
                    raise Exception(f"All download attempts failed:\n" + "\n".join(exceptions))
        
        # Find the output file (it will have .mp3 extension after post-processing)
        output_file = os.path.join(temp_dir, f"{video_id}.mp3")
        if not os.path.exists(output_file):
            # Try to find any audio file that was downloaded
            for ext in ['mp3', 'm4a', 'webm', 'opus']:
                test_file = os.path.join(temp_dir, f"{video_id}.{ext}")
                if os.path.exists(test_file):
                    output_file = test_file
                    break
        
        # Verify file exists and is not empty
        if not os.path.exists(output_file):
            raise Exception(f"Output file not found at {output_file}")
        if os.path.getsize(output_file) == 0:
            raise Exception("Downloaded file is empty")
            
        print(f"Successfully downloaded file to {output_file} with size {os.path.getsize(output_file)} bytes")
        return output_file
        
    except Exception as e:
        print(f"Error in download_audio: {str(e)}")
        # Clean up any partial downloads
        try:
            output_file = os.path.join(temp_dir, f"{video_id}.mp3")
            if os.path.exists(output_file):
                os.remove(output_file)
        except Exception as cleanup_error:
            print(f"Error during cleanup: {str(cleanup_error)}")
        raise Exception(f"Error downloading audio: {str(e)}")

def convert_audio_to_segments(audio_file):
    """Convert audio file to segments for processing."""
    try:
        # Verify file exists before processing
        if not os.path.exists(audio_file):
            raise Exception(f"Audio file not found: {audio_file}")
            
        segments = []
        
        # Load the audio file
        try:
            audio = AudioSegment.from_mp3(audio_file)
        except Exception as e:
            raise Exception(f"Failed to load audio file: {str(e)}")
        
        # Split into segments (10 minutes = 600000 milliseconds)
        segment_length = 600000
        
        for start in range(0, len(audio), segment_length):
            # Extract segment
            segment = audio[start:start + segment_length]
            
            # Create temp file for segment
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            try:
                segment.export(temp_file.name, format='mp3')
                segments.append({
                    'file': temp_file.name,
                    'start_time': start / 1000  # Convert to seconds
                })
            except Exception as e:
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
                raise Exception(f"Failed to export segment: {str(e)}")
        
        return segments
    except Exception as e:
        raise Exception(f"Error converting audio: {str(e)}")

def format_timestamp(seconds):
    """Convert seconds to HH:MM:SS format."""
    return str(timedelta(seconds=int(seconds)))

def transcribe_audio(video_id):
    """Generate AI transcript for a YouTube video."""
    audio_file = None
    segments = []
    previous_text = ""  # Store previous segment text for context
    
    try:
        # Download audio
        audio_file = download_audio(video_id)
        print(f"Successfully downloaded audio to: {audio_file}")
        
        # Verify file exists and is readable
        if not os.path.exists(audio_file):
            raise Exception(f"Downloaded audio file not found: {audio_file}")
            
        # Convert to segments
        segments = convert_audio_to_segments(audio_file)
        print(f"Created {len(segments)} segments")
        
        if not segments:
            raise Exception("No segments were created from the audio file")
        
        transcript = []
        for i, segment in enumerate(segments):
            try:
                if not os.path.exists(segment['file']):
                    print(f"Segment file {i+1} not found, skipping")
                    continue
                    
                print(f"Processing segment {i+1}/{len(segments)}")
                with open(segment['file'], 'rb') as audio:
                    # Use the previous text as prompt for context
                    response = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio,
                        response_format="verbose_json",
                        timestamp_granularities=["segment"],
                        prompt=previous_text[-200:] if previous_text else None  # Use last 200 chars as context
                    )
                
                # Process segment-level timestamps
                if hasattr(response, 'segments'):
                    for seg in response.segments:
                        absolute_start = segment['start_time'] + seg.start
                        absolute_end = segment['start_time'] + seg.end
                        transcript.append({
                            'start': absolute_start,
                            'end': absolute_end,
                            'timestamp': format_timestamp(absolute_start),
                            'end_timestamp': format_timestamp(absolute_end),
                            'text': seg.text.strip()
                        })
                    
                    # Update context for next segment
                    previous_text = response.text
                
            except Exception as e:
                print(f"Error processing segment {i+1}: {str(e)}")
                continue
            finally:
                # Clean up segment file
                try:
                    if os.path.exists(segment['file']):
                        os.unlink(segment['file'])
                except Exception as e:
                    print(f"Error cleaning up segment file: {str(e)}")
        
        if not transcript:
            raise Exception("No transcript was generated. Please try again.")
        
        return transcript
        
    except Exception as e:
        print(f"Error in transcribe_audio: {str(e)}")
        raise
    finally:
        # Clean up all temporary files
        try:
            if audio_file and os.path.exists(audio_file):
                os.unlink(audio_file)
            for segment in segments:
                if os.path.exists(segment['file']):
                    os.unlink(segment['file'])
        except Exception as e:
            print(f"Error in cleanup: {str(e)}")
