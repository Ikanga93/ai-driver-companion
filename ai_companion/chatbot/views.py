# chatbot/views.py

import base64
import json
import requests
import stripe
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def dashboard(request):
    return render(request, 'chatbot/dashboard.html')

def index(request):
    return render(request, 'chatbot/index.html')

def chat(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        audio_base64 = data.get('audio')

        if not audio_base64:
            return JsonResponse({'error': 'No audio provided'}, status=400)

        # Decode audio
        audio_bytes = base64.b64decode(audio_base64)

        # Send to OpenAI's API
        response = send_to_openai(audio_bytes)

        if response:
            return JsonResponse({'message': response})
        else:
            return JsonResponse({'error': 'Failed to process audio'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def send_to_openai(audio_bytes):
    api_key = settings.OPENAI_API_KEY
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        "model": "gpt-4o-audio-preview",
        "modalities": ["audio"],
        "audio": {
            "voice": "alloy",
            "format": "wav"
        },
        "messages": [
            {
                "role": "user",
                "content": None,  # Content is in audio
                "audio": {
                    "data": base64.b64encode(audio_bytes).decode('utf-8')
                }
            }
        ]
    }

    try:
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=payload)
        response_data = response.json()

        if 'choices' in response_data and len(response_data['choices']) > 0:
            audio_response = response_data['choices'][0]['message']['audio']['data']
            return audio_response
        else:
            return None
    except Exception as e:
        print(f"Error communicating with OpenAI: {e}")
        return None

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'chatbot/signup.html', {'form': form})

@login_required
def checkout(request):
    if request.method == 'POST':
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': 'price_1Hh1XYZ...',  # Replace with your Stripe Price ID
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.build_absolute_uri('/success/'),
            cancel_url=request.build_absolute_uri('/cancel/'),
        )
        return JsonResponse({'id': session.id})
    context = {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    }
    return render(request, 'chatbot/checkout.html', context)

def success(request):
    return render(request, 'chatbot/success.html')

def cancel(request):
    return render(request, 'chatbot/cancel.html')