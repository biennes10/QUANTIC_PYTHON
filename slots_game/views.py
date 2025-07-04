# slots_game/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import random

from .forms import CustomUserCreationForm
from .quantum_shuffle import melanger_quantique
from .models import CustomUser  # ton modèle utilisateur

# --------- imports Qiskit pour la machine à sous ------------
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
# ------------------------------------------------------------

def getNombreSlots():
    nombre = 6
    while nombre > 5:
        qc = QuantumCircuit(3,3)

        qc.h(0)
        qc.h(1)
        qc.h(2)
        qc.measure([0,1,2],[0,1,2])

        sim = AerSimulator()
        compiled_circuit = transpile(qc,sim)
        result = sim.run(compiled_circuit, shots=1).result()
        counts = result.get_counts()
        binary_result = list(counts.keys())[0]  # Récupère la clé, par exemple '111'
        nombre = int(binary_result, 2)  # Convertit en base 10
        if nombre <= 5:
            return nombre



def welcome_view(request):
    """
    Vue pour la page d'accueil du site.
    """
    return render(request, 'slots_game/welcome.html')

# ------------------------------------------------------------------
#  I.  INSCRIPTION / CONNEXION
# ------------------------------------------------------------------
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


# ------------------------------------------------------------------
#  II.  MACHINE À SOUS  (quantique)
# ------------------------------------------------------------------
@login_required
def slots_game_view(request):
    user = request.user
    message = ""
    current_slots = ["?", "?", "?"]

    if request.method == 'POST':
        bet_amount = int(request.POST.get('bet_amount', 0))

        if bet_amount <= 0:
            message = "Veuillez entrer un montant de pari valide."
        elif user.balance < bet_amount:
            message = "Fonds insuffisants pour ce pari."
        else:
            user.balance -= bet_amount

            symbols = ["🍒", "🍋", "🍊", "🔔", "⭐", "💎"]  

            current_slots = []

            for i in range(3):
                current_slots.append(getNombreSlots())


            win_multiplier = 0
            if current_slots[0] == current_slots[1] == current_slots[2]:
                win_multiplier = 5
            elif len(set(current_slots)) == 2:  # une paire
                win_multiplier = 2

            symbols_result = []

            for slot in current_slots:
                symbols_result.append(symbols[slot])

            won_amount = bet_amount * win_multiplier
            user.balance += won_amount
            user.save()

            message = (
                f"Félicitations ! Vous avez gagné {won_amount} pièces."
                if won_amount > 0
                else "Dommage !"
            ) + f" Votre nouveau solde est de {user.balance}."

        return JsonResponse({'message': message,
                             'balance': user.balance,
                             'result': symbols_result})

    return render(request, 'slots_game/game.html',
                  {'user': user,
                   'message': message,
                   'current_slots': current_slots})


# ------------------------------------------------------------------
#  III.  BLACKJACK  (mélange quantique)
# ------------------------------------------------------------------
@login_required
def blackjack_game_view(request):
    user = request.user
    state = request.session.get('bj_state', {})

    if request.method == 'POST':
        action = request.POST.get('action', 'new')

        # Nouvelle partie (action = 'bet' ou 'new')
        if action in ['new', 'bet']:
            try:
                bet = int(request.POST.get('bet', 0))
            except (TypeError, ValueError):
                bet = 0

            if bet <= 0 or bet > user.balance:
                state['message'] = "Mise invalide."
            else:
                user.balance -= bet
                user.save()

                deck = create_deck()
                player = [deck.pop(), deck.pop()]
                dealer = [deck.pop(), deck.pop()]
                p_val = hand_value(player)
                d_val = hand_value(dealer)

                state = {
                    'deck': deck,
                    'player': player,
                    'dealer': dealer,
                    'finished': False,
                    'message': '',
                    'bet': bet,
                }

                # Gestion du Blackjack naturel
                if p_val == 21:
                    state['finished'] = True
                    if d_val == 21:
                        user.balance += bet
                        state['message'] = "Blackjack pour les deux ! Égalité."
                    else:
                        gain = int(2.5 * bet)
                        user.balance += bet + gain
                        state['message'] = f"Blackjack naturel ! Vous gagnez {gain} pièces 🎉"
                    user.save()

        # Tirer une carte
        elif action == 'hit' and not state.get('finished', True):
            state['player'].append(state['deck'].pop())
            if hand_value(state['player']) > 21:
                state['finished'] = True
                state['message'] = 'Bust ! Vous dépassez 21.'

        # Rester
        elif action == 'stand' and not state.get('finished', True):
            while hand_value(state['dealer']) < 17:
                state['dealer'].append(state['deck'].pop())

            p_val = hand_value(state['player'])
            d_val = hand_value(state['dealer'])
            state['finished'] = True

            if d_val > 21 or p_val > d_val:
                gain = state['bet'] * 2
                user.balance += gain
                state['message'] = f"Vous gagnez {gain} pièces !"
            elif p_val == d_val:
                user.balance += state['bet']
                state['message'] = "Égalité – mise rendue."
            else:
                state['message'] = "Le croupier gagne."

            user.save()

        # Sauvegarde de la session après l'action
        request.session['bj_state'] = state
        request.session.modified = True

    return render(request, 'blackjack_game/game.html', {
        'user': user,
        'player_cards': state.get('player', []),
        'dealer_cards': state.get('dealer', []),
        'message': state.get('message', ''),
        'state': state,
    })

# ------------------------------------------------------------------
#  UTILITAIRES BLACKJACK
# ------------------------------------------------------------------
def create_deck():
    valeurs  = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    couleurs = ['♠', '♥', '♦', '♣']
    deck = [f"{v}{c}" for v in valeurs for c in couleurs]
    return melanger_quantique(deck)             # mélange quantique


def hand_value(hand):
    """Calcule la valeur d'une main de Blackjack (As = 11 ou 1)."""
    map_val = {**{str(n): n for n in range(2, 11)}, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}
    total = sum(map_val[c[:-1]] for c in hand)
    aces = sum(1 for c in hand if c.startswith('A'))
    while total > 21 and aces:
        total -= 10
        aces  -= 1
    return total
