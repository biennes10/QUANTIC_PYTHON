# slots_game/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import random
from .forms import CustomUserCreationForm
from .models import CustomUser # Importez CustomUser

from qiskit import QuantumCircuit, transpile
from qiskit.visualization import plot_histogram
from qiskit_aer import Aer
from qiskit_aer import AerSimulator

def welcome_view(request):
    """
    Vue pour la page d'accueil du site.
    """
    return render(request, 'slots_game/welcome.html')

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
            
            qc = QuantumCircuit(3,3)

            qc.h(0)
            qc.h(1)
            qc.h(2)
            qc.measure([0,1,2],[0,1,2])

            sim = AerSimulator()
            compiled_circuit = transpile(qc,sim)
            result = sim.run(compiled_circuit, shots=3).result()
            counts = result.get_counts()


            result = []

            for b, freq in counts.items():
                value = int(b, 2)
                capped_value = min(value, 5)
                result.extend([capped_value] * freq)
          


            win_multiplier = 0
            if result[0] == result[1] == result[2]:
                win_multiplier = 5
            elif result[0] == result[1] or result[1] == result[2] or result[0] == result[2]:
                win_multiplier = 2

            won_amount = bet_amount * win_multiplier
            user.balance += won_amount

            user.save()

            if won_amount > 0:
                message = f"Félicitations ! Vous avez gagné {won_amount} pièces. Votre nouveau solde est de {user.balance}."
            else:
                message = f"Dommage ! Votre nouveau solde est de {user.balance}."
            current_slots = []
            for i in result:
                current_slots.append(symbols[i])
            

        return JsonResponse({'message': message, 'balance': user.balance, 'result': current_slots})

    return render(request, 'slots_game/game.html', {'user': user, 'message': message, 'current_slots': current_slots})