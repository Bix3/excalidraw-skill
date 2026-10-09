#!/usr/bin/env python3
"""Embed an Excalidraw scene into a PNG without re-rendering it.

Requires Python 3.8+ and ImageMagick 7 (magick on PATH).
Replaces existing PNG text metadata with the editable scene.
"""

import argparse
import json
from pathlib import Path
import shlex
import subprocess
import zlib


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=(
            "Example: ./scripts/embed-excalidraw.py "
            "scene.excalidraw rendered.png editable.png"
        ),
    )
    parser.add_argument("scene", type=Path, help="source .excalidraw file")
    parser.add_argument("input_png", type=Path, help="existing rendered PNG")
    parser.add_argument("output_png", type=Path, help="editable PNG to write (overwrites)")
    args = parser.parse_args()

    payload = json.dumps(
        {
            "version": "1",
            "encoding": "bstring",
            "compressed": True,
            "encoded": zlib.compress(args.scene.read_bytes()).decode("latin1"),
        },
        ensure_ascii=True,
        separators=(",", ":"),
    )
    # Remove existing text properties so Excalidraw finds our tEXt chunk first.
    command = [str(args.input_png.resolve())]
    with args.input_png.open("rb") as png:
        png.seek(8)
        while header := png.read(8):
            length = int.from_bytes(header[:4], "big")
            if header[4:] in (b"tEXt", b"zTXt", b"iTXt"):
                keyword = png.read(length).split(b"\0", 1)[0].decode("latin1")
                command.extend(["+set", keyword])
                png.seek(4, 1)
            else:
                png.seek(length + 4, 1)

    # -set interprets backslashes and percent signs; escape both literally.
    payload = payload.replace("\\", "\\\\").replace("%", "%%")
    command.extend([
        "-set", "application/vnd.excalidraw+json", payload,
        "-compress", "none",
        "-define", "png:exclude-chunk=date,time",
        "-write", "PNG:" + str(args.output_png.resolve()),
    ])
    # Stdin avoids command-line size limits and -define's value truncation.
    subprocess.run(
        ["magick", "-script", "-"],
        input=shlex.join(command) + "\n",
        text=True,
        check=True,
    )
    print(f"Wrote {args.output_png}")


if __name__ == "__main__":
    main()
