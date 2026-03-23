"""
LZW: начальный словарь — 256 байтов; новые коды до max_dict.
Формат: uint32 max_dict, uint32 число кодов, затем uint16 коды.
Для декодирования начальный словарь восстанавливается автоматически (0..255).
"""
from __future__ import annotations

import struct


def lzw_compress(data: bytes, max_dict: int = 4096) -> bytes:
    if max_dict < 256:
        raise ValueError("max_dict должен быть >= 256")
    if max_dict > 65536:
        raise ValueError("max_dict не может превышать 65536 (коды хранятся как uint16)")
    d: dict[bytes, int] = {bytes([i]): i for i in range(256)}
    nxt = 256
    w = b""
    codes: list[int] = []
    for c in data:
        wc = w + bytes([c])
        if wc in d and d[wc] < max_dict:
            w = wc
        else:
            codes.append(d[w])
            if nxt < max_dict:
                d[wc] = nxt
                nxt += 1
            w = bytes([c])
    if w:
        codes.append(d[w])
    out = bytearray(struct.pack("<II", max_dict, len(codes)))
    for code in codes:
        out += struct.pack("<H", code & 0xFFFF)
    return bytes(out)


def lzw_decompress(blob: bytes) -> bytes:
    if len(blob) < 8:
        raise ValueError("Короткий заголовок")
    max_dict, ncodes = struct.unpack_from("<II", blob, 0)
    pos = 8
    codes = [struct.unpack_from("<H", blob, pos + i * 2)[0] for i in range(ncodes)]
    dict_list: list[bytes] = [bytes([i]) for i in range(256)]
    nxt = 256
    out = bytearray()
    if not codes:
        return b""
    prev = dict_list[codes[0]]
    out.extend(prev)
    for code in codes[1:]:
        if code < len(dict_list):
            cur = dict_list[code]
        elif code == nxt:
            cur = prev + prev[:1]
        else:
            raise ValueError("Неверный код LZW")
        out.extend(cur)
        if nxt < max_dict:
            dict_list.append(prev + cur[:1])
            nxt += 1
        prev = cur
    return bytes(out)


def roundtrip(data: bytes) -> bool:
    return lzw_decompress(lzw_compress(data)) == data