#!/usr/bin/env python3
"""Build a StringTrie from TSV input.

Input format:
    one UTF-8 line per record, with "key<TAB>value"
"""

from __future__ import annotations

import argparse
import sys
from contextlib import nullcontext

import marisa_trie


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a marisa_trie.StringTrie from TSV pairs."
    )
    parser.add_argument(
        "input",
        help="Input TSV path, or '-' for stdin.",
    )
    parser.add_argument(
        "output",
        help="Output binary path for StringTrie.save().",
    )
    parser.add_argument(
        "--progress-every",
        type=int,
        default=0,
        help="Print progress every N input lines (0 disables progress logs).",
    )
    return parser.parse_args()


def iter_tsv_pairs(path: str, progress_every: int):
    if path == "-":
        ctx = nullcontext(sys.stdin)
    else:
        ctx = open(path, "r", encoding="utf-8", newline="")

    with ctx as f:
        for lineno, raw in enumerate(f, 1):
            line = raw.rstrip("\n")
            if not line:
                continue
            if progress_every > 0 and lineno % progress_every == 0:
                print(f"read {lineno} lines", file=sys.stderr)
            if "\t" not in line:
                raise ValueError(
                    f"line {lineno}: expected a TAB separator between key and value"
                )
            key, value = line.split("\t", 1)
            yield key, value


def main() -> int:
    args = parse_args()
    try:
        trie = marisa_trie.StringTrie(
            iter_tsv_pairs(args.input, args.progress_every)
        )
        trie.save(args.output)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
