let player;
let currentVideoId = '';

// Initialize YouTube Player API
function onYouTubeIframeAPIReady() {
    player = new YT.Player('player', {
        height: '100%',
        width: '100%',
        videoId: '',
        playerVars: {
            'playsinline': 1,
            'origin': window.location.origin,
            'enablejsapi': 1,
            'rel': 0,
            'modestbranding': 1
        },
        events: {
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange,
            'onError': onPlayerError
        }
    });
}

function onPlayerReady(event) {
    addSystemMessage('YouTube player is ready. Please enter a video URL.');
}

function onPlayerStateChange(event) {
    switch(event.data) {
        case YT.PlayerState.PLAYING:
            addSystemMessage('Video started playing');
            break;
        case YT.PlayerState.PAUSED:
            addSystemMessage('Video paused');
            break;
        case YT.PlayerState.ENDED:
            addSystemMessage('Video ended');
            break;
    }
}

function onPlayerError(event) {
    let errorMessage = 'An error occurred with the video player: ';
    switch(event.data) {
        case 2:
            errorMessage += 'Invalid video ID';
            break;
        case 5:
            errorMessage += 'HTML5 player error';
            break;
        case 100:
            errorMessage += 'Video not found';
            break;
        case 101:
        case 150:
            errorMessage += 'Video playback not allowed';
            break;
        default:
            errorMessage += 'Unknown error';
    }
    addSystemMessage(errorMessage);
}

// Extract video ID from YouTube URL
function getVideoId(url) {
    try {
        url = url.trim();
        if (!url.startsWith('http')) {
            url = 'https://' + url;
        }
        const urlObj = new URL(url);
        let videoId = '';
        
        if (urlObj.hostname === 'youtu.be') {
            videoId = urlObj.pathname.slice(1);
        } else if (urlObj.hostname.includes('youtube.com')) {
            videoId = urlObj.searchParams.get('v');
        }
        
        if (videoId && videoId.length === 11) {
            return videoId;
        }
        return false;
    } catch (error) {
        console.error('Error parsing URL:', error);
        return false;
    }
}

// Handle URL input
document.querySelector('.url-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        const url = this.value;
        const videoId = getVideoId(url);
        
        if (videoId) {
            currentVideoId = videoId;
            player.loadVideoById(videoId);
            addSystemMessage('Loading video...');
        } else {
            addSystemMessage('Invalid YouTube URL. Please enter a valid YouTube URL (e.g., https://www.youtube.com/watch?v=...)');
        }
    }
});

// Chat functionality
const chatMessages = document.querySelector('#chat-messages');
const chatInput = document.querySelector('.chat-input');
const sendButton = document.querySelector('.send-button');

function addMessage(text, isUser = true) {
    const messageDiv = document.createElement('div');
    messageDiv.style.marginBottom = '10px';
    messageDiv.style.padding = '8px';
    messageDiv.style.borderRadius = '5px';
    messageDiv.style.maxWidth = '80%';
    messageDiv.style.wordWrap = 'break-word';
    
    if (isUser) {
        messageDiv.style.marginLeft = 'auto';
        messageDiv.style.backgroundColor = '#007bff';
        messageDiv.style.color = 'white';
    } else {
        messageDiv.style.marginRight = 'auto';
        messageDiv.style.backgroundColor = '#e9ecef';
        messageDiv.style.color = 'black';
    }
    
    messageDiv.textContent = text;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addSystemMessage(text) {
    addMessage(text, false);
}

function handleSendMessage() {
    const message = chatInput.value.trim();
    if (message) {
        addMessage(message, true);
        chatInput.value = '';
        
        // TODO: Implement AI response handling
        // For now, just echo a placeholder response
        setTimeout(() => {
            if (currentVideoId) {
                const timestamp = player.getCurrentTime();
                addSystemMessage(`Chatting about video at timestamp ${Math.floor(timestamp)} seconds. AI integration coming soon!`);
            } else {
                addSystemMessage('Please load a YouTube video first before starting the chat.');
            }
        }, 1000);
    }
}

sendButton.addEventListener('click', handleSendMessage);
chatInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        handleSendMessage();
    }
});

// Function to seek to specific timestamp
function seekTo(seconds) {
    if (player && typeof player.seekTo === 'function') {
        player.seekTo(seconds);
        player.playVideo();
    }
}

// Add click handlers for timestamps
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('timestamp') || e.target.classList.contains('ai-timestamp')) {
        const timestampText = e.target.textContent;
        const seconds = parseTimestamp(timestampText);
        if (!isNaN(seconds)) {
            seekTo(seconds);
        }
    }
});

// Helper function to parse timestamp text to seconds
function parseTimestamp(timestamp) {
    const parts = timestamp.split(':').reverse();
    let seconds = 0;
    for (let i = 0; i < parts.length; i++) {
        seconds += parseInt(parts[i]) * Math.pow(60, i);
    }
    return seconds;
}

// Initial system message
addSystemMessage('Welcome! Please enter a YouTube URL to get started.');
