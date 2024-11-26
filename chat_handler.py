import os
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class ChatHandler:
    def __init__(self):
        self.conversation_history = []
        self.transcript = None
        self.timestamp_map = {}  # Store timestamp mappings

    def set_transcript(self, transcript):
        # Store timestamp mappings
        self.timestamp_map = {entry['timestamp']: entry['start'] for entry in transcript}
        
        # Format transcript for context
        transcript_text = "\n".join([f"{entry['timestamp']}: {entry['text']}" for entry in transcript])
        self.transcript = transcript_text
        
        # Initialize conversation with system message
        self.conversation_history = [{
            "role": "system",
            "content": f"You are a helpful AI assistant discussing a YouTube video. Here's the video transcript:\n\n{transcript_text}\n\nWhen referring to specific moments in the video, always include the timestamp in MM:SS format. Format timestamps exactly like they appear in the transcript (e.g., '01:23'). This is important for the user to navigate the video."
        }]

    def process_response(self, response):
        # Find all timestamps in the format MM:SS
        timestamp_pattern = r'\b\d{2}:\d{2}\b'
        
        # Replace timestamps with clickable spans
        def replace_timestamp(match):
            timestamp = match.group(0)
            if timestamp in self.timestamp_map:
                seconds = self.timestamp_map[timestamp]
                return f'<span class="ai-timestamp" data-time="{seconds}">{timestamp}</span>'
            return timestamp

        processed_response = re.sub(timestamp_pattern, replace_timestamp, response)
        return processed_response

    def send_message(self, message):
        if not self.transcript:
            return "Error: No video transcript loaded yet."

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": message
        })

        try:
            # Get response from OpenAI
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=self.conversation_history,
                max_tokens=500
            )

            # Extract assistant's response
            assistant_response = response.choices[0].message.content

            # Process response to add clickable timestamps
            processed_response = self.process_response(assistant_response)

            # Add original response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_response
            })

            return processed_response

        except Exception as e:
            return f"Error: {str(e)}"
