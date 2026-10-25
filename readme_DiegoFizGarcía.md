# Practice 2 (Cryptography):

Student: Diego Fiz García.

GitHub repository: https://github.com/DiegoFiz/cryptography-practice2

## 1. How to run the project

The project is written entirely in Python 3.14, using only the standard library, and all the files are in the same folder:

- `railfence.py` (A1), `columnar.py` (A2 and A3), `measure.py` (B1 and B2), `kasiski.py` (B3), `keylength.py` (C1), `break_vigenere.py` (C2), `break_columnar.py` (C3), and `attack.py` and `crypto.py` (Part D).
- `basics.py` and `break_caesar.py` come from Practice 1. As the statement warned, I had to fix both of them before working on Part C. `basics.py` was missing `normalise`, `chi_squared`, the frequency tables and the index of coincidence constants that the new modules import. As for `break_caesar.py`, it imported two files that no longer existed and had the `return` inside the loop, so it only tried the first shift.
- `experiments.py` generates every table in this report with fixed seeds, so the results can be reproduced.
- The `tests/` folder contains the test suite (`test_practice2.py`) and the English text it uses (`sample_text.py`).
- The `.txt` files are the inputs of the commands listed below: `message.txt`, `cipher.txt`, `rail_cipher.txt` and the three hands-on exercises from the slides (`t2_mono.txt`, `t3_transposition.txt` and `t4_vigenere.txt`).

To check each part I used the following commands from the project folder:

```
python crypto.py railfence encrypt --rails 3 --in message.txt
python crypto.py railfence decrypt --rails 3 --in rail_cipher.txt
python crypto.py columnar encrypt --key CIPHER --in message.txt
python crypto.py columnar encrypt --key CIPHER --pad Q --in message.txt
python crypto.py columnar decrypt --key CIPHER --in cipher.txt
python crypto.py measure ic --in cipher.txt
python crypto.py measure classify --in cipher.txt
python crypto.py measure kasiski --in t4_vigenere.txt
python attack.py --in t4_vigenere.txt
python attack.py --in t3_transposition.txt
python attack.py --in t3_transposition.txt --cols 6
python attack.py --in t2_mono.txt
```

`attack.py` also accepts the `--lang es` option. In every case the input is normalised first: it is converted to uppercase and every character outside the A-Z range is removed. Accents are separated before this step, so an "á" becomes "A" instead of being lost.

Decrypting a padded text returns the text with its padding, for example `MYSECRETMESSAGEXXX`. When there is an error (a file that does not exist, a missing `--rails` or a length that is not a multiple of the number of columns, among others), the program shows a clear message and exits with an error code, without producing a *traceback*.

As a final check of the pipeline, I used the three hands-on exercises from the slides. `attack.py` solves all of them without any intervention:

| File | Measurements shown | Result |
|---|---|---|
| `t4_vigenere.txt` (T4) | IC = 0.0413, chi2/n = 6.05, first coset_ic above the bar at m = 6 (0.0658), Kasiski factor 6 in 3/3 distances | key `CIPHER`, "THECRYPTANALYSTNEVERHASTHEKEY..." |
| `t3_transposition.txt` (T3) | IC = 0.0797, chi2/n = 0.27, bigram score for n = 2, 3 and 6 | n = 6, "TRANSPOSITIONCHANGESTHEORDERBUTNOTTHELETTERSTHEMSELVES" |
| `t2_mono.txt` (T2) | IC = 0.0657, key length 1 | monoalphabetic; shows the frequency report |

**Check values from the statement.** Every result published in the statement is reproduced exactly:

