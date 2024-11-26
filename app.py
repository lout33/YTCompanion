from flask import Flask, render_template, request, jsonify
from get_transcript import get_video_transcript
from chat_handler import ChatHandler
import re

app = Flask(__name__)
chat_handler = ChatHandler()

def extract_video_id(url):
    # Extract video ID from various YouTube URL formats
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    match = re.match(youtube_regex, url)
    return match.group(6) if match else None

@app.route('/', methods=['GET', 'POST'])
def index():
    transcript = None
    error = None
    video_id = None
    
    if request.method == 'POST':
        video_url = request.form.get('video_url')
        video_id = extract_video_id(video_url)
        
        if not video_id:
            error = "Error: Invalid YouTube URL"
        else:
            result = get_video_transcript(video_url)
            if isinstance(result, str) and result.startswith('Error:'):
                error = result
            else:
                transcript = result
                chat_handler.set_transcript(result)
    
    return render_template('index.html', transcript=transcript, error=error, video_id=video_id)

@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.json.get('message')
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    response = chat_handler.send_message(message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
