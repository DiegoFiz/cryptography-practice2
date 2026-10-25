#EXERCISE C3 (COLUMNAR TRANSPOSITION BREAKER):

import math
import os
from itertools import permutations
from basics import ALPHABET, normalise

_tables = {}   # caché para no recalcular la tabla de bigramas cada vez


# Corpus para la tabla de bigramas. Si hay un fichero corpus_<idioma>.txt al lado del código
# lo uso; si no, uso pydoc_data.topics, que es la documentación de Python en inglés y viene
# en la biblioteca estándar (me quedo con las primeras 150 000 letras).
def load_corpus(language: str) -> str:
    folder = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(folder, f"corpus_{language}.txt")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return normalise(f.read())
    from pydoc_data import topics
    text = " ".join(topics.topics.values())
    return normalise(text)[:150000]


# Tabla 26x26 con log p(xy). Empiezo todos los contadores en 1 para que ningún bigrama
# tenga probabilidad 0 (si no, log(0) daría error).
def bigram_table(language: str = "en") -> list[list[float]]:
    if language in _tables:
        return _tables[language]

    counts = []
    for i in range(26):
        counts.append([1] * 26)
    corpus = load_corpus(language)
    for i in range(len(corpus) - 1):
        a = ALPHABET.index(corpus[i])
        b = ALPHABET.index(corpus[i + 1])
        counts[a][b] += 1

    total = 0
    for row in counts:
        total += sum(row)

    table = []
    for row in counts:
        log_row = []
        for value in row:
            log_row.append(math.log(value / total))
        table.append(log_row)
    _tables[language] = table
    return table


# Puntuación de un texto: suma de log p(xy) de cada par de letras seguidas
def score(text: str, language: str = "en") -> float:
    table = bigram_table(language)
    text = normalise(text)
    total = 0
    for i in range(len(text) - 1):
        a = ALPHABET.index(text[i])
        b = ALPHABET.index(text[i + 1])
        total += table[a][b]
    return total


def attack(ciphertext: str, n_cols: int, language: str = "en") -> tuple[tuple[int, ...], str]:
    """Returns (column order, plaintext) for a known number of columns."""
    text = normalise(ciphertext)
    n = n_cols
    if n < 1 or len(text) < n or len(text) % n != 0:
        raise ValueError("need len(ciphertext) a positive multiple of n_cols")
    rows = len(text) // n
    table = bigram_table(language)

    # El criptograma son n bloques seguidos, uno por columna
    blocks = []
    for k in range(n):
        block = []
        for letter in text[k * rows:(k + 1) * rows]:
            block.append(ALPHABET.index(letter))
        blocks.append(block)

    # Para no recalcular el texto entero en cada permutación, precalculo:
    #   inner[a][b] = puntuación de poner el bloque b justo a la derecha del a (misma fila)
    #   wrap[a][b]  = puntuación de pasar del final de una fila (bloque a) al principio
    #                 de la siguiente (bloque b, una fila más abajo)
    inner = []
    wrap = []
    for a in range(n):
        inner_row = []
        wrap_row = []
        for b in range(n):
            s = 0
            for r in range(rows):
                s += table[blocks[a][r]][blocks[b][r]]
            inner_row.append(s)
            s = 0
            for r in range(rows - 1):
                s += table[blocks[a][r]][blocks[b][r + 1]]
            wrap_row.append(s)
        inner.append(inner_row)
        wrap.append(wrap_row)

    # Pruebo las n! ordenaciones
    best_score = -math.inf
    best_perm = None
    for perm in permutations(range(n)):
        s = 0
        for j in range(n - 1):
            s += inner[perm[j]][perm[j + 1]]
        s = wrap[perm[-1]][perm[0]] + s
        if s > best_score:
            best_score = s
            best_perm = perm

    # Reconstruyo el texto: la columna j del texto claro es el bloque best_perm[j]
    plain = ""
    for r in range(rows):
        for j in range(n):
            plain += text[best_perm[j] * rows + r]

    # El orden se devuelve numerado desde 1, igual que key_order
    order = []
    for k in best_perm:
        order.append(k + 1)
    return tuple(order), plain