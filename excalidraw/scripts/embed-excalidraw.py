#!/usr/bin/env python
"""Embed an Excalidraw scene into a PNG without re-rendering it.

Replaces all PNG text chunks with one scene tEXt chunk immediately before IEND.
Preserves every other chunk byte-for-byte, including compressed image data.
"""

import argparse
import json
from pathlib import Path
import struct
import zlib

from png_chunks import PNG_SIGNATURE, SCENE_KEYWORD, TEXT_CHUNKS, iter_chunks


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

    try:
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
        # Read everything before writing so input and output may be the same path.
        png = args.input_png.read_bytes()
        chunk_data = SCENE_KEYWORD + b"\0" + payload.encode("latin1")
        crc = zlib.crc32(chunk_data, zlib.crc32(b"tEXt")) & 0xFFFFFFFF
        scene_chunk = (
            struct.pack(">I", len(chunk_data))
            + b"tEXt"
            + chunk_data
            + struct.pack(">I", crc)
        )
        output = bytearray(PNG_SIGNATURE)
        for chunk_type, start, end in iter_chunks(png):
            if chunk_type in TEXT_CHUNKS:
                continue
            if chunk_type == b"IEND":
                output.extend(scene_chunk)
            output.extend(png[start:end])
        args.output_png.write_bytes(output)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Cannot embed scene: {error}\n")
    print(f"Wrote {args.output_png}")


if __name__ == "__main__":
    main()
