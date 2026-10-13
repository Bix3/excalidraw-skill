"""Minimal PNG chunk traversal shared by the metadata CLI scripts."""

import struct


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SCENE_KEYWORD = b"application/vnd.excalidraw+json"
TEXT_CHUNKS = (b"tEXt", b"zTXt", b"iTXt")


def iter_chunks(png):
    """Yield (type, start, end) for complete chunks, including their CRC bytes."""
    if not png.startswith(PNG_SIGNATURE):
        raise ValueError("invalid PNG signature")

    offset = len(PNG_SIGNATURE)
    while offset < len(png):
        if len(png) - offset < 12:
            raise ValueError("truncated PNG chunk")
        length = struct.unpack_from(">I", png, offset)[0]
        end = offset + length + 12
        if end > len(png):
            raise ValueError("truncated PNG chunk data")
        chunk_type = png[offset + 4:offset + 8]
        if chunk_type == b"IEND":
            if length != 0:
                raise ValueError("PNG IEND chunk must be empty")
            if end != len(png):
                raise ValueError("data follows PNG IEND chunk")
        yield chunk_type, offset, end
        offset = end
        if chunk_type == b"IEND":
            return

    raise ValueError("PNG has no IEND chunk")
