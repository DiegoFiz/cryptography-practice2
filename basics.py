# PRÁCTICA 1 (ampliada para la Práctica 2)
# Funciones básicas que usan el resto de módulos: alfabeto, normalización,
# tablas de frecuencias, chi-cuadrado y desplazamiento César.

import unicodedata
from collections import Counter

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


# Normaliza un texto: lo pasa a mayúsculas y elimina todo lo que no sea A-Z.
# Antes separo las tildes (NFD) para que "á" se convierta en "A" y no se pierda la letra.
def normalise(text: str) -> str:
    text = unicodedata.normalize("NFD", text.upper())
    result = ""
    for char in text:
        if "A" <= char <= "Z":
            result += char
    return result


# Convierte letras A-Z en números 0-25 (lo demás se ignora)
def to_numbers(text: str) -> list[int]:
    text = text.upper()
    result = []
    for char in text:
        if "A" <= char <= "Z":
            result.append(ord(char) - ord("A"))
    return result


# Convierte números 0-25 en letras A-Z
def to_letters(nums: list[int]) -> str:
    result = []
    for n in nums:
        if 0 <= n <= 25:
            result.append(chr(n + ord("A")))
    return "".join(result)


# Algoritmo extendido de Euclides: devuelve (gcd, s, t) con a*s + b*t = gcd
def egcd(a: int, b: int) -> tuple[int, int, int]:
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    if old_r < 0:
        old_r, old_s, old_t = -old_r, -old_s, -old_t
    return old_r, old_s, old_t


# Inverso modular de num módulo mod (con Euclides extendido, no buscando)
def modinv(num: int, mod: int) -> int:
    gcd, x, _ = egcd(num, mod)
    if gcd != 1:
        raise ValueError(f"No modular inverse for {num} mod {mod}: gcd = {gcd}")
    return x % mod


# XOR byte a byte con la clave repetida
def xor_bytes(data: bytes, key: bytes) -> bytes:
    result = []
    for i in range(len(data)):
        result.append(data[i] ^ key[i % len(key)])
    return bytes(result)


# ---------------------------------------------------------------------------
# Tablas de frecuencia p_L (en %). Teoría T2, diapositiva 11:
#   inglés  E 12.7, T 9.1, A 8.2      español  E 13.7, A 12.5, O 8.7
# Las normalizo para que sumen exactamente 1.
# ---------------------------------------------------------------------------
ENGLISH_PERCENT = [8.167, 1.492, 2.782, 4.253, 12.702, 2.228, 2.015, 6.094, 6.966, 0.153,
                   0.772, 4.025, 2.406, 6.749, 7.507, 1.929, 0.095, 5.987, 6.327, 9.056,
                   2.758, 0.978, 2.360, 0.150, 1.974, 0.074]
SPANISH_PERCENT = [12.53, 1.42, 4.68, 5.86, 13.68, 0.69, 1.01, 0.70, 6.25, 0.44,
                   0.02, 4.97, 3.15, 6.71, 8.68, 2.51, 0.88, 6.87, 7.98, 4.63,
                   3.93, 0.90, 0.01, 0.22, 0.90, 0.52]


def _make_table(percents):
    total = sum(percents)
    table = {}
    for i in range(26):
        table[ALPHABET[i]] = percents[i] / total
    return table


FREQ = {"en": _make_table(ENGLISH_PERCENT), "es": _make_table(SPANISH_PERCENT)}

# Constantes del índice de coincidencia (T4, diapositivas 13 y 15)
KAPPA_R = 1 / 26                          # letras aleatorias uniformes = 0.0385
KAPPA_P = {"en": 0.0667, "es": 0.0750}    # texto natural


# Acepto "en"/"english" y "es"/"spanish"
def get_language(language: str) -> str:
    language = language.lower()
    if language in ("en", "english"):
        return "en"
    if language in ("es", "spanish"):
        return "es"
    raise ValueError("language must be 'en' or 'es'")


# Chi-cuadrado (T4, diapositiva 5) dividido entre n para poder comparar textos de distinta longitud:
#   chi2 = suma_L (o_L - e_L)^2 / e_L     con  e_L = n * p_L
def chi_squared(text: str, language: str = "en") -> float:
    text = normalise(text)
    n = len(text)
    if n == 0:
        return float("inf")
    table = FREQ[get_language(language)]
    counts = Counter(text)
    total = 0
    for letter in ALPHABET:
        observed = counts.get(letter, 0)
        expected = n * table[letter]
        total += (observed - expected) ** 2 / expected
    return total / n


# Desplaza cada letra k posiciones: E_k(x) = (x + k) mod 26. Para descifrar se usa -k.
def caesar_shift(text: str, k: int) -> str:
    result = ""
    for letter in normalise(text):
        number = (ord(letter) - ord("A") + k) % 26
        result += chr(number + ord("A"))
    return result


# Asistente de frecuencias de la Práctica 1: cuenta las letras del criptograma,
# las ordena y las empareja con el orden de frecuencias del idioma.
def frequency_report(text: str, language: str = "en") -> str:
    text = normalise(text)
    language = get_language(language)
    n = len(text)
    if n == 0:
        return "no letters"
    counts = Counter(text)
    table = FREQ[language]

    # orden del criptograma (más frecuente primero; en empate, orden alfabético)
    cipher_order = sorted(ALPHABET, key=lambda letter: (-counts.get(letter, 0), letter))
    # orden del idioma
    language_order = sorted(ALPHABET, key=lambda letter: -table[letter])

    lines = [f"Frequency report (n = {n}, language = {language})",
             "rank  cipher  count      %   |  language   %   -> suggested mapping"]
    mapping = {}
    for i in range(26):
        c = cipher_order[i]
        p = language_order[i]
        mapping[c] = p.lower()
        percent_c = 100 * counts.get(c, 0) / n
        percent_p = 100 * table[p]
        lines.append(f"{i + 1:>4}  {c:>6}  {counts.get(c, 0):>5}  {percent_c:5.1f}   |"
                     f"  {p:>8}  {percent_p:4.1f}  -> {c}={p.lower()}")

    draft = ""
    for letter in text:
        draft += mapping[letter]
    lines.append("first draft by rank alignment (to be refined by hand with bigrams/trigrams):")
    lines.append(draft)
    return "\n".join(lines)