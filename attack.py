#EXERCISE D:

import argparse
import sys
from basics import normalise, chi_squared, frequency_report, KAPPA_P, KAPPA_R
from measure import index_of_coincidence, classify, THRESHOLD
import keylength
import kasiski
import break_vigenere
import break_columnar


def attack_transposition(text, language, cols):
    # Si me dan --cols pruebo solo ese; si no, todos los divisores de la longitud entre 2 y 8
    if cols:
        candidates = [cols]
    else:
        candidates = []
        for d in range(2, 9):
            if len(text) % d == 0:
                candidates.append(d)
    if not candidates:
        print("No column count in 2..8 divides the length; use --cols.")
        return 1

    best = None
    for n in candidates:
        try:
            order, plain = break_columnar.attack(text, n, language)
        except ValueError as e:
            print(f"  n = {n}: {e}")
            continue
        s = break_columnar.score(plain, language)
        per_bigram = s / max(len(text) - 1, 1)
        print(f"  n = {n}: bigram log-prob = {s:.1f}  ({per_bigram:.3f} per bigram)")
        if best is None or s > best[0]:
            best = (s, n, order, plain)

    if best is None:
        return 1
    print(f"Decision: columnar transposition, best n = {best[1]} (highest bigram log-prob)")
    print(f"column order = {best[2]}")
    print(f"plaintext: {best[3]}")
    return 0


def attack_substitution(text, language, ic):
    ic_mid = (KAPPA_R + KAPPA_P[language]) / 2
    m = keylength.find_key_length(text, language=language)
    print(f"IC mid-point = {ic_mid:.4f}; find_key_length = {m} (coset-IC bar {keylength.bar(language):.4f})")

    # IC alto y una sola longitud -> monoalfabético
    if ic >= ic_mid and m == 1:
        print("Decision: monoalphabetic substitution (IC high, key length 1).")
        print(frequency_report(text, language))
        return 0

    # Si no -> polialfabético. Imprimo las medidas que justifican la decisión
    for k in range(1, 17):
        line = f"  coset_ic(m={k:>2}) = {keylength.coset_ic(text, k):.4f}"
        if k == m:
            line += "  <- first average above the bar"
        print(line)

    # Kasiski como comprobación independiente (factores > 3, los 5 más frecuentes)
    tally = kasiski.factor_tally(text)
    factors = []
    for f in tally:
        if f > 3:
            factors.append(f)
    factors.sort(key=lambda f: (-tally[f], -f))
    top = []
    for f in factors[:5]:
        top.append(f"{f}:{tally[f]}")
    print(f"Kasiski (corroboration): {len(kasiski.distances(text))} distances; "
          f"factor tally > 3: " + ", ".join(top))

    key, plain = break_vigenere.attack(text, language)
    print(f"Decision: polyalphabetic (IC low or key length > 1), key length {len(key)}.")
    print(f"key: {key}")
    print(f"plaintext: {plain}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="attack.py")
    parser.add_argument("--in", dest="inp", required=True)
    parser.add_argument("--lang", default="en", choices=["en", "es"])
    parser.add_argument("--cols", type=int)
    args = parser.parse_args(argv)

    try:
        with open(args.inp, encoding="utf-8") as f:
            text = normalise(f.read())
    except OSError as e:
        print(f"error: cannot read {args.inp}: {e.strerror}", file=sys.stderr)
        return 1
    if len(text) < 2:
        print("Input has fewer than 2 letters: nothing to analyse.")
        return 1

    # 1) IC y familia
    ic = index_of_coincidence(text)
    chi = chi_squared(text, args.lang)
    family = classify(text, args.lang)
    print(f"letters n = {len(text)}")
    print(f"IC = {ic:.4f}  (random {KAPPA_R:.4f}, {args.lang} {KAPPA_P[args.lang]:.4f})")
    print(f"chi2/n = {chi:.4f}  threshold = {THRESHOLD[args.lang]}  -> family: {family}")

    # 2), 3) y 4)
    if family == "transposition":
        return attack_transposition(text, args.lang, args.cols)
    return attack_substitution(text, args.lang, ic)


if __name__ == "__main__":
    sys.exit(main())