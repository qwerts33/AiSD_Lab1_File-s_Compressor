"""
LZ78: токен (индекс известной фразы, следующий байт; 0xFFFF — только индекс в конце).
Ограничение словаря max_dict.
"""
from __future__ import annotations

import struct

_SENT = 0xFFFF


def lz78_compress(data: bytes, max_dict: int = 1 << 20) -> bytes:
    d: dict[bytes, int] = {b"": 0}
    nxt = 1
    w = b""
    tokens: list[tuple[int, int]] = []
    for c in data:
        wc = w + bytes([c])
        if wc in d and d[wc] < max_dict:
            w = wc
        else:
            tokens.append((d[w], c))
            if nxt < max_dict:
                d[wc] = nxt
                nxt += 1
            w = b""
    if w:
        tokens.append((d[w], _SENT))
    out = bytearray(struct.pack("<II", max_dict, len(tokens)))
    for idx, ch in tokens:
        out += struct.pack("<IH", idx, ch)
    return bytes(out)


def lz78_decompress(blob: bytes) -> bytes:
    if len(blob) < 8:
        raise ValueError("Короткий заголовок")
    max_dict, ntok = struct.unpack_from("<II", blob, 0)
    pos = 8
    dict_list: list[bytes] = [b""]
    out = bytearray()
    for _ in range(ntok):
        idx, ch = struct.unpack_from("<IH", blob, pos)
        pos += 6
        if ch == _SENT:
            out.extend(dict_list[idx])
            continue
        phrase = dict_list[idx] + bytes([ch])
        out.extend(phrase)
        if len(dict_list) < max_dict:
            dict_list.append(phrase)
    return bytes(out)


def roundtrip(data: bytes) -> bool:
    return lz78_decompress(lz78_compress(data)) == data
