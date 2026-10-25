#   python -m unittest discover -s tests -v      (o también: pytest tests/)

import contextlib
import io
import os
import random
import sys
import tempfile
import unittest

# para poder importar los módulos de la carpeta de arriba
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

from basics import ALPHABET, normalise, caesar_shift
import railfence
import columnar
import measure
import kasiski
import keylength
import break_vigenere
import break_columnar
import attack
import crypto
from break_caesar import break_caesar
from sample_text import SAMPLE

PLAIN = normalise(SAMPLE)     # unas 2100 letras de inglés sacadas de las diapositivas
KASISKI_TEXT = "ELQYR JVQDR LXEGB ELQQV ALQFE PTQOG DEZRG SIDSC PEFGO PXDOL ELQYR JXAOA LPKGV D"


# ---------- funciones de ayuda para generar datos de prueba

def random_piece(length, rng):
    start = rng.randrange(len(PLAIN) - length)
    return PLAIN[start:start + length]


def random_key(length, rng):
    # clave con periodo real = length (sin cosas como AAA o ABAB)
    while True:
        key = "".join(rng.choice(ALPHABET) for _ in range(length))
        periodic = False
        for d in range(1, length):
            if length % d == 0 and key == key[:d] * (length // d):
                periodic = True
        if not periodic:
            return key


def random_substitution(text, rng):
    perm = list(ALPHABET)
    rng.shuffle(perm)
    return text.translate(str.maketrans(ALPHABET, "".join(perm)))


def run_program(module, args, text):
    # escribe text en un fichero temporal, ejecuta module.main(...) y devuelve (código, salida)
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(text)
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output):
            code = module.main(args + ["--in", f.name])
    finally:
        os.unlink(f.name)
    return code, output.getvalue()


# ---------- A1

class TestA1RailFence(unittest.TestCase):
    def test_check_values(self):
        self.assertEqual(railfence.encrypt("MYSECRETMESSAGE", 2), "MSCEMSAEYERTESG")
        self.assertEqual(railfence.encrypt("MYSECRETMESSAGE", 3), "MCMAYERTESGSESE")
        self.assertEqual(railfence.encrypt("MYSECRETMESSAGE", 4), "MEAYRTSGSCMSEEE")

    def test_round_trip_every_rail_count(self):
        message = "Attack at dawn! Hold the bridge, 1918."
        for r in range(2, 45):          # también con más raíles que letras
            cipher = railfence.encrypt(message, r)
            self.assertEqual(railfence.decrypt(cipher, r), normalise(message))

    def test_invalid_rails(self):
        with self.assertRaises(ValueError):
            railfence.encrypt("ABC", 1)

    def test_edge_cases(self):
        for r in (2, 3, 5):
            self.assertEqual(railfence.encrypt("", r), "")
            self.assertEqual(railfence.encrypt("a", r), "A")
            self.assertEqual(railfence.encrypt("123 !?", r), "")
            self.assertEqual(railfence.decrypt("", r), "")


# ---------- A2

