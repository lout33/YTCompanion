# YouTube AI Chat Assistant

YTCompanion: An interactive web application that enables users to have AI-powered conversations about YouTube videos. The application provides video transcription, summarization, and intelligent chat capabilities.

## Features

- **YouTube Video Integration**: Load and watch YouTube videos directly in the application
- **AI Transcription**: Generate accurate transcripts using OpenAI's Whisper API
- **Video Summarization**: Get AI-generated summaries of video content
- **Interactive Chat**: Have context-aware conversations about the video content
- **Timestamp Navigation**: Click on timestamps to jump to specific parts of the video
- **Multiple Views**: Switch between AI Chat, Regular Transcript, and AI Transcript views

## Prerequisites

- Python 3.8+
- OpenAI API key
- FFmpeg (for audio processing)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd yt_ai_chat
```

2. Install the required Python packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

1. Start the Flask server:
```bash
python app.py
```

2. Open your web browser and navigate to `http://localhost:5000`

3. Enter a YouTube URL in the input field and click "Load Video"

4. Use the toggle buttons to switch between:
   - AI Chat: Have conversations about the video content
   - Transcript: View the original video transcript
   - AI Transcript: View the AI-generated transcript with enhanced accuracy

## Project Structure

- `app.py`: Main Flask application server
- `ai_transcription.py`: Handles video transcription using OpenAI's Whisper API
- `summary_generator.py`: Generates video summaries
- `chat_handler.py`: Manages chat interactions
- `templates/`: HTML templates and frontend assets
- `static/`: Static files (CSS, JavaScript)

## Dependencies

Key dependencies include:
- Flask
- OpenAI
- yt-dlp
- FFmpeg-python
- pydub
- python-dotenv

For a complete list of dependencies, see `requirements.txt`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

Mit