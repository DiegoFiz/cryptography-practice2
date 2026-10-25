# Measures B1, B2, C1, C2 y C3
#   python experiments.py --theory <carpeta con los .pptx T1..T4>
#   python experiments.py --theory theory --only b1|calib|b2|c1|sweep|divisors|c2|c3|time


import argparse
import glob
import math
import os
import random
import re
import sys
import time
import zipfile

from basics import ALPHABET, FREQ, KAPPA_P, KAPPA_R, normalise, chi_squared
import columnar
import keylength
import break_vigenere
import break_columnar
from measure import classify, index_of_coincidence, THRESHOLD

B2_LENGTHS = (60, 120, 250, 400)


# ------------------------------------------------------------------ utilidades

def reference_text(folder: str) -> str:
    files = sorted(glob.glob(os.path.join(folder, "*T[1-4]_*.pptx")))
    if not files:
        sys.exit(f"no T1..T4 .pptx files found in {folder!r}")
    paragraphs = []
    for file in files:
        z = zipfile.ZipFile(file)
        slides = []
        for name in z.namelist():
            if re.fullmatch(r"ppt/slides/slide\d+\.xml", name):
                slides.append(name)
        slides.sort(key=lambda s: int(re.findall(r"\d+", s)[0]))   # slide2 antes que slide10
        for name in slides:
            xml = z.read(name).decode("utf-8")
            for para in re.findall(r"<a:p>.*?</a:p>", xml, flags=re.S):
                t = "".join(re.findall(r"<a:t>([^<]*)</a:t>", para))
                letters = [c for c in t if c.isalpha()]
                # me quedo con los párrafos que son prosa (mayoría de minúsculas);
                # así quito los ejemplos de criptogramas, que van en mayúsculas
                if letters:
                    lower = sum(1 for c in letters if c.islower())
                    if lower / len(letters) >= 0.5:
                        paragraphs.append(t)
    return normalise(" ".join(paragraphs))


# Un trozo aleatorio de L letras del texto de referencia
def window(ref, L, rng):
    start = rng.randrange(len(ref) - L)
    return ref[start:start + L]


