from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def format_transcript_for_summary(transcript):
    """Format transcript for summary generation based on its type."""
    if isinstance(transcript, list):
        # Check if it's an AI transcript (with timestamp and text fields)
        if transcript and isinstance(transcript[0], dict) and 'text' in transcript[0]:
            return " ".join(segment['text'] for segment in transcript)
        # Regular transcript list
        return " ".join(transcript)
    # If it's already a string
    return transcript

def generate_summary(transcript, video_title=None):
    """Generate a summary of the transcript using OpenAI's GPT model."""
    try:
        # Format the transcript text
        transcript_text = format_transcript_for_summary(transcript)
        
        # Prepare the prompt
        title_context = f"Title: {video_title}\n" if video_title else ""
        prompt = f"{title_context}Please provide a comprehensive summary of the following video transcript. " \
                f"Include the main topics discussed, key points, and any important conclusions. " \
                f"Format the response with bullet points for main topics and their key details:\n\n{transcript_text}"

        # Generate summary using OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates clear, concise video summaries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        raise Exception(f"Failed to generate summary: {str(e)}")