| Part | Call | Result obtained |
|---|---|---|
| A1 | `encrypt("MYSECRETMESSAGE", 2)` | `MSCEMSAEYERTESG` |
| A1 | `encrypt("MYSECRETMESSAGE", 3)` | `MCMAYERTESGSESE` |
| A1 | `encrypt("MYSECRETMESSAGE", 4)` | `MEAYRTSGSCMSEEE` |
| A2 | `key_order("ENIGMA")` | `[2, 6, 4, 3, 5, 1]` |
| A2 | `key_order("ROTOR")` | `[3, 1, 5, 2, 4]` |
| A2 | `key_order("KASISKI")` | `[4, 1, 6, 2, 7, 5, 3]` |
| A2 | `key_order("BLETCHLEY")` | `[1, 6, 3, 8, 2, 5, 7, 4, 9]` |
| A2 | `encrypt("MYSECRETMESSAGE", "CIPHER")` | `MEACSXEEXYTGSMERSX` |
| A2 | `encrypt("THE INDEX OF COINCIDENCE", "KASISKI")` | `HOIICEENETXCDICEFDNON` |
| A3 | `encrypt_double("THESAMEKEYMUSTNEVERBEUSEDTWICE", "ROTOR", "ENIGMA")` | `WCTEIHSTAEVREBEUTMNSUEEDSEEMYK` |
| B1 | `index_of_coincidence("CRYPTANALYSIS")` | 6/156 = 0.0385 |
| B1 | `index_of_coincidence("THEINDEXOFCOINCIDENCE")` | 34/420 = 0.0810 |
| B3 | `repeats(...)["ELQ"]` | `[0, 15, 50]` |
| B3 | longest repeat | `ELQYRJ` at `[0, 50]` |
| B3 | `distances(...)` | `[15, 35, 50]` |

In addition, `columnar decrypt` returns the padded text (`MYSECRETMESSAGEXXX`) and `encrypt` with `--pad Q` produces `MEACSQEEQYTGSMERSQ`, which confirms that the padding is a parameter.

**Tests.** To run them I used `pip install pytest` and then `pytest tests/` from the project folder. They can also be run without installing anything with `python -m unittest discover -s tests -v`. There are 32 tests in total, covering:

- every check value from the statement;
- the full encryption and decryption of every cipher in Part A, including a double transposition of 23 letters, which is not a multiple of either 5 or 6;
- the index of coincidence and Kasiski examination values;
- at least 20 generated and correctly broken ciphertexts for each attack in Part C (21 are generated for C1 and C2);
- the command-line interface;
- the edge cases: empty input, a single letter, no letters and a ciphertext shorter than the number of columns.

With Python 3.14, `pytest tests/` returns `32 passed` and `python -m unittest discover -s tests -v` returns `OK`.

**Measurements.** The command `python experiments.py --theory theory` generates every table (they can also be obtained separately with `--only b1|calib|b2|c1|sweep|divisors|c2|c3|time`), and it needs the four theory presentations (T1–T4, `.pptx`) in a folder called `theory`. The reference text is the English prose of those slides (48,412 letters, without the ciphertext examples), while the bigram table for C3 comes from a different text, `pydoc_data.topics`, so that the attack is never evaluated with the same text used to build its score.

## 2. Padding and double transposition (A3)

With 30 letters and keys of length 5 (`ROTOR`) and 6 (`ENIGMA`), neither of the two passes needs padding. The problem appears when the length is not a multiple of both.

A naive implementation pads at every pass: first up to a multiple of 5 and then again up to a multiple of 6. I checked it with `ATTACKATDAWNHOLDTHEBRID` (23 letters):

```
pass 1 (ROTOR, adds 2 X):    TANTIADOEXAKWDRCALBXTTHHD          (25 letters)
pass 2 (ENIGMA, adds 5 X):   AKLHXTDWBDTXCTXNERTXIAAHXAODXX     (30 letters)
naive decrypt_double:        WTDDBDAXOXRNXETCTXXTAIXAHLAXKH     <- wrong result
```

The program does not even produce an error. Undoing the second pass gives 30 letters: the 25 real ones plus the 5 X of the second padding. Since 30 is also a multiple of 5, `decrypt(..., "ROTOR")` builds a grid of 30/5 = 6 rows instead of 5. As a result, every boundary between columns moves and every letter goes back to a wrong position.

To undo the encryption correctly, those 5 letters would have to be removed first, but the receiver has no way of knowing how many there are. The intermediate length must be a multiple of 5 between 25 and 30, and both 25 and 30 are possible: a 23-letter message and a 30-letter message both produce a 30-letter ciphertext. Moreover, a padding X cannot be told apart from a real X of the message.

