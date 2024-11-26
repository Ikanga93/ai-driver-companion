"""
URL configuration for ai_companion project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# ai_companion/urls.py

from django.contrib import admin
from django.urls import path
from chatbot import views as chatbot_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', chatbot_views.index, name='index'),
    path('dashboard/', chatbot_views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='chatbot/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('signup/', chatbot_views.signup, name='signup'),
    path('checkout/', chatbot_views.checkout, name='checkout'),
    path('success/', chatbot_views.success, name='success'),
    path('cancel/', chatbot_views.cancel, name='cancel'),
    path('ws/chat/', chatbot_views.ChatConsumer.as_asgi()),
    path('webhook/', chatbot_views.stripe_webhook, name='stripe-webhook'),
]
