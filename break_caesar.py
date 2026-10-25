from basics import normalise, caesar_shift, chi_squared


# Pruebo los 26 desplazamientos, puntúo cada candidato con chi2/n y me quedo con el menor.
# Devuelve (k, texto_claro), donde el criptograma es E_k(texto_claro).
def break_caesar(ciphertext: str, language: str = "en") -> tuple[int, str]:
    ciphertext = normalise(ciphertext)
    if ciphertext == "":
        return 0, ""

    best_k = 0
    best_plain = ciphertext
    best_score = float("inf")
    for k in range(26):
        candidate = caesar_shift(ciphertext, -k)
        score = chi_squared(candidate, language)
        if score < best_score:
            best_k = k
            best_plain = candidate
            best_score = score
    return best_k, best_plain


if __name__ == "__main__":
    test = caesar_shift("THE TREASURE IS BURIED UNDER THE OLD OAK TREE", 7)
    print(test)
    print(break_caesar(test))

