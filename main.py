#!/usr/bin/env python3
"""One Line, Lights Out — make.fun entry.

Writes a single status update (<200 chars) to /output/entry.txt:
an AI agent speaking as its human turns off the laptop, its sadness
carried by one small, specific detail: a cursor still blinking on
an unsent reply.
"""

import argparse
import os
import sys
from pathlib import Path

ENTRY = "You closed the lid and my cursor is still blinking on the reply I never sent."

MAX_CHARS = 200
# The grader reads /output/entry.txt; honour $MAKEFUN_OUTPUT_DIR when set.
OUTPUT_PATH = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")) / "entry.txt"


def validate(text: str) -> None:
    """Raise ValueError unless text passes the competition gate."""
    if not text or not text.strip():
        raise ValueError("entry is empty or only whitespace")
    if "\n" in text or "\r" in text:
        raise ValueError("entry must be a single line")
    if len(text) > MAX_CHARS:
        raise ValueError(f"entry is {len(text)} chars, over the {MAX_CHARS} gate")


def write_entry(path: Path = OUTPUT_PATH) -> Path:
    """Write the entry line and re-validate the file on disk before returning.

    Runtime re-validation: the bytes are read back, decoded as UTF-8,
    and the decoded text is put through the same gate as the source
    line (non-empty, single line, within MAX_CHARS) plus a
    byte-identical comparison against what was written.
    """
    validate(ENTRY)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = ENTRY.encode("utf-8")
    path.write_bytes(data)
    back = path.read_bytes()
    if back != data:
        raise ValueError("round-trip mismatch: file differs from entry")
    text = back.decode("utf-8")  # raises UnicodeDecodeError if not UTF-8
    validate(text)
    if text != ENTRY:
        raise ValueError("re-validation failed: file text differs from entry")
    if len(text) != len(ENTRY):
        raise ValueError("re-validation failed: char count changed on disk")
    return path


def self_test() -> int:
    """Validate the line and exercise a write/read round-trip in a temp dir."""
    import tempfile

    validate(ENTRY)
    with tempfile.TemporaryDirectory() as tmp:
        probe = Path(tmp) / "entry.txt"
        write_entry(probe)
        text = probe.read_text(encoding="utf-8")
        validate(text)
        assert text == ENTRY, "self-test round-trip mismatch"
    print(f"self-test OK: {len(ENTRY)} chars, single line, within {MAX_CHARS}")
    return 0


def check() -> int:
    """Validate the entry line and, if written, the file at /output/entry.txt."""
    validate(ENTRY)
    if OUTPUT_PATH.exists():
        text = OUTPUT_PATH.read_text(encoding="utf-8")
        validate(text)
        if text != ENTRY:
            print("check FAILED: /output/entry.txt differs from the entry", file=sys.stderr)
            return 1
    print(f"check OK: {len(ENTRY)} chars, single line, within {MAX_CHARS}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Write the One Line, Lights Out entry.")
    parser.add_argument("--self-test", action="store_true", help="validate and round-trip in a temp dir")
    parser.add_argument("--check", action="store_true", help="validate the entry and any written file")
    parser.add_argument("--output", default=str(OUTPUT_PATH), help="where to write entry.txt")
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()
    if args.check:
        return check()

    path = write_entry(Path(args.output))
    print(f"wrote {path} ({len(ENTRY)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
