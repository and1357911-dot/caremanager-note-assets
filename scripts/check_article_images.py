#!/usr/bin/env python3
"""Read-only article image intake check; never uploads or publishes."""
import json
import pathlib
import re
import struct
import sys
import zlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
PATTERN = re.compile(r"OSN-[0-9]{3,}-[0-9]{8}\Z")
SIGNATURE = bytes.fromhex("89504e470d0a1a0a")

def inspect(article):
    if not PATTERN.fullmatch(article):
        raise ValueError("Invalid article ID")
    folder = ROOT / article
    expected = {f"instagram_{i:02d}.png" for i in range(1, 7)}
    actual = {p.name for p in folder.glob("*.png")} if folder.is_dir() else set()
    if actual != expected:
        raise ValueError("Exactly six article-specific PNG files required")
    results = []
    digests = set()
    import hashlib
    for i in range(1, 7):
        path = folder / f"instagram_{i:02d}.png"
        data = path.read_bytes()
        if len(data) > 8*1024*1024 or len(data) < 45 or not data.startswith(SIGNATURE):
            raise ValueError("Invalid PNG signature or file size")
        offset = 8
        dimensions = None
        complete = False
        while offset + 12 <= len(data):
            size = struct.unpack_from(">I", data, offset)[0]
            kind = data[offset+4:offset+8]
            end = offset + 12 + size
            if end > len(data):
                raise ValueError("Truncated PNG chunk")
            payload = data[offset+8:offset+8+size]
            crc = struct.unpack_from(">I", data, offset+8+size)[0]
            if zlib.crc32(kind+payload) & 0xffffffff != crc:
                raise ValueError("PNG CRC failure")
            if dimensions is None:
                if kind != b"IHDR" or size != 13:
                    raise ValueError("Missing PNG header")
                dimensions = struct.unpack_from(">II", payload)
            if kind == b"IEND":
                complete = size == 0 and end == len(data)
                break
            offset = end
        if not complete or dimensions != (1080, 1350):
            raise ValueError("Incomplete PNG or wrong dimensions")
        digest = hashlib.sha256(data).hexdigest()
        if digest in digests:
            raise ValueError("Duplicate image")
        digests.add(digest)
        results.append({"file":path.name,"sha256":digest})
    return {"article_id":article,"png_check":"PASS","visual_qc":"NOT_CHECKED",
            "publication_approved":False,"images":results}

if __name__ == "__main__":
    try:
        print(json.dumps(inspect(sys.argv[1]),ensure_ascii=False,indent=2))
    except (ValueError, OSError, IndexError) as exc:
        sys.exit("BLOCKED: "+str(exc))