class TestA2Columnar(unittest.TestCase):
    def test_key_order(self):
        self.assertEqual(columnar.key_order("ENIGMA"), [2, 6, 4, 3, 5, 1])
        self.assertEqual(columnar.key_order("ROTOR"), [3, 1, 5, 2, 4])
        self.assertEqual(columnar.key_order("KASISKI"), [4, 1, 6, 2, 7, 5, 3])
        self.assertEqual(columnar.key_order("BLETCHLEY"), [1, 6, 3, 8, 2, 5, 7, 4, 9])

    def test_check_values(self):
        self.assertEqual(columnar.encrypt("MYSECRETMESSAGE", "CIPHER"), "MEACSXEEXYTGSMERSX")
        self.assertEqual(columnar.encrypt("THE INDEX OF COINCIDENCE", "KASISKI"), "HOIICEENETXCDICEFDNON")

    def test_round_trip_returns_padded_plaintext(self):
        rng = random.Random(1)
        for _ in range(200):
            message = random_piece(rng.randint(1, 80), rng)
            key = random_key(rng.randint(2, 9), rng)
            missing = (len(key) - len(message) % len(key)) % len(key)
            expected = message + "X" * missing
            cipher = columnar.encrypt(message, key)
            self.assertEqual(columnar.decrypt(cipher, key), expected)

    def test_pad_is_a_parameter(self):
        self.assertEqual(columnar.encrypt("MYSECRETMESSAGE", "CIPHER", pad="Q"), "MEACSQEEQYTGSMERSQ")
        self.assertEqual(columnar.decrypt(columnar.encrypt("ABCDE", "KEY", pad="Z"), "KEY"), "ABCDEZ")
        # si pad tiene varias letras, se usan por orden
        self.assertEqual(columnar.decrypt(columnar.encrypt("ABCD", "KEYS", pad="PQ"), "KEYS"), "ABCD")
        self.assertEqual(columnar.decrypt(columnar.encrypt("ABCDE", "KEYS", pad="PQR"), "KEYS"), "ABCDEPQR")

    def test_edge_cases(self):
        self.assertEqual(columnar.encrypt("", "KEY"), "")
        self.assertEqual(columnar.encrypt("a", "KEY"), "XAX")
        self.assertEqual(columnar.encrypt("!!! 42", "KEY"), "")
        self.assertEqual(columnar.decrypt("", "KEY"), "")
        with self.assertRaises(ValueError):         # criptograma más corto que el nº de columnas
            columnar.decrypt("AB", "CIPHER")
        with self.assertRaises(ValueError):
            columnar.encrypt("ABC", "")


# ---------- A3

class TestA3Double(unittest.TestCase):
    def test_check_value(self):
        cipher = columnar.encrypt_double("THESAMEKEYMUSTNEVERBEUSEDTWICE", "ROTOR", "ENIGMA")
        self.assertEqual(cipher, "WCTEIHSTAEVREBEUTMNSUEEDSEEMYK")
        self.assertEqual(columnar.decrypt_double(cipher, "ROTOR", "ENIGMA"), "THESAMEKEYMUSTNEVERBEUSEDTWICE")

    def test_length_not_multiple_of_either_key(self):
        message = "ATTACKATDAWNHOLDTHEBRID"      # 23 letras: ni múltiplo de 5 ni de 6
        cipher = columnar.encrypt_double(message, "ROTOR", "ENIGMA")
        self.assertEqual(len(cipher), 30)       # se rellena una vez hasta lcm(5, 6) = 30
        self.assertEqual(columnar.decrypt_double(cipher, "ROTOR", "ENIGMA"), message + "XXXXXXX")

    def test_round_trip_random(self):
        rng = random.Random(2)
        for _ in range(100):
            message = random_piece(rng.randint(1, 90), rng)
            k1 = random_key(rng.randint(2, 8), rng)
            k2 = random_key(rng.randint(2, 8), rng)
            result = columnar.decrypt_double(columnar.encrypt_double(message, k1, k2), k1, k2)
            self.assertTrue(result.startswith(message))
            self.assertEqual(result[len(message):], "X" * (len(result) - len(message)))


# ---------- B1

class TestB1IndexOfCoincidence(unittest.TestCase):
    def test_check_values(self):
        self.assertAlmostEqual(measure.index_of_coincidence("CRYPTANALYSIS"), 6 / 156)
        self.assertAlmostEqual(measure.index_of_coincidence("THEINDEXOFCOINCIDENCE"), 34 / 420)
        self.assertEqual(round(measure.index_of_coincidence("CRYPTANALYSIS"), 4), 0.0385)
        self.assertEqual(round(measure.index_of_coincidence("THEINDEXOFCOINCIDENCE"), 4), 0.0810)

    def test_edge_cases(self):
        self.assertEqual(measure.index_of_coincidence(""), 0.0)
        self.assertEqual(measure.index_of_coincidence("A"), 0.0)
        self.assertEqual(measure.index_of_coincidence("1234 ..."), 0.0)
        self.assertEqual(measure.index_of_coincidence("AA"), 1.0)

    def test_same_ic_after_transposition(self):
        text = PLAIN[:300]
        cipher = columnar.encrypt(text, "CIPHER")
        self.assertAlmostEqual(measure.index_of_coincidence(cipher), measure.index_of_coincidence(text))


