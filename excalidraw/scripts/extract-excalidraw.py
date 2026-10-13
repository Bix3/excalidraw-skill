#!/usr/bin/env python3
"""Extract an embedded Excalidraw scene directly from PNG text chunks.

Supports tEXt, zTXt, and compressed/uncompressed iTXt metadata, including
compressed/uncompressed bstring envelopes and raw scene JSON.
"""

import argparse
import json
from pathlib import Path
import zlib

from png_chunks import SCENE_KEYWORD, TEXT_CHUNKS, iter_chunks


def read_scene_text(png):
    """Read the first matching text chunk while validating all chunk bounds."""
    text = None
    for chunk_type, start, end in iter_chunks(png):
        if text is not None or chunk_type not in TEXT_CHUNKS:
            continue
        chunk_data = png[start + 8:end - 4]
        keyword, separator, value = chunk_data.partition(b"\0")
        if keyword != SCENE_KEYWORD:
            continue
        if not separator:
            raise ValueError("scene text chunk has no keyword separator")
        if chunk_type == b"tEXt":
            text = value.decode("latin1")
        elif chunk_type == b"zTXt":
            if not value:
                raise ValueError("truncated zTXt scene metadata")
            if value[0] != 0:
                raise ValueError("unsupported zTXt compression method")
            text = zlib.decompress(value[1:]).decode("latin1")
        else:
            if len(value) < 2:
                raise ValueError("truncated iTXt scene metadata")
            compressed, method = value[:2]
            if compressed not in (0, 1) or method != 0:
                raise ValueError("unsupported iTXt compression")
            fields = value[2:].split(b"\0", 2)
            if len(fields) != 3:
                raise ValueError("malformed iTXt scene metadata")
            scene_text = fields[2]
            if compressed:
                scene_text = zlib.decompress(scene_text)
            text = scene_text.decode("utf8")
    return text


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="Example: ./scripts/extract-excalidraw.py editable.png scene.excalidraw",
    )
    parser.add_argument("input_png", type=Path, help="PNG with an embedded scene")
    parser.add_argument("output_scene", type=Path, help=".excalidraw file to write (overwrites)")
    args = parser.parse_args()

    try:
        text = read_scene_text(args.input_png.read_bytes())
        if text is None:
            parser.exit(1, "No embedded Excalidraw scene found.\n")
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
    except (OSError, ValueError, KeyError, TypeError, AttributeError, zlib.error) as error:
        parser.exit(1, f"Cannot decode embedded scene: {error}\n")

    args.output_scene.write_bytes(scene)
    print(f"Wrote {args.output_scene}")


if __name__ == "__main__":
    main()
