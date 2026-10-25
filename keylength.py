#EXERCISE C1 (KEY LENGTH):

from basics import normalise, KAPPA_P, KAPPA_R
from measure import index_of_coincidence

# "Claramente por encima" = el IC medio de los cosets ha recorrido al menos el 70 % del
# camino entre KAPPA_R (aleatorio) y KAPPA_P (idioma):
#     media >= KAPPA_R + 0.7 * (KAPPA_P - KAPPA_R)   -> 0.0582 en inglés
# El 0.7 lo elegí con datos (python experiments.py --only sweep, semilla 42, 720 textos):
#     FRACTION 0.5 / 0.6 / 0.7 / 0.8 / 0.9  ->  acierto 0.840 / 0.894 / 0.900 / 0.889 / 0.839
FRACTION = 0.7


# Divide el texto en m cosets (posiciones 0, m, 2m... / 1, m+1... ) y devuelve la media de sus IC
def coset_ic(ciphertext: str, m: int) -> float:
    text = normalise(ciphertext)
    total = 0
    for i in range(m):
        total += index_of_coincidence(text[i::m])
    return total / m


# Valor a partir del cual considero que una media "destaca"
def bar(language: str = "en") -> float:
    return KAPPA_R + FRACTION * (KAPPA_P[language] - KAPPA_R)


# Devuelve el MENOR m que supera la barra (no el de mayor media: los múltiplos de la
# longitud real también dan picos y a veces más altos).
def find_key_length(ciphertext: str, max_m: int = 16, language: str = "en") -> int:
    text = normalise(ciphertext)
    averages = {}
    for m in range(1, max_m + 1):
        averages[m] = coset_ic(text, m)

    for m in range(1, max_m + 1):
        if averages[m] >= bar(language):
            return m

    # si ninguno llega a la barra (texto muy corto), cojo el menor m que esté
    # cerca (90 %) del máximo
    top = max(averages.values())
    for m in range(1, max_m + 1):
        if averages[m] >= 0.9 * top:
            return m
    return 1