# ---------- B2

class TestB2Classifier(unittest.TestCase):
    def test_families(self):
        # Con 250 letras medí un error de ~1 % en sustituciones (una clave aleatoria puede llevar
        # letras frecuentes a letras frecuentes y parecer inglés), así que permito 1 fallo de 20.
        rng = random.Random(3)
        substitution_errors = 0
        for _ in range(20):
            text = random_piece(250, rng)
            perm = list(ALPHABET)
            rng.shuffle(perm)
            c1 = columnar.encrypt(text, random_key(5, rng), pad="E")
            c2 = railfence.encrypt(text, rng.randint(2, 6))
            c3 = text.translate(str.maketrans(ALPHABET, "".join(perm)))
            self.assertEqual(measure.classify(c1), "transposition")
            self.assertEqual(measure.classify(c2), "transposition")
            if measure.classify(c3) != "substitution":
                substitution_errors += 1
        self.assertLessEqual(substitution_errors, 1)

    def test_edge_cases(self):
        for text in ("", "A", "!!!"):
            self.assertIn(measure.classify(text), ("transposition", "substitution"))


# ---------- B3

class TestB3Kasiski(unittest.TestCase):
    def test_check_values(self):
        found = kasiski.repeats(KASISKI_TEXT)
        self.assertEqual(found["ELQ"], [0, 15, 50])
        longest = max(found, key=len)
        self.assertEqual(longest, "ELQYRJ")
        self.assertEqual(found[longest], [0, 50])
        self.assertEqual(kasiski.distances(KASISKI_TEXT), [15, 35, 50])
        tally = kasiski.factor_tally(KASISKI_TEXT)
        self.assertEqual(tally[5], 3)               # 5 divide las tres distancias

    def test_edge_cases(self):
        for text in ("", "A", "?!"):
            self.assertEqual(kasiski.repeats(text), {})
            self.assertEqual(kasiski.distances(text), [])
            for value in kasiski.factor_tally(text).values():
                self.assertEqual(value, 0)


# ---------- C1

class TestC1KeyLength(unittest.TestCase):
    def test_smallest_clear_peak(self):
        cipher = break_vigenere.vigenere_encrypt(PLAIN[:400], "CIPHER")
        self.assertEqual(keylength.find_key_length(cipher), 6)
        # el múltiplo 12 también pasa la barra, pero tiene que salir 6
        self.assertGreater(keylength.coset_ic(cipher, 12), keylength.bar("en"))

    def test_twenty_generated(self):
        # Con 400 letras y claves de 3-5 letras distintas falla un 1.6 % de las veces
        # (python experiments.py --only divisors): los cosets de un divisor (p. ej. m = 2 con la
        # clave WMLC) mezclan desplazamientos parecidos y pasan justo la barra.
        # Por eso genero 21 criptogramas y exijo al menos 20 aciertos (ver README, apartado 10).
        rng = random.Random(4)
        right = 0
        for _ in range(21):
            m = rng.choice((3, 4, 5))
            key = "".join(rng.sample(ALPHABET, m))     # letras distintas
            cipher = break_vigenere.vigenere_encrypt(random_piece(400, rng), key)
            if keylength.find_key_length(cipher) == m:
                right += 1
        self.assertGreaterEqual(right, 20)

    def test_edge_cases(self):
        self.assertEqual(keylength.coset_ic("", 3), 0.0)
        self.assertEqual(keylength.find_key_length(""), 1)
        self.assertEqual(keylength.find_key_length("A"), 1)


# ---------- C2

