#EXERCISE C2 (AUTOMATIC VIGENERE ATTACK):

from basics import ALPHABET, normalise, caesar_shift
from break_caesar import break_caesar
from keylength import find_key_length


def attack(ciphertext: str, language: str = "en") -> tuple[str, str]:
    """Returns (key, plaintext). The key length is NOT given."""
    text = normalise(ciphertext)
    if text == "":
        return "", ""

    # 1) longitud de clave con C1
    m = find_key_length(text, language=language)

    # 2) cada coset es un César: lo rompo con el breaker de la Práctica 1
    key = ""
    for i in range(m):
        coset = text[i::m]
        k, _ = break_caesar(coset, language)
        key += ALPHABET[k]

    # 3) descifro con la clave obtenida
    plain = ""
    for i in range(len(text)):
        shift = ALPHABET.index(key[i % m])
        plain += caesar_shift(text[i], -shift)
    return key, plain


# Cifrado Vigenère (lo uso para generar los textos de prueba)
def vigenere_encrypt(plaintext: str, key: str) -> str:
    text = normalise(plaintext)
    result = ""
    for i in range(len(text)):
        shift = ALPHABET.index(key[i % len(key)])
        result += caesar_shift(text[i], shift)
    return result