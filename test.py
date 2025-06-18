import tkinter as tk
from qiskit import QuantumCircuit
from qiskit_aer import Aer

def tirage_quantique(max_val):
    nb_bits = (max_val - 1).bit_length()
    backend = Aer.get_backend('qasm_simulator')

    while True:
        qc = QuantumCircuit(nb_bits, nb_bits)
        qc.h(range(nb_bits))
        qc.measure(range(nb_bits), range(nb_bits))
        job = backend.run(qc, shots=1)
        result = job.result().get_counts()
        tirage = int(list(result.keys())[0], 2)
        if tirage < max_val:
            return tirage

def melanger_quantique(jeu):
    jeu = jeu[:]
    n = len(jeu)
    for i in range(n - 1, 0, -1):
        j = tirage_quantique(i + 1)
        jeu[i], jeu[j] = jeu[j], jeu[i]
    return jeu

valeurs = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
couleurs = ['♠', '♥', '♦', '♣']
jeu_initial = [f"{valeur}{couleur}" for valeur in valeurs for couleur in couleurs]

jeu_de_cartes = []
cartes_tirees = []

def initialiser_paquet():
    global jeu_de_cartes, cartes_tirees
    jeu_de_cartes = melanger_quantique(jeu_initial)
    cartes_tirees = []
    mise_a_jour_affichage()
    label_resultat.config(text="Nouveau paquet mélangé")

def tirer_et_afficher():
    if jeu_de_cartes:
        carte = jeu_de_cartes.pop(0)
        cartes_tirees.append(carte)
        label_resultat.config(text=f"Carte tirée : {carte}")
        mise_a_jour_affichage()
    else:
        label_resultat.config(text="Plus de cartes")

def mise_a_jour_affichage():
    paquet_texte = "\n".join(jeu_de_cartes)
    defausse_texte = "\n".join(cartes_tirees)
    text_paquet.config(state="normal")
    text_defausse.config(state="normal")
    text_paquet.delete(1.0, tk.END)
    text_defausse.delete(1.0, tk.END)
    text_paquet.insert(tk.END, paquet_texte)
    text_defausse.insert(tk.END, defausse_texte)
    text_paquet.config(state="disabled")
    text_defausse.config(state="disabled")

fenetre = tk.Tk()
fenetre.title("Blackjack Quantique - Paquet de Cartes")

frame_top = tk.Frame(fenetre)
frame_top.pack(pady=10)

bouton_tirer = tk.Button(frame_top, text="Tirer une carte", command=tirer_et_afficher, font=("Arial", 12))
bouton_tirer.grid(row=0, column=0, padx=10)

bouton_shuffle = tk.Button(frame_top, text="Re-mélanger", command=initialiser_paquet, font=("Arial", 12))
bouton_shuffle.grid(row=0, column=1, padx=10)

label_resultat = tk.Label(fenetre, text="", font=("Arial", 14, "bold"))
label_resultat.pack(pady=10)

frame_affichage = tk.Frame(fenetre)
frame_affichage.pack(padx=20, pady=10)

label_paquet = tk.Label(frame_affichage, text="Paquet restant", font=("Arial", 12))
label_paquet.grid(row=0, column=0, padx=20)

label_defausse = tk.Label(frame_affichage, text="Cartes tirées", font=("Arial", 12))
label_defausse.grid(row=0, column=1, padx=20)

text_paquet = tk.Text(frame_affichage, width=15, height=20, state="disabled", font=("Courier", 12))
text_paquet.grid(row=1, column=0, padx=20)

text_defausse = tk.Text(frame_affichage, width=15, height=20, state="disabled", font=("Courier", 12))
text_defausse.grid(row=1, column=1, padx=20)

initialiser_paquet()

fenetre.mainloop()