My `encrypt_double` function avoids this problem by padding only once, at the beginning, up to a multiple of lcm(5, 6) = 30. This way both grids are full and no pass adds extra padding. So `decrypt_double` only has to undo the passes in reverse order (first `kw2` and then `kw1`), and it returns `ATTACKATDAWNHOLDTHEBRID` followed by 7 X. It also rejects lengths that are not a multiple of the lcm. The trade-off is that the padding can be up to lcm − 1 letters long.

## 3. Minimum trustworthy length for the index of coincidence (B1)

`index_of_coincidence` applies the definition with the n(n − 1) denominator. The word `CRYPTANALYSIS` gives 6/156 = 0.0385, exactly the value expected for random letters, even though it is an English word.

To determine from what length the index can be trusted, I measured how often it places a text on the wrong side of the mid-point between random letters and English, (0.0385 + 0.0667)/2 = 0.0526. For each length I used 1000 English text fragments and 1000 strings of uniform random letters:

| n | English IC (mean ± sd) | English below the mid-point | Random IC (mean ± sd) | Random above the mid-point |
|---|---|---|---|---|
| 13 | 0.0577 ± 0.0273 | 55.5 % | 0.0375 ± 0.0205 | 15.4 % |
| 20 | 0.0619 ± 0.0200 | 29.1 % | 0.0390 ± 0.0135 | 20.4 % |
| 30 | 0.0632 ± 0.0149 | 22.4 % | 0.0385 ± 0.0091 | 7.7 % |
| 40 | 0.0647 ± 0.0124 | 15.4 % | 0.0386 ± 0.0067 | 3.4 % |
| 50 | 0.0651 ± 0.0103 | 8.4 % | 0.0387 ± 0.0057 | 1.3 % |
| 60 | 0.0660 ± 0.0101 | 5.2 % | 0.0383 ± 0.0044 | 0.5 % |
| 80 | 0.0661 ± 0.0082 | 2.3 % | 0.0384 ± 0.0033 | 0.0 % |
| 100 | 0.0669 ± 0.0075 | 0.3 % | 0.0386 ± 0.0027 | 0.0 % |
| 150 | 0.0667 ± 0.0061 | 0.3 % | 0.0386 ± 0.0018 | 0.0 % |

My answer is **approximately 100 letters**. The criterion I followed is that the index must be wrong less than 1 % of the time in both directions, and this holds from 100 letters onwards (0.3 % and 0.0 %). With 80 letters it still fails 2.3 % of the time. With 13 letters, which is the length of `CRYPTANALYSIS`, more than half of the English texts look random, so that value gives no information about the word.

The table also shows that the spread of random text decreases roughly as 1/n (0.0027 with 100 letters and 0.0018 with 150), while the spread of English decreases more slowly, roughly as 1/√n. Therefore, it is the English text that determines the minimum length.

## 4. Family classifier (B2)

The `classify` function computes chi2/n with the scoring function from Practice 1 (`chi_squared`, in `basics.py`) against the frequency table of the language. It returns `"transposition"` if the value is below **1.72** and `"substitution"` otherwise. A transposition only changes the position of the letters, so the counts are still those of English and chi2/n is small. A substitution, on the other hand, changes the letters, and chi2/n increases considerably.

**Choice of the threshold.** To avoid setting the threshold arbitrarily, `experiments.py --only calib` builds an independent training set, with seed 2026, different from the one used for the tables. It is made up of 600 transpositions without padding and 600 monoalphabetic substitutions with random keys, 150 of each type for lengths 60, 120, 250 and 400. Then every threshold between 0.20 and 4.00 is tried in steps of 0.01 and the errors are counted. The minimum (10 errors out of 1200) is reached for any value between 1.69 and 1.75, so I chose the mid-point of the interval, 1.72.

