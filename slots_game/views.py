# slots_game/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import random
from .forms import CustomUserCreationForm
from .models import CustomUser # Importez CustomUser
from .quantum_shuffle import melanger_quantique

from qiskit import QuantumCircuit, transpile
from qiskit.visualization import plot_histogram
from qiskit_aer import Aer
from qiskit_aer import AerSimulator

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

@login_required
def blackjack_game_view(request):
    """
    - GET  : affiche la page et l’état courant (ou vide)
    - POST : actions bet / hit / stand (AJAX)
    L’état est stocké en session sous 'bj_state'.
    """
    user = request.user

    # ------- 1) Affichage initial -------
    if request.method == 'GET':
        state = request.session.get('bj_state', {})
        return render(request, 'blackjack_game/game.html',
                      {'user': user, 'state': state})

    # ------- 2) Appels AJAX -------
    action = request.POST.get('action')
    bet    = int(request.POST.get('bet', 0))
    state  = request.session.get('bj_state', {})

    # (a) Nouvelle mise / distribution
    if action == 'bet':
        if bet <= 0 or bet > user.balance:
            return JsonResponse({'error': 'Mise invalide.'}, status=400)

        deck   = create_deck()
        player = [deck.pop(), deck.pop()]
        dealer = [deck.pop(), deck.pop()]

        state = {
            'deck': deck,
            'player': player,
            'dealer': dealer,
            'bet': bet,
            'finished': False,
            'message': '',
        }
        user.balance -= bet
        user.save()

    # (b) Tirer
    elif action == 'hit' and not state.get('finished', True):
        state['player'].append(state['deck'].pop())
        if hand_value(state['player']) > 21:
            state['finished'] = True
            state['message']  = 'Bust ! Vous dépassez 21.'

    # (c) Rester
    elif action == 'stand' and not state.get('finished', True):
        while hand_value(state['dealer']) < 17:
            state['dealer'].append(state['deck'].pop())

        p_val = hand_value(state['player'])
        d_val = hand_value(state['dealer'])
        state['finished'] = True

        if d_val > 21 or p_val > d_val:
            gain = state['bet'] * 2
            user.balance += gain
            state['message'] = f'Vous gagnez {gain} pièces !'
        elif p_val == d_val:
            user.balance += state['bet']
            state['message'] = 'Égalité – mise rendue.'
        else:
            state['message'] = 'Le croupier gagne.'

        user.save()

    request.session['bj_state'] = state
    request.session.modified = True
    return JsonResponse({'state': state, 'balance': user.balance})

def create_deck():
    valeurs  = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
    couleurs = ['♠','♥','♦','♣']
    deck = [f"{v}{c}" for v in valeurs for c in couleurs]
    deck = melanger_quantique(deck)
    return deck


def hand_value(hand):
    """Calcule la valeur (avec gestion des As = 1 ou 11)."""
    valeur_carte = {
        **{str(n): n for n in range(2, 11)},
        'J': 10, 'Q': 10, 'K': 10, 'A': 11,
    }
    total = sum(valeur_carte[c[:-1]] for c in hand)
    nb_aces = sum(1 for c in hand if c.startswith('A'))
    while total > 21 and nb_aces:
        total -= 10
        nb_aces -= 1
    return total