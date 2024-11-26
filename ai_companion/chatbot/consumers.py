# chatbot/consumers.py

import json
import base64
import asyncio
import websockets
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from pydub import AudioSegment
from io import BytesIO

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_authenticated:
            await self.accept()
            self.openai_ws = None
            self.openai_task = None
        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.openai_ws:
            await self.openai_ws.close()
        if self.openai_task:
            self.openai_task.cancel()

    async def receive(self, text_data):
        data = json.loads(text_data)
        audio_base64 = data.get('audio')

        if not audio_base64:
            await self.send(json.dumps({'error': 'No audio provided'}))
            return

        # Decode audio
        audio_bytes = base64.b64decode(audio_base64)
        audio = AudioSegment.from_file(BytesIO(audio_bytes), format="wav")
        pcm_audio = audio.set_frame_rate(24000).set_channels(1).set_sample_width(2).raw_data

        # Connect to OpenAI's Realtime API if not connected
        if not self.openai_ws:
            self.openai_ws = await websockets.connect(
                'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01',
                extra_headers={
                    'Authorization': f'Bearer {settings.OPENAI_API_KEY}',
                    'OpenAI-Beta': 'realtime=v1',
                }
            )
            # Send initial response.create event
            await self.openai_ws.send(json.dumps({
                "type": "response.create",
                "response": {
                    "modalities": ["audio"],
                    "instructions": "You are a friendly AI companion for truck drivers. Keep the conversation engaging and supportive."
                }
            }))
            # Start listening to OpenAI's responses
            self.openai_task = asyncio.create_task(self.listen_openai())

        # Send audio to OpenAI
        await self.openai_ws.send(json.dumps({
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [{
                    "type": "input_audio",
                    "audio": base64.b64encode(pcm_audio).decode('utf-8')
                }]
            }
        }))

    async def listen_openai(self):
        try:
            async for message in self.openai_ws:
                data = json.loads(message)
                if data.get('message') and data['message'].get('audio'):
                    audio_response = data['message']['audio']['data']
                    await self.send(json.dumps({'message': audio_response}))
                elif data.get('error'):
                    await self.send(json.dumps({'error': data['error']['message']}))
        except websockets.exceptions.ConnectionClosed:
            await self.close()
        except Exception as e:
            await self.send(json.dumps({'error': str(e)}))

'''
Explanation:

Connection Management:
On connect, verify if the user is authenticated.
Establish a WebSocket connection to OpenAI's Realtime API.
Receiving Audio:
Decode the incoming audio from base64.
Convert the audio to the required PCM format.
Send the audio data to OpenAI.
Listening to OpenAI:
Continuously listen for responses from OpenAI.
Upon receiving audio responses, send them back to the client.
Notes:

Asynchronous Handling: Ensures non-blocking operations for real-time interactions.
Error Handling: Basic error handling is implemented. Consider enhancing it for production.
Session Management: Currently, a single WebSocket connection per user is maintained. Adjust as needed.
'''