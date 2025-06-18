# slots_game/urls.py

from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('', views.slots_game_view, name='home'), # Page d'accueil du jeu
    path('play_slots/', views.slots_game_view, name='play_slots'), # Endpoint pour le jeu via AJAX
    path('play_blackjack/', views.blackjack_game_view, name='play_blackjack'),
]