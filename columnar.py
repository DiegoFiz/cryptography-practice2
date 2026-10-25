#EXERCISE A2, A3 (COLUMNAR - transposition):

from math import lcm
from basics import normalise


# Añade letras de relleno hasta que la longitud sea múltiplo de block.
# pad = "X" -> se repite la X.  Si pad tiene varias letras se usan por orden
# (lo uso en B2 para meter relleno aleatorio sacado de la distribución del idioma).
def add_padding(text: str, block: int, pad: str) -> str:
    missing = len(text) % block
    if missing != 0:
        missing = block - missing
    pad_letters = normalise(pad)
    if missing > 0 and pad_letters == "":
        raise ValueError("pad must contain at least one letter A-Z")
    for i in range(missing):
        text += pad_letters[i % len(pad_letters)]
    return text


# Numera las letras de la clave por orden alfabético; los empates, de izquierda a derecha.
# key_order("ENIGMA") -> [2, 6, 4, 3, 5, 1]
def key_order(keyword: str) -> list[int]:
    keyword = keyword.upper()
    pairs = []
    for i in range(len(keyword)):
        pairs.append((keyword[i], i))
    pairs.sort()                       # ordena por letra y, si empatan, por posición
    order = [0] * len(keyword)
    rank = 1
    for letter, position in pairs:
        order[position] = rank
        rank += 1
    return order


def encrypt(plaintext: str, keyword: str, pad: str = "X") -> str:
    n = len(keyword)
    if n == 0:
        raise ValueError("empty keyword")
    text = add_padding(normalise(plaintext), n, pad)

    # escribo el texto por filas: la letra i va a la columna i % n
    columns = [""] * n
    for i in range(len(text)):
        columns[i % n] += text[i]

    # leo las columnas en el orden 1, 2, ..., n que marca la clave
    order = key_order(keyword)
    result = ""
    for rank in range(1, n + 1):
        j = order.index(rank)
        result += columns[j]
    return result


def decrypt(ciphertext: str, keyword: str) -> str:
    text = normalise(ciphertext)
    n = len(keyword)
    if n == 0:
        raise ValueError("empty keyword")
    if len(text) % n != 0:
        raise ValueError("ciphertext length is not a multiple of the number of columns")
    rows = len(text) // n
    order = key_order(keyword)

    # la columna con número r ocupa el trozo r-1 del criptograma
    columns = []
    for j in range(n):
        start = (order[j] - 1) * rows
        columns.append(text[start:start + rows])

    # vuelvo a leer por filas (el relleno NO se quita)
    result = ""
    for i in range(rows):
        for j in range(n):
            result += columns[j][i]
    return result


# Doble transposición: la salida de la primera pasada es la entrada de la segunda.
# Relleno UNA sola vez, hasta un múltiplo de lcm(|kw1|, |kw2|), para que ninguna pasada
# tenga que añadir más relleno (ver la respuesta de A3 en el README).
def encrypt_double(plaintext: str, kw1: str, kw2: str, pad: str = "X") -> str:
    if kw1 == "" or kw2 == "":
        raise ValueError("empty keyword")
    text = add_padding(normalise(plaintext), lcm(len(kw1), len(kw2)), pad)
    first = encrypt(text, kw1, pad)
    return encrypt(first, kw2, pad)


def decrypt_double(ciphertext: str, kw1: str, kw2: str) -> str:
    text = normalise(ciphertext)
    if len(text) % lcm(len(kw1), len(kw2)) != 0:
        raise ValueError("length must be a multiple of lcm(|kw1|, |kw2|)")
    # se deshacen las pasadas en orden inverso
    first = decrypt(text, kw2)
    return decrypt(first, kw1)