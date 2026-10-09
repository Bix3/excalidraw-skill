#!/usr/bin/env python3
"""Extract an embedded Excalidraw scene from a PNG using ImageMagick.

Requires Python 3 and ImageMagick 7 (magick on PATH).
Supports compressed/uncompressed bstring and raw scene metadata.
"""

import argparse
import json
from pathlib import Path
import subprocess
import zlib


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="Example: ./scripts/extract-excalidraw.py editable.png scene.excalidraw",
    )
    parser.add_argument("input_png", type=Path, help="PNG with an embedded scene")
    parser.add_argument("output_scene", type=Path, help=".excalidraw file to write (overwrites)")
    args = parser.parse_args()

    result = subprocess.run(
        [
            "magick", "identify",
            "-format", "%[application/vnd.excalidraw+json]",
            str(args.input_png.resolve()),
        ],
        stdout=subprocess.PIPE,
        check=True,
    )
    if not result.stdout:
        parser.exit(1, "No embedded Excalidraw scene found.\n")

    try:
        # PNG tEXt stores Latin-1, including the encoded binary string.
        text = result.stdout.decode("latin1")
        metadata = json.loads(text)
        if "encoded" in metadata:
            if metadata["encoding"] != "bstring":
                raise ValueError("unsupported scene encoding")
            scene = metadata["encoded"].encode("latin1")
            if metadata["compressed"]:
                scene = zlib.decompress(scene)
        else:
            if metadata["type"] != "excalidraw":
                raise ValueError("metadata is not an Excalidraw scene")
            scene = text.encode("utf8")
    except (ValueError, KeyError, TypeError, AttributeError, zlib.error) as error:
        parser.exit(1, f"Cannot decode embedded scene: {error}\n")

    args.output_scene.write_bytes(scene)
    print(f"Wrote {args.output_scene}")


if __name__ == "__main__":
    main()
