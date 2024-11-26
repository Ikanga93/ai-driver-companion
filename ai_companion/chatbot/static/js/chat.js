// chatbot/static/js/chat.js

const startButton = document.getElementById('start-chat');
const stopButton = document.getElementById('stop-chat');
const responseAudio = document.getElementById('responseAudio');

let mediaRecorder;
let audioChunks = [];
let socket;
const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
const socketUrl = `${protocol}${window.location.host}/ws/chat/`;

document.addEventListener('DOMContentLoaded', () => {
    const startButton = document.getElementById('start-chat');
    const stopButton = document.getElementById('stop-chat');
    const responseAudio = document.getElementById('responseAudio');

    startButton.addEventListener('click', async () => {
        socket = new WebSocket(socketUrl);
    
        socket.onopen = () => {
            console.log('WebSocket connection established');
            startRecording();
        };
    
        socket.onmessage = (e) => {
            const data = JSON.parse(e.data);
            if (data.message) {
                const audioResponse = data.message;
                responseAudio.src = 'data:audio/wav;base64,' + audioResponse;
                responseAudio.play();
            } else if (data.error) {
                console.error('Error:', data.error);
                document.getElementById('error-message').innerText = data.error;
            }
        };
    
        socket.onclose = () => {
            console.log('WebSocket connection closed');
        };
    });
    
    stopButton.addEventListener('click', () => {
        stopRecording();
        if (socket) {
            socket.close();
        }
    });
    
    function startRecording() {
        startButton.disabled = true;
        stopButton.disabled = false;
        startButton.innerText = 'Recording...';

        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/wav' });
                mediaRecorder.start();
    
                mediaRecorder.ondataavailable = event => {
                    audioChunks.push(event.data);
                };
    
                mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    const reader = new FileReader();
                    reader.readAsDataURL(audioBlob);
                    reader.onloadend = () => {
                        const base64Audio = reader.result.split(',')[1];
                        sendAudio(base64Audio);
                    };
                    audioChunks = [];
                };
            })
            .catch(error => {
                console.error('Error accessing microphone:', error);
            });
    }
    
    function stopRecording() {
        mediaRecorder.stop();
        startButton.disabled = false;
        stopButton.disabled = true;
        startButton.innerText = 'Start Conversation';
    }
    
    function sendAudio(audio) {
        socket.send(JSON.stringify({ 'audio': audio }));
    }
    
});
