#EXERCISE B3 (KASISKI EXAMINATION):

from basics import normalise


# Todas las secuencias de min_len letras o más que aparecen más de una vez, con sus posiciones.
def repeats(ciphertext: str, min_len: int = 3) -> dict[str, list[int]]:
    text = normalise(ciphertext)
    n = len(text)
    result = {}
    length = min_len
    while length <= n // 2 + 1:
        positions = {}
        for i in range(n - length + 1):
            piece = text[i:i + length]
            if piece not in positions:
                positions[piece] = []
            positions[piece].append(i)

        found = False
        for piece in positions:
            if len(positions[piece]) > 1:
                result[piece] = positions[piece]
                found = True
        # si no hay repeticiones de esta longitud, tampoco las habrá más largas
        if not found:
            break
        length += 1
    return result


# Me quedo solo con las repeticiones "maximales": las que no se pueden alargar ni por la
# izquierda ni por la derecha. Así ELQYRJ cuenta una vez y no también ELQY, LQYR...
def maximal_repeats(ciphertext: str, min_len: int = 3) -> dict[str, list[int]]:
    text = normalise(ciphertext)
    result = {}
    for piece, positions in repeats(text, min_len).items():
        right = set()
        left = set()
        for p in positions:
            if p + len(piece) < len(text):
                right.add(text[p + len(piece)])
            else:
                right.add(None)
            if p > 0:
                left.add(text[p - 1])
            else:
                left.add(None)
        can_extend_right = len(right) == 1 and None not in right
        can_extend_left = len(left) == 1 and None not in left
        if not can_extend_right and not can_extend_left:
            result[piece] = positions
    return result


# Distancias entre apariciones consecutivas de cada repetición maximal
def distances(ciphertext: str, min_len: int = 3) -> list[int]:
    result = []
    for positions in maximal_repeats(ciphertext, min_len).values():
        for i in range(len(positions) - 1):
            result.append(positions[i + 1] - positions[i])
    result.sort()
    return result


# Para cada factor posible, cuántas distancias son divisibles por él
def factor_tally(ciphertext: str, max_factor: int = 20) -> dict[int, int]:
    ds = distances(ciphertext)
    tally = {}
    for f in range(2, max_factor + 1):
        tally[f] = 0
        for d in ds:
            if d % f == 0:
                tally[f] += 1
    return tally

