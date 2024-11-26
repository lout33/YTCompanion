import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class ChatHandler:
    def __init__(self):
        self.conversation_history = []
        self.transcript = None

    def set_transcript(self, transcript):
        # Format transcript for context
        transcript_text = "\n".join([f"{entry['timestamp']}: {entry['text']}" for entry in transcript])
        self.transcript = transcript_text
        
        # Initialize conversation with system message
        self.conversation_history = [{
            "role": "system",
            "content": f"You are a helpful AI assistant discussing a YouTube video. Here's the video transcript:\n\n{transcript_text}\n\nPlease help answer questions about the video content."
        }]

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

            # Add assistant's response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_response
            })

            return assistant_response

        except Exception as e:
            return f"Error: {str(e)}"
