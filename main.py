#!/usr/bin/env python3
"""Famous Last Words: The Funniest Epitaph — make.fun entry.

Writes one original epitaph line to $MAKEFUN_OUTPUT_DIR/entry.txt
(default /output), UTF-8, no trailing newline, a single line of at
most 150 characters. Pure Python standard library only.
"""

import os
import stat
import sys
import tempfile

LINE = "The Wi-Fi password dies with me."

OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
OUTPUT_NAME = "entry.txt"


def main() -> int:
    if not (1 <= len(LINE) <= 150):
        print(f"error: line is {len(LINE)} chars, must be 1-150", file=sys.stderr)
        return 1
    if "\n" in LINE or "\r" in LINE:
        print("error: line must be a single line", file=sys.stderr)
        return 1

    data = LINE.encode("utf-8")
    if data.endswith(b"\n"):
        print("error: trailing newline not allowed", file=sys.stderr)
        return 1
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    target = os.path.join(OUTPUT_DIR, OUTPUT_NAME)

    fd, tmp_path = tempfile.mkstemp(dir=OUTPUT_DIR, prefix=".entry-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, target)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

    with open(target, "rb") as f:
        read_back = f.read()
    if read_back != data:
        print("error: read-back bytes differ", file=sys.stderr)
        return 1
    if read_back.decode("utf-8") != LINE:
        print("error: read-back text mismatch", file=sys.stderr)
        return 1
    if stat.S_IMODE(os.stat(target).st_mode) != 0o644:
        print("error: mode is not 0644", file=sys.stderr)
        return 1

    print(f"wrote {target} ({len(LINE)} chars, {len(data)} bytes, mode 0644)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
