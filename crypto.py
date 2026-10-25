#EXERCISE D (Terminal Comands):
#   python crypto.py railfence encrypt --rails 3 --in message.txt
#   python crypto.py columnar  encrypt --key CIPHER --in message.txt
#   python crypto.py columnar  decrypt --key CIPHER --in cipher.txt
#   python crypto.py measure   ic | classify | kasiski --in cipher.txt

import argparse
import sys
import railfence
import columnar
import measure
import kasiski
from basics import normalise


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="crypto.py")
    sub = parser.add_subparsers(dest="cmd", required=True)

    for name in ("railfence", "columnar"):
        p = sub.add_parser(name)
        p.add_argument("mode", choices=["encrypt", "decrypt"])
        p.add_argument("--rails", type=int)
        p.add_argument("--key")
        p.add_argument("--pad", default="X")
        p.add_argument("--in", dest="inp", required=True)

    p = sub.add_parser("measure")
    p.add_argument("what", choices=["ic", "classify", "kasiski"])
    p.add_argument("--lang", default="en", choices=["en", "es"])
    p.add_argument("--in", dest="inp", required=True)

    args = parser.parse_args(argv)
    try:
        with open(args.inp, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(f"error: cannot read {args.inp}: {e.strerror}", file=sys.stderr)
        return 1

    try:
        if args.cmd == "railfence":
            if args.rails is None:
                parser.error("railfence needs --rails")
            if args.mode == "encrypt":
                print(railfence.encrypt(text, args.rails))
            else:
                print(railfence.decrypt(text, args.rails))

        elif args.cmd == "columnar":
            if not args.key:
                parser.error("columnar needs --key")
            key = args.key.upper()
            if args.mode == "encrypt":
                print(columnar.encrypt(text, key, args.pad))
            else:
                print(columnar.decrypt(text, key))

        elif args.what == "ic":
            print(f"{measure.index_of_coincidence(text):.4f}")

        elif args.what == "classify":
            print(measure.classify(text, args.lang))

        else:
            text = normalise(text)
            print("repeats:", kasiski.repeats(text))
            print("distances:", kasiski.distances(text))
            print("factor tally:", kasiski.factor_tally(text))

    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())