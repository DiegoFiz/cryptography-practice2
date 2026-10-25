#EXERCISE B1, B2 (INDEX OF COINCIDENCE):

from collections import Counter
from basics import normalise, chi_squared

# Umbral de chi2/n elegido con datos (python experiments.py --only calib):
# 1200 muestras de entrenamiento (semilla 2026), transposiciones sin relleno frente a
# monoalfabéticas, longitudes 60/120/250/400. El error mínimo (10/1200) se da entre
# 1.69 y 1.75 y cojo el punto medio. Para español no tenía texto de referencia, así que
# uso el mismo valor (lo digo en el apartado 10 del README).
THRESHOLD = {"en": 1.72, "es": 1.72}


# IC = suma n_L (n_L - 1) / (n (n - 1))   (T4, diapositiva 12)
def index_of_coincidence(text: str) -> float:
    text = normalise(text)
    n = len(text)
    if n < 2:
        return 0.0
    counts = Counter(text)
    total = 0
    for count in counts.values():
        total += count * (count - 1)
    return total / (n * (n - 1))


# Una transposición no cambia las letras, así que su chi2/n frente al idioma es pequeño.
# Una sustitución cambia la distribución y da un chi2/n grande.
def classify(ciphertext: str, language: str = "en") -> str:
    """Return "transposition" or "substitution"."""
    text = normalise(ciphertext)
    if chi_squared(text, language) < THRESHOLD[language]:
        return "transposition"
    return "substitution"