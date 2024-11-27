"""
ASGI config for ai_companion project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

# ai_companion/asgi.py

import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from django.conf import settings
import chatbot.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_companion.settings')
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chatbot.routing.websocket_urlpatterns
        )
    ),
})

if settings.DEBUG:
    from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
    application = ASGIStaticFilesHandler(application)

'''
Explanation:

asgi.py is configured to route WebSocket connections using the URL patterns defined in chatbot.routing.
AuthMiddlewareStack ensures that the user authentication is available in your WebSocket consumers.
'''