**Measurement.** The test set, generated with seed 7, contains 150 columnar transpositions (with random keys of 4 to 9 letters) and 150 monoalphabetic samples per length. I ran the measurement twice, changing only the padding: first with a fixed `X` and then with random letters drawn from the English distribution. For this, the `pad` parameter of `encrypt` accepts a string of letters.

| Length | pad = X: trans. errors | subst. errors | **total error** | pad ~ English: trans. errors | subst. errors | **total error** |
|---|---|---|---|---|---|---|
| 60 | 58/150 | 0/150 | **19.3 %** | 3/150 | 1/150 | **1.3 %** |
| 120 | 25/150 | 3/150 | **9.3 %** | 0/150 | 0/150 | **0.0 %** |
| 250 | 0/150 | 2/150 | **0.7 %** | 0/150 | 2/150 | **0.7 %** |
| 400 | 0/150 | 2/150 | **0.7 %** | 0/150 | 0/150 | **0.0 %** |

**1. At which lengths does the classifier work and at which does it fail?**
With X padding, it works correctly with 250 and 400 letters (0.7 % error) and fails with 60 (19.3 %) and 120 (9.3 %). Almost every error is a transposition classified as a substitution. With padding drawn from the English distribution, on the other hand, it already works with 60 letters (1.3 %). The few remaining substitution errors (at most 2/150) are caused by random keys that happen to map frequent letters to other frequent letters, so the result still looks like English.

**2. Why does the error change so much when only the pad character is changed?**
The chi-squared statistic divides by the expected count e_L = n · p_L, which is very small for X: p_X = 0.0015, so in 60 letters only 0.09 X are expected. Each padding X is therefore a very large excess over a minimal expected value, and the term grows with the square of the number of X.

With k padding letters, their contribution to chi2/n is approximately k² / (n² · p_X). For k = 6:

| n | Padding contribution | Comparison with the threshold (1.72) |
|---|---|---|
| 60 | 6.7 | far above |
| 120 | 1.67 | practically equal (hence the 9 % error) |
| 250 | 0.38 | below (almost no errors) |

When the padding follows the English distribution, it cannot be told apart from the rest of the message and does not change the statistic.

**3. 66-letter ciphertext with 6 pad characters.**
The expected count is e_X = 66 · 0.0015 = 0.099. The X term alone is (6 − 0.099)² / 0.099 = 351.7, so chi2/n = 351.7 / 66 = **5.33** due only to the padding; without it, that term would be approximately 0.0015. This value is **3.1 times my threshold**, so the padding alone is enough for a transposition to be classified as a substitution. This is also the reason why `cipher.txt` (18 letters, 3 of them X) appears as a substitution in Section 1.

**4. Design rule.**
The padding must be impossible to tell apart from the message. It cannot be a fixed character, and even less an infrequent one like X. It must be drawn at random from the same letter distribution as the plaintext, like the random `XQZTU` padding in the columnar transposition slide of T3, and removed through a prior agreement with the receiver. Any fixed choice made by whoever implements the cipher introduces a statistic that can be measured.

## 5. Why not use the greatest common divisor (B3)

The `repeats` function finds every sequence of three or more letters that appears more than once, `distances` computes the gap between consecutive occurrences and `factor_tally` counts how many distances each factor divides.

In the example from the statement, gcd(15, 35, 50) = 5 is correct, but the greatest common divisor is only right if every distance is a multiple of the key length. It fails without any warning in two situations:

- **Too small:** a single coincidental repeat, that is, a distance that is not a multiple of m, is enough for the gcd to drop to a smaller divisor of m, usually 1. This happens in the full 526-letter message of the T4 slides, where the gcd of all the distances is 1 although the key has length 6. If a coincidental distance of 16 were added to the example from the statement, the result would be gcd(15, 35, 50, 16) = 1, while `factor_tally` would still place 5 in 3 of the 4 distances.
- **Too large:** if, by chance, every distance is a multiple of 2m, the gcd returns 2m.

`factor_tally` does not have this problem, since a coincidental distance only adds one unit to a few factors instead of invalidating the result. The key length is the largest factor that still appears in most of the distances.

I also only take into account the distances of maximal repeats (`maximal_repeats`), that is, those that cannot be extended either to the left or to the right. This way, `ELQYRJ` is counted only once and not also as `ELQY`, `LQYR`, etc.

**Results obtained.** On the ciphertext from the statement, `repeats` finds `ELQ` at positions 0, 15 and 50, and the longest repeat is `ELQYRJ`, at 0 and 50. The distances are 15, 35 and 50, and `factor_tally` returns 3 for factor 5, 1 for factors 2, 3, 7, 10 and 15, and 0 for the rest. Factor 5 is the only one that divides all three distances, and it is the correct length.

On the Vigenère exercise from the T4 slides (`t4_vigenere.txt`), the maximal repeats are `VPT` (positions 0 and 84), `WHW` (20 and 44) and `BPS` (31 and 37), with distances 6, 24 and 84. Factor 6 appears in all three distances and 12 in two; the pipeline confirms length 6 with the index of coincidence of the cosets and recovers the key `CIPHER`.

## 6. Key length: coset table (C1)

The `coset_ic` function splits the ciphertext into m cosets and returns the average of their indices of coincidence. `find_key_length` returns the **smallest** value of m whose average is "clearly" above the baseline. In my implementation, "clearly" means that the average has covered at least 70 % of the distance between the value of random letters and that of English:

average ≥ κ_r + 0.7 · (κ_p − κ_r) = 0.0385 + 0.7 · (0.0667 − 0.0385) = **0.0582**

I determined the value 0.7 experimentally (`--only sweep`, with 720 Vigenère ciphertexts with keys of 3, 5, 7 and 9 letters and lengths of 100, 200 and 400):

| FRACTION | 0.5 | 0.6 | 0.7 | 0.8 | 0.9 |
|---|---|---|---|---|---|
| bar | 0.0526 | 0.0554 | 0.0582 | 0.0611 | 0.0639 |
| key length correct | 0.840 | 0.894 | **0.900** | 0.889 | 0.839 |

If no value of m reaches the bar, as happens with very short texts, the function returns the smallest m whose average reaches at least 90 % of the maximum.

The full table for one of my test ciphertexts (400 letters and key `CIPHER`, that is, m = 6) is shown below. `find_key_length` returns 6:

| m | coset_ic | | m | coset_ic | |
|---|---|---|---|---|---|
| 1 | 0.0438 | | 9 | 0.0556 | |
| 2 | 0.0534 | **divisor** | 10 | 0.0519 | |
| 3 | 0.0562 | **divisor** | 11 | 0.0434 | |
| 4 | 0.0534 | | **12** | **0.0788** | **multiple** |
| 5 | 0.0432 | | 13 | 0.0406 | |
| **6** | **0.0757** | **true length** | 14 | 0.0557 | |
| 7 | 0.0444 | | 15 | 0.0585 | |
| 8 | 0.0518 | | 16 | 0.0508 | |

The divisors 2 and 3 stay at intermediate values, since their cosets mix 3 and 2 alphabets respectively. The values of m that share a factor with 6 (4, 8, 9, 10, 14, 15 and 16) are also somewhat higher than the rest. The most important point is that **the highest average in the whole table corresponds to m = 12 (0.0788), not to m = 6 (0.0757)**. Therefore, a function that returned the maximum average would have answered 12.

However, the rule is not infallible. With `--only divisors` (3000 ciphertexts of 400 letters and keys of 3 to 5 different letters), the length obtained was wrong 47 times (1.6 %), and in 41 of them it was a divisor of the real length. For example, with the key `WMLC` it returned 2 (coset_ic 0.0601) instead of 4 (0.0817), because the two shifts that fall in each coset of m = 2 are close enough for their mixture to pass the bar.

## 7. Automatic Vigenère attack (C2)

The `attack` function determines the key length with C1, splits the text into cosets, breaks each one with the Caesar breaker from Practice 1 and joins the shifts to form the key. The tests were carried out with random keys whose real period is m, with 100 trials per cell:

**Complete key recovered:**

| m \ n | 100 | 150 | 200 | 300 | 400 |
|---|---|---|---|---|---|
| 3 | 0.77 | 0.84 | 0.91 | 0.97 | 0.98 |
| 5 | 0.49 | 0.81 | 0.86 | 0.99 | 0.99 |
| 7 | 0.13 | 0.48 | 0.70 | 0.88 | 0.97 |
| 9 | 0.07 | 0.19 | 0.45 | 0.74 | 0.92 |

**Only the key length correct:**

| m \ n | 100 | 150 | 200 | 300 | 400 |
|---|---|---|---|---|---|
| 3 | 0.80 | 0.86 | 0.91 | 0.97 | 0.98 |
| 5 | 0.78 | 0.93 | 0.96 | 1.00 | 0.99 |
| 7 | 0.81 | 0.95 | 0.96 | 0.99 | 1.00 |
| 9 | 0.73 | 0.90 | 0.98 | 0.99 | 1.00 |

**1. Which quantity governs each table?**
Finding the length depends on the **total length n**. The average of the coset_ic values uses all n letters (m cosets of n/m letters each), so its noise hardly depends on m. For this reason, the four rows of the second table are practically equal and all of them are above 0.9 from 150–200 letters onwards.

Recovering the complete key depends instead on the **number of letters per coset, n/m**. Each Caesar break only has n/m letters, and all m of them must be right at the same time: P(key) ≈ P(correct length) · q(n/m)^m, where q is the probability of getting one coset right. If q = (P_key / P_length)^(1/m) is estimated from both tables, it turns out that q depends only on n/m and not on m:

| Letters per coset | Approximate q |
|---|---|
| 11–14 | 0.77 |
| 20–22 | 0.91 |
| 30–33 | 0.97 |
| 40–44 | 0.98 |

This behaviour matches what I observed in Practice 1 with the Caesar breaker.

**2. 200 letters with m = 5 against m = 9.**
In both cases the length is found correctly (0.96 and 0.98), so the failure does not come from that step. With m = 5, each coset contains 200/5 = **40 letters**, q ≈ 0.98 and 0.98^5 ≈ 0.90 (measured value: 0.86). With m = 9, each coset contains 200/9 ≈ **22 letters**, q ≈ 0.92 and, since all nine cosets must be right, 0.92^9 ≈ 0.47 (measured value: 0.45). In other words, the attack fails when breaking the cosets with Caesar, not when determining the length.

**3. Rule of thumb.**
**n ≳ 40 · m**, that is, about 40 letters per coset, and never less than 150–200 letters in total so that the length is determined correctly: n ≳ max(40 · m, 200). In general, n ≥ m · ℓ, where ℓ is the coset length that makes q(ℓ)^m reach the desired success level. Since all m cosets must be right at the same time, ℓ grows slowly with m.

## 8. Columnar transposition attack (C3)

The `attack` function tries the n! column orders and scores each candidate with the bigram log-probability, that is, the sum of log p(xy) for every pair of consecutive letters. The table (`bigram_table`) is built from `pydoc_data.topics`, taking the first 150,000 letters of the Python documentation, and every count starts at 1 so that no bigram has zero probability.

To speed up the computation, I do not rebuild the text for every permutation. Instead, I precompute `inner[a][b]`, the score of placing block b immediately to the right of block a, and `wrap[a][b]`, the score of going from the end of one row to the beginning of the next. This way, each permutation only needs n additions.

**Why single-letter frequencies are useless here:** every candidate order is an anagram of the same ciphertext, with exactly the same letters and counts, so any score based on single letters gives the same value to all n! candidates.

Plaintext recovered exactly (100 trials per cell, X padding):

| columns \ n | 60 | 120 | 200 |
|---|---|---|---|
| 4 | 1.00 | 1.00 | 1.00 |
| 5 | 0.97 | 1.00 | 1.00 |
| 6 | 0.93 | 1.00 | 1.00 |
| 7 | 0.87 | 0.99 | 1.00 |

The few failures are concentrated in 60-letter texts with 5 to 7 columns. In that case, each column only contains between 9 and 12 letters, and there are not enough bigrams to tell the correct order apart from a similar one.