class TestC2Vigenere(unittest.TestCase):
    def test_twenty_generated(self):
        # igual que en C1: 21 criptogramas y al menos 20 claves recuperadas
        rng = random.Random(5)
        right = 0
        for _ in range(21):
            key = "".join(rng.sample(ALPHABET, rng.choice((3, 4, 5))))
            plain = random_piece(400, rng)
            cipher = break_vigenere.vigenere_encrypt(plain, key)
            if break_vigenere.attack(cipher) == (key, plain):
                right += 1
        self.assertGreaterEqual(right, 20)

    def test_caesar_breaker(self):
        self.assertEqual(break_caesar(caesar_shift(PLAIN[:60], 3)), (3, PLAIN[:60]))
        self.assertEqual(break_caesar(""), (0, ""))

    def test_edge_cases(self):
        self.assertEqual(break_vigenere.attack(""), ("", ""))
        self.assertEqual(break_vigenere.attack("..."), ("", ""))
        key, plain = break_vigenere.attack("Q")
        self.assertEqual(len(plain), 1)


# ---------- C3

class TestC3ColumnarBreaker(unittest.TestCase):
    def test_twenty_generated(self):
        rng = random.Random(6)
        for _ in range(20):
            n = rng.choice((4, 5, 6))
            key = random_key(n, rng)
            cipher = columnar.encrypt(random_piece(200, rng), key)
            order, plain = break_columnar.attack(cipher, n)
            self.assertEqual(plain, columnar.decrypt(cipher, key))
            self.assertEqual(list(order), columnar.key_order(key))

    def test_edge_cases(self):
        with self.assertRaises(ValueError):         # más corto que el nº de columnas
            break_columnar.attack("ABC", 5)
        with self.assertRaises(ValueError):         # no es múltiplo
            break_columnar.attack("ABCDEFG", 3)
        with self.assertRaises(ValueError):
            break_columnar.attack("", 3)


# ---------- D

class TestDPipeline(unittest.TestCase):
    def test_vigenere(self):
        code, out = run_program(attack, [], break_vigenere.vigenere_encrypt(PLAIN[:400], "LEMON"))
        self.assertEqual(code, 0)
        self.assertIn("key: LEMON", out)
        self.assertIn("coset_ic", out)      # tiene que enseñar las medidas, no solo la respuesta

    def test_columnar(self):
        code, out = run_program(attack, [], columnar.encrypt(PLAIN[:200], "CIPHER", pad="E"))
        self.assertEqual(code, 0)
        self.assertIn("family: transposition", out)
        self.assertIn("plaintext: " + PLAIN[:200], out)

    def test_monoalphabetic(self):
        rng = random.Random(7)
        code, out = run_program(attack, [], random_substitution(PLAIN[:400], rng))
        self.assertIn("monoalphabetic", out)

    def test_edge_cases(self):
        self.assertEqual(run_program(attack, [], "")[0], 1)
        self.assertEqual(run_program(attack, [], "A")[0], 1)

    def test_crypto_cli(self):
        out = run_program(crypto, ["railfence", "encrypt", "--rails", "3"], "MYSECRETMESSAGE")[1]
        self.assertEqual(out.strip(), "MCMAYERTESGSESE")
        out = run_program(crypto, ["columnar", "encrypt", "--key", "CIPHER"], "MYSECRETMESSAGE")[1]
        self.assertEqual(out.strip(), "MEACSXEEXYTGSMERSX")
        out = run_program(crypto, ["columnar", "decrypt", "--key", "CIPHER"], "MEACSXEEXYTGSMERSX")[1]
        self.assertEqual(out.strip(), "MYSECRETMESSAGEXXX")
        out = run_program(crypto, ["measure", "ic"], "CRYPTANALYSIS")[1]
        self.assertEqual(out.strip(), "0.0385")
        out = run_program(crypto, ["measure", "kasiski"], KASISKI_TEXT)[1]
        self.assertIn("distances: [15, 35, 50]", out)


if __name__ == "__main__":
    unittest.main()