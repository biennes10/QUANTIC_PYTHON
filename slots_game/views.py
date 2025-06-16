# slots_game/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import random
from .forms import CustomUserCreationForm
from .models import CustomUser # Importez CustomUser

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home') # Redirige vers la page d'accueil du jeu après inscription
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def slots_game_view(request):
    user = request.user
    message = ""
    current_slots = ["?", "?", "?"] # Initial display

    if request.method == 'POST':
        bet_amount = int(request.POST.get('bet_amount', 0))

        if bet_amount <= 0:
            message = "Veuillez entrer un montant de pari valide."
        elif user.balance < bet_amount:
            message = "Fonds insuffisants pour ce pari."
        else:
            user.balance -= bet_amount # Déduire le pari

            symbols = ["🍒", "🍋", "🍊", "🔔", "⭐", "💎"]
            result = [random.choice(symbols) for _ in range(3)]

            win_multiplier = 0
            if result[0] == result[1] == result[2]:
                win_multiplier = 5
            elif result[0] == result[1] or result[1] == result[2]:
                win_multiplier = 2

            won_amount = bet_amount * win_multiplier
            user.balance += won_amount

            user.save()

            if won_amount > 0:
                message = f"Félicitations ! Vous avez gagné {won_amount} pièces. Votre nouveau solde est de {user.balance}."
            else:
                message = f"Dommage ! Votre nouveau solde est de {user.balance}."
            current_slots = result

        return JsonResponse({'message': message, 'balance': user.balance, 'result': current_slots})

    return render(request, 'slots_game/game.html', {'user': user, 'message': message, 'current_slots': current_slots})