from qiskit import QuantumCircuit
from qiskit_aer import Aer

def tirage_quantique(max_val: int) -> int:
    """Retourne un entier aléatoire uniforme dans [0, max_val-1] par mesure quantique."""
    nb_bits = (max_val - 1).bit_length()
    backend = Aer.get_backend('qasm_simulator')

    while True:
        qc = QuantumCircuit(nb_bits, nb_bits)
        qc.h(range(nb_bits))
        qc.measure(range(nb_bits), range(nb_bits))
        tirage = int(list(backend.run(qc, shots=1).result()
                               .get_counts()
                               .keys())[0], 2)
        if tirage < max_val:
            return tirage

def melanger_quantique(paquet: list[str]) -> list[str]:
    """Fisher-Yates où l’indice j est obtenu par tirage_quantique."""
    jeu = paquet[:] 
    for i in range(len(jeu) - 1, 0, -1):
        j = tirage_quantique(i + 1)
        jeu[i], jeu[j] = jeu[j], jeu[i]
    return jeu