**Largest value of n in under ten seconds: n = 10.** Time of one exhaustive attack on 200 letters (`--only time`):

| n | orderings | time |
|---|---|---|
| 8 | 40,320 | 0.02s |
| 9 | 362,880 | 0.27s |
| 10 | 3,628,800 | 2.55s |
| 11 | 39,916,800 | 30.86s |

Each additional column multiplies the time by approximately n, so with n = 11 the ten seconds are already far exceeded.

**How to extend this limit (not implemented):** with *hill climbing*, following the method described at the end of topic T4 for monoalphabetic ciphers. Starting from a random column order, two columns are swapped (or a block is moved). The change is kept if the bigram score improves and undone otherwise; when the process gets stuck, it restarts from another random order. The method works because the score improves gradually as more columns end up next to their real neighbours, so there is no need to go through all n! orders.

## 9. The value Part D depends on

Before trying any attack, the pipeline makes its decision based on **chi2/n of the ciphertext against the language table**, together with the index of coincidence. This value depends on a single property of the cipher: **whether it preserves the single-letter distribution of the plaintext**, that is, whether the letters of the ciphertext are the same as those of the message.

A cipher able to fool the classifier completely would be a substitution that only swaps letters with similar frequencies (E↔T, A↔O, I↔N, S↔H, R↔D, L↔C, U↔M, W↔F, G↔Y, P↔B, V↔K, J↔X, Q↔Z), followed by a columnar transposition. Computed with the English table, these swaps only increase the expected chi2/n by about 0.05, far from 1.72, and a substitution never changes the index of coincidence. Therefore, the pipeline would conclude that it is a transposition and run C3, which would look for a column order in a text whose bigrams no longer correspond to English and would return a meaningless result.

The ADFGVX cipher (T3) produces the opposite failure: its output only uses six letters, so it is classified as a substitution and the pipeline runs the wrong attack.

## 10. Limitations

The cases in which the programs do not work correctly or have restrictions are listed below:

**Spanish is not calibrated:** the 1.72 threshold and the C1 bar have only been measured with English texts. For Spanish I use the same threshold and κ_p = 0.075, taken from the T4 slides, since the course material does not include a Spanish reference text. Also, unless there is a `corpus_es.txt` file next to the code, `break_columnar.py` uses the English bigram table with `--lang es` as well.

**The key length can stop at a divisor:** as explained in Section 6, in approximately 1.6 % of the cases (400 letters and keys of 3 to 5 different letters), `find_key_length` returns a divisor of the real length. For this reason, the C1 and C2 tests generate 21 ciphertexts and require at least 20 of them to be broken correctly.

**Keys with repeated letters:** a key like `ETT` can make the text look like it has a shorter period, in which case the complete key is obtained incorrectly. The C2 tables were obtained with random keys, so this effect is already reflected in them.

**Classifier with X padding:** it fails with short texts (19.3 % error with 60 letters), and around 1 % of random substitutions are classified as transpositions (Section 4).

**Only columnar transposition is attacked:** a rail fence ciphertext is correctly classified as a transposition, but C3 returns a meaningless result. Without the `--cols` option, the pipeline only tries the divisors of the length between 2 and 8, and it does not support columnar transposition without padding (columns of different lengths).

**Monoalphabetic ciphers are not solved automatically:** the statement does not require it. The pipeline shows the frequency report and the rest of the analysis has to be done by hand, as in Practice 1.

**C3 is exhaustive:** it is only feasible in a reasonable time up to n = 10 columns.

**The C3 table may vary slightly depending on the Python version:** the bigram corpus is the documentation of the installed Python version. With Python 3.11, the 60-letter column gives 0.96 / 0.92 / 0.88 instead of 0.97 / 0.93 / 0.87. The results in this report were obtained with Python 3.14.

## 11. Use of artificial intelligence tools

As the statement allows, I used Claude (Anthropic) only as a programming assistant in this practice, specifically to correct code errors made while programming and to verify that, indeed, the results obtained when running the ".py" files are correct.