# slots_game/urls.py

from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('', views.welcome_view, name='home'), # La page d'accueil principale
    path('play_slots/', views.slots_game_view, name='play_slots'), # Endpoint pour le jeu via AJAX
]