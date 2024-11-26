from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from get_transcript import get_video_transcript
from chat_handler import ChatHandler
from ai_transcription import transcribe_audio
from summary_generator import generate_summary
import re
import os

app = Flask(__name__)
CORS(app)
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

@app.route('/generate_ai_transcript', methods=['POST'])
def generate_ai_transcript():
    video_id = request.json.get('video_id')
    if not video_id:
        return jsonify({'error': 'No video ID provided'}), 400
    
    try:
        # Validate video ID format
        if not re.match(r'^[A-Za-z0-9_-]{11}$', video_id):
            return jsonify({'error': 'Invalid video ID format'}), 400
            
        transcript = transcribe_audio(video_id)
        
        if not transcript:
            return jsonify({'error': 'Failed to generate transcript'}), 500
        
        # Generate summary from the AI transcript
        try:
            summary = generate_summary(transcript)
            return jsonify({
                'transcript': transcript,
                'summary': summary
            })
        except Exception as summary_error:
            print(f"Error generating summary: {str(summary_error)}")
            # Return transcript even if summary fails
            return jsonify({
                'transcript': transcript,
                'summary_error': str(summary_error)
            })
            
    except Exception as e:
        import traceback
        error_msg = str(e)
        trace = traceback.format_exc()
        print("Error in generate_ai_transcript:", error_msg)
        print("Traceback:", trace)
        
        # Provide a more user-friendly error message
        user_msg = "Failed to process video"
        if "Error downloading audio" in error_msg:
            user_msg = "Failed to download video audio. Please check if the video exists and is accessible."
        elif "Error converting audio" in error_msg:
            user_msg = "Failed to process audio. The video might be too long or in an unsupported format."
        
        return jsonify({
            'error': user_msg,
            'details': error_msg
        }), 500

@app.route('/generate_summary', methods=['POST'])
def generate_video_summary():
    """Generate a summary for either type of transcript."""
    try:
        data = request.json
        transcript = data.get('transcript')
        video_title = data.get('title')
        
        if not transcript:
            return jsonify({'error': 'No transcript provided'}), 400
            
        summary = generate_summary(transcript, video_title)
        return jsonify({'summary': summary})
        
    except Exception as e:
        print(f"Error in generate_summary: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