# Clave aleatoria de longitud n cuyo periodo real sea n (descarto cosas como QQQ o ABAB)
def random_keyword(n, rng):
    while True:
        key = ""
        for _ in range(n):
            key += rng.choice(ALPHABET)
        periodic = False
        for d in range(1, n):
            if n % d == 0 and key == key[:d] * (n // d):
                periodic = True
        if not periodic:
            return key


# Sustitución monoalfabética con una permutación aleatoria del alfabeto
def random_mono(text, rng):
    perm = list(ALPHABET)
    rng.shuffle(perm)
    return text.translate(str.maketrans(ALPHABET, "".join(perm)))


# n letras de relleno sacadas al azar con la distribución del idioma
def language_pad(n, rng, language="en"):
    weights = [FREQ[language][letter] for letter in ALPHABET]
    return "".join(rng.choices(ALPHABET, weights=weights, k=n))


# Una muestra de transposición columnar con clave de 4 a 9 letras.
# pad_mode: "X" (relleno constante), "lang" (relleno aleatorio del idioma) o None (sin cifrar,
# que es lo mismo que una transposición sin relleno a efectos de frecuencias)
def columnar_sample(ref, L, rng, pad_mode):
    key = random_keyword(rng.randint(4, 9), rng)
    if pad_mode == "X":
        pad = "X"
    elif pad_mode == "lang":
        pad = language_pad(len(key), rng)
    else:
        pad = None
    plain = window(ref, L, rng)
    if pad is None:
        return plain
    return columnar.encrypt(plain, key, pad)


def mean_and_sd(values):
    mean = sum(values) / len(values)
    var = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return mean, var ** 0.5


# ------------------------------------------------------------------ B1

def b1(ref, trials=1000, seed=13):
    rng = random.Random(seed)
    mid = (KAPPA_R + KAPPA_P["en"]) / 2
    print(f"\nB1 — IC misread rate around the mid-point {mid:.4f} ({trials} samples per cell)")
    print("| n | English IC: mean ± sd | English below mid-point | random IC: mean ± sd | random above mid-point |")
    print("|---|---|---|---|---|")
    for L in (13, 20, 30, 40, 50, 60, 80, 100, 150):
        english = []
        for _ in range(trials):
            english.append(index_of_coincidence(window(ref, L, rng)))
        uniform = []
        for _ in range(trials):
            letters = "".join(rng.choice(ALPHABET) for _ in range(L))
            uniform.append(index_of_coincidence(letters))
        me, se = mean_and_sd(english)
        mr, sr = mean_and_sd(uniform)
        wrong_e = 100 * sum(1 for x in english if x < mid) / trials
        wrong_r = 100 * sum(1 for x in uniform if x >= mid) / trials
        print(f"| {L} | {me:.4f} ± {se:.4f} | {wrong_e:.1f} % | {mr:.4f} ± {sr:.4f} | {wrong_r:.1f} % |")


# ------------------------------------------------------------------ B2

# Elijo el umbral con un conjunto de ENTRENAMIENTO (semilla distinta a la de la tabla):
# transposiciones sin relleno y monoalfabéticas a las 4 longitudes. Busco el umbral con
# menos errores y, si hay un intervalo de empates, cojo su punto medio.
def calibrate_threshold(ref, seed=2026, per_family=150):
    rng = random.Random(seed)
    trans = []
    subst = []
    for L in B2_LENGTHS:
        for _ in range(per_family):
            trans.append(chi_squared(window(ref, L, rng)))
            subst.append(chi_squared(random_mono(window(ref, L, rng), rng)))

    errors = {}
    for i in range(20, 401):
        t = round(0.01 * i, 2)
        wrong = 0
        for x in trans:
            if x >= t:
                wrong += 1
        for x in subst:
            if x < t:
                wrong += 1
        errors[t] = wrong

    best = min(errors.values())
    best_thresholds = [t for t in errors if errors[t] == best]
    low, high = best_thresholds[0], best_thresholds[-1]
    print(f"calibration: {len(trans)} transposition + {len(subst)} substitution samples, "
          f"minimum errors {best}/{len(trans) + len(subst)} for thresholds {low:.2f}..{high:.2f}")
    return round((low + high) / 2, 2)


def b2(ref, per_family=150, seed=7):
    results = {}
    for pad_mode in ("X", "lang"):
        rng = random.Random(seed)
        results[pad_mode] = {}
        for L in B2_LENGTHS:
            trans_errors = 0
            for _ in range(per_family):
                if classify(columnar_sample(ref, L, rng, pad_mode)) != "transposition":
                    trans_errors += 1
            subst_errors = 0
            for _ in range(per_family):
                if classify(random_mono(window(ref, L, rng), rng)) != "substitution":
                    subst_errors += 1
            results[pad_mode][L] = (trans_errors, subst_errors)

    print(f"\nB2 classifier, threshold chi2/n = {THRESHOLD['en']}, {per_family}+{per_family} samples per length")
    print("| length | pad = X: trans. err | subst. err | total error | pad ~ English: trans. err | subst. err | total error |")
    print("|---|---|---|---|---|---|---|")
    total = 2 * per_family
    for L in B2_LENGTHS:
        a, b = results["X"][L]
        c, d = results["lang"][L]
        print(f"| {L} | {a}/{per_family} | {b}/{per_family} | {100 * (a + b) / total:.1f} % "
              f"| {c}/{per_family} | {d}/{per_family} | {100 * (c + d) / total:.1f} % |")

    # Pregunta 3: 66 letras con 6 X de relleno
    n, k = 66, 6
    e = n * FREQ["en"]["X"]
    contribution = (k - e) ** 2 / e
    print(f"\nPad contribution, n = {n}, {k} X: e_X = {e:.4f}; (k - e_X)^2/e_X = {contribution:.2f}; "
          f"/n = {contribution / n:.3f}  (vs. no pad: e_X/n = {e / n:.4f})")


# ------------------------------------------------------------------ C1

def c1(ref, key="CIPHER", L=400, seed=11):
    rng = random.Random(seed)
    c = break_vigenere.vigenere_encrypt(window(ref, L, rng), key)
    m0 = len(key)
    print(f"\nC1 coset table: {L} letters, key {key} (m = {m0}); bar = {keylength.bar('en'):.4f}; "
          f"find_key_length = {keylength.find_key_length(c)}")
    print("| m | average coset IC | role |")
    print("|---|---|---|")
    for m in range(1, 17):
        if m == m0:
            role = "**true key length**"
        elif m % m0 == 0:
            role = "multiple"
        elif m > 1 and m0 % m == 0:
            role = "divisor"
        else:
            role = ""
        print(f"| {m} | {keylength.coset_ic(c, m):.4f} | {role} |")


# Cómo elegí qué significa "claramente" (FRACTION de keylength.py)
def fraction_sweep(ref, trials=60, seed=42):
    print("\nC1 — FRACTION sweep (mean key-length accuracy, keys 3/5/7/9 x lengths 100/200/400)")
    original = keylength.FRACTION
    for fraction in (0.5, 0.6, 0.7, 0.8, 0.9):
        keylength.FRACTION = fraction
        rng = random.Random(seed)
        right = 0
        total = 0
        for m in (3, 5, 7, 9):
            for L in (100, 200, 400):
                for _ in range(trials):
                    plain = window(ref, L, rng)
                    key = random_keyword(m, rng)
                    c = break_vigenere.vigenere_encrypt(plain, key)
                    if keylength.find_key_length(c) == m:
                        right += 1
                    total += 1
        print(f"FRACTION = {fraction}: bar = {keylength.bar('en'):.4f}, accuracy = {right / total:.3f}")
    keylength.FRACTION = original


# Caso límite de la regla del menor pico claro: claves de letras distintas, 400 letras.
# Cuento cuántas veces find_key_length falla y cuántas de esas devuelve un divisor.
def divisor_check(ref, trials=3000, seed=99):
    rng = random.Random(seed)
    wrong = 0
    divisor = 0
    example = None
    for _ in range(trials):
        m = rng.choice((3, 4, 5))
        key = "".join(rng.sample(ALPHABET, m))
        c = break_vigenere.vigenere_encrypt(window(ref, 400, rng), key)
        found = keylength.find_key_length(c)
        if found != m:
            wrong += 1
            if m % found == 0:
                divisor += 1
                if example is None:
                    example = (key, found, keylength.coset_ic(c, found), keylength.coset_ic(c, m))
    print(f"\nC1 — divisor check: {trials} ciphertexts of 400 letters, keys of 3-5 distinct letters")
    print(f"wrong key length: {wrong} ({100 * wrong / trials:.1f} %), of which a divisor of m: {divisor}")
    if example:
        key, found, a, b = example
        print(f"example: key {key}, returned {found} (coset_ic {a:.4f}) instead of {len(key)} (coset_ic {b:.4f})")


# ------------------------------------------------------------------ C2

def print_grid(title, rows_label, row_values, col_values, data):
    print(f"\n{title}")
    print(f"| {rows_label} | " + " | ".join(str(c) for c in col_values) + " |")
    print("|---|" + "---|" * len(col_values))
    for r in row_values:
        print(f"| {r} | " + " | ".join(f"{data[r, c]:.2f}" for c in col_values) + " |")


def c2(ref, trials=100, seed=3):
    rng = random.Random(seed)
    key_lengths = (3, 5, 7, 9)
    lengths = (100, 150, 200, 300, 400)
    full_key = {}
    right_length = {}
    for m in key_lengths:
        for L in lengths:
            ok_key = 0
            ok_length = 0
            for _ in range(trials):
                key = random_keyword(m, rng)
                c = break_vigenere.vigenere_encrypt(window(ref, L, rng), key)
                if keylength.find_key_length(c) == m:
                    ok_length += 1
                if break_vigenere.attack(c)[0] == key:
                    ok_key += 1
            full_key[m, L] = ok_key / trials
            right_length[m, L] = ok_length / trials
    print_grid(f"C2 — complete key recovered ({trials} trials per cell)",
               "key length \\ n", key_lengths, lengths, full_key)
    print_grid(f"C2 — key length correct ({trials} trials per cell)",
               "key length \\ n", key_lengths, lengths, right_length)


# ------------------------------------------------------------------ C3

def c3(ref, trials=100, seed=5):
    rng = random.Random(seed)
    columns = (4, 5, 6, 7)
    lengths = (60, 120, 200)
    success = {}
    for n in columns:
        for L in lengths:
            ok = 0
            for _ in range(trials):
                key = random_keyword(n, rng)
                plain = window(ref, L, rng)
                c = columnar.encrypt(plain, key)
                if break_columnar.attack(c, n)[1] == columnar.decrypt(c, key):
                    ok += 1
            success[n, L] = ok / trials
    print_grid(f"C3 — plaintext recovered exactly ({trials} trials per cell, pad X)",
               "columns \\ n", columns, lengths, success)


# Tiempo del ataque exhaustivo según el número de columnas (paro al pasar de 10 s)
def timing(ref):
    rng = random.Random(9)
    print("\nC3 — time of one exhaustive attack (200 letters)")
    for n in range(6, 12):
        L = 200 - 200 % n
        plain = window(ref, L, rng)
        c = columnar.encrypt(plain, random_keyword(n, rng))
        start = time.perf_counter()
        break_columnar.attack(c, n)
        seconds = time.perf_counter() - start
        print(f"n = {n:>2}: {math.factorial(n):>9} orderings, {seconds:7.2f} s")
        if seconds > 10:
            break


# ------------------------------------------------------------------ main

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--theory", default=".")
    parser.add_argument("--only", choices=["b1", "calib", "b2", "c1", "sweep", "divisors", "c2", "c3", "time"])
    parser.add_argument("--trials", type=int, default=100)
    args = parser.parse_args(argv)

    ref = reference_text(args.theory)
    print(f"reference text: {len(ref)} letters of English prose from the T1-T4 slides; "
          f"bigram corpus: pydoc_data.topics (Python standard library)")

    if args.only in (None, "b1"):
        b1(ref)
    if args.only in (None, "calib"):
        print("threshold =", calibrate_threshold(ref))
    if args.only in (None, "b2"):
        b2(ref)
    if args.only in (None, "c1"):
        c1(ref)
    if args.only in (None, "sweep"):
        fraction_sweep(ref)
    if args.only in (None, "divisors"):
        divisor_check(ref)
    if args.only in (None, "c2"):
        c2(ref, args.trials)
    if args.only in (None, "c3"):
        c3(ref, args.trials)
    if args.only in (None, "time"):
        timing(ref)


if __name__ == "__main__":
    main()