#EXERCISE A1 (RAILFENCE):

from basics import normalise


# Devuelve, para cada posición del texto, en qué raíl cae siguiendo el zigzag.
# Ejemplo con 3 raíles: 0 1 2 1 0 1 2 1 0 ...
def rail_pattern(length: int, rails: int) -> list[int]:
    if rails < 2:
        raise ValueError("rails must be >= 2")
    pattern = []
    row = 0
    step = 1
    for i in range(length):
        pattern.append(row)
        if row == 0:
            step = 1            # en el raíl de arriba, bajamos
        elif row == rails - 1:
            step = -1           # en el raíl de abajo, subimos
        row += step
    return pattern


def encrypt(plaintext: str, rails: int) -> str:
    text = normalise(plaintext)
    pattern = rail_pattern(len(text), rails)
    rows = [""] * rails
    for i in range(len(text)):
        rows[pattern[i]] += text[i]
    # se lee raíl por raíl
    return "".join(rows)


def decrypt(ciphertext: str, rails: int) -> str:
    text = normalise(ciphertext)
    pattern = rail_pattern(len(text), rails)

    # 1) cuántas letras tiene cada raíl
    sizes = [0] * rails
    for row in pattern:
        sizes[row] += 1

    # 2) corto el criptograma en los trozos de cada raíl
    rows = []
    start = 0
    for size in sizes:
        rows.append(text[start:start + size])
        start += size

    # 3) recorro el zigzag otra vez cogiendo la siguiente letra de cada raíl
    used = [0] * rails
    result = ""
    for row in pattern:
        result += rows[row][used[row]]
        used[row] += 1
    return result
