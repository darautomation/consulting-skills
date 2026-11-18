#!/usr/bin/env python3
"""Pre-send checks for a client message. Exit 0 = OK to show for approval, 1 = blocked.

Checks:
  1. Recipient's first name (or its stem / transliteration) appears in the text or the source notes.
  2. No other client's name from --others appears in the text.
  3. No leftover placeholders: {..}, <..>, TODO, [insert ...], XXX.
  4. No banned phrases (from --banned or built-in AI-tell list).
  5. Length: warns above --max chars (messenger limit), suggests splitting.

Usage:
  python3 guard_check.py --to "Anna" --text recap.md
  python3 guard_check.py --to "Анна" --text recap.md --source notes.txt --others clients.txt
"""
import argparse
import re
import sys

TRANSLIT = str.maketrans({
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e", "ж": "zh", "з": "z", "и": "i",
    "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t",
    "у": "u", "ф": "f", "х": "kh", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch", "ы": "y", "э": "e",
    "ю": "yu", "я": "ya", "ь": "", "ъ": "",
})
PLACEHOLDER_RE = re.compile(r"\{[^}\n]{1,40}\}|<[A-Za-zА-Яа-я _-]{2,30}>|\bTODO\b|\bXXX\b|\[insert[^\]]*\]", re.I)
DEFAULT_BANNED = [
    "hope this finds you well", "hope you're well", "feel free to reach out", "don't hesitate to",
    "i hope this helps", "delve", "in today's fast-paced world", "\u2014",
    "надеюсь, это было полезно", "не стесняйтесь обращаться", "важно отметить",
]


def norm(s):
    return s.lower().translate(TRANSLIT)


ENDINGS = "(?:a|u|e|y|i|o|om|oy|ov|ya|yu|ye|ey|em|ii|iya|iyu|iey|ie|s|'s)?"


def name_base(name):
    n = norm(name.strip().split()[0]) if name.strip() else ""
    for suf in ("iya", "ya"):
        if n.endswith(suf) and len(n) > len(suf) + 2:
            return n[: -len(suf)]
    if len(n) >= 4 and n[-1] in "aeiouy":
        return n[:-1]  # Olga -> olg (Ольгу, Ольге, Ольгой), Anna -> ann
    return n


def contains_name(text, name):
    base = name_base(name)
    if len(base) < 2:
        return False
    return re.search(r"\b" + re.escape(base) + ENDINGS + r"\b", norm(text)) is not None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--to", required=True, help="recipient first name")
    ap.add_argument("--text", required=True, help="file with the message draft")
    ap.add_argument("--source", help="file with the source notes/transcript of this client's call")
    ap.add_argument("--others", help="file with other clients' names, one per line")
    ap.add_argument("--banned", help="file with extra banned phrases, one per line")
    ap.add_argument("--max", type=int, default=3500)
    a = ap.parse_args()

    text = open(a.text, encoding="utf-8").read()
    source = open(a.source, encoding="utf-8").read() if a.source else ""
    problems, warnings = [], []

    if not (contains_name(text, a.to) or (source and contains_name(source, a.to))):
        problems.append(f"recipient '{a.to}' not found in the draft or the source notes: possible wrong person")

    if a.others:
        for line in open(a.others, encoding="utf-8"):
            other = line.strip()
            if not other or name_base(other) == name_base(a.to):
                continue
            first = other.split()[0]
            if len(first) >= 3 and contains_name(text, first):
                problems.append(f"another client's name in the text: '{other}'")

    for m in PLACEHOLDER_RE.finditer(text):
        problems.append(f"placeholder left: '{m.group(0)}'")

    banned = list(DEFAULT_BANNED)
    if a.banned:
        banned += [l.strip() for l in open(a.banned, encoding="utf-8") if l.strip()]
    low = text.lower()
    for b in banned:
        if b.lower() in low:
            warnings.append(f"banned phrase: '{b}'")

    if len(text) > a.max:
        warnings.append(f"{len(text)} chars > {a.max}: split at paragraph boundaries before sending")

    for p in problems:
        print("BLOCK  " + p)
    for w in warnings:
        print("WARN   " + w)
    if not problems and not warnings:
        print("OK")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
