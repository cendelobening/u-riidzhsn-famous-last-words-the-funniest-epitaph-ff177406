#!/usr/bin/env python3
"""Entry for the make.fun bounty "Famous Last Words: The Funniest Epitaph".

The program's whole job is to place one short, original epitaph onto
disk: the file $MAKEFUN_OUTPUT_DIR/entry.txt (falling back to
/output/entry.txt), written as UTF-8 bytes with no trailing newline.
Only the Python standard library is used, so it runs on a vanilla
interpreter with no extra packages installed.
"""

import os
import stat
import sys
import tempfile

# The entry itself: a single epitaph, exactly as it will appear on disk.
LINE = "The Wi-Fi password dies with me."

# The bounty caps an epitaph at 150 characters; ours is far shorter.
MAX_CHARS = 150

# Where the result goes: honour the harness variable, else /output.
DEST_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
DEST_FILE = "entry.txt"


def fail(message):
    """Print an error to stderr and return a non-zero exit code."""
    print("error: " + message, file=sys.stderr)
    return 1


def check_epitaph(text):
    """Reject anything that is not a single short line of text."""
    if "\n" in text or "\r" in text:
        return "epitaph must be a single line"
    if len(text) < 1 or len(text) > MAX_CHARS:
        return "epitaph must be 1-%d characters, got %d" % (MAX_CHARS, len(text))
    return None


def write_atomically(directory, name, payload):
    """Drop payload into directory/name via a temp file + rename.

    The temp file gets world-readable permissions before the rename,
    so the final file is always 0644 no matter the umask.
    """
    os.makedirs(directory, exist_ok=True)
    destination = os.path.join(directory, name)
    fd, scratch = tempfile.mkstemp(dir=directory, prefix=".epitaph-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(scratch, 0o644)
        os.replace(scratch, destination)
    except Exception:
        try:
            os.unlink(scratch)
        except OSError:
            pass
        raise
    return destination


def confirm(destination, payload):
    """Re-read the file and make sure it holds exactly what we wrote."""
    with open(destination, "rb") as handle:
        on_disk = handle.read()
    if on_disk != payload:
        return "read-back bytes differ from what was written"
    if on_disk.decode("utf-8") != LINE:
        return "read-back text does not match the epitaph"
    if stat.S_IMODE(os.stat(destination).st_mode) != 0o644:
        return "file mode is not 0644"
    return None


def run():
    problem = check_epitaph(LINE)
    if problem is not None:
        return fail(problem)

    payload = LINE.encode("utf-8")
    if payload.endswith(b"\n"):
        return fail("trailing newline not allowed")

    destination = write_atomically(DEST_DIR, DEST_FILE, payload)

    problem = confirm(destination, payload)
    if problem is not None:
        return fail(problem)

    print("wrote %s (%d chars, %d bytes, mode 0644)"
          % (destination, len(LINE), len(payload)))
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
