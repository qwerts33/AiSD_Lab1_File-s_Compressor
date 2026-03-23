"""
LZ77: сжатие/распаковка.
Формат потока: заголовок window_size (uint32 LE), затем токены:
  0x00 + byte — литерал
  0x01 + uint16 offset + uint16 length — копия из окна (offset от текущей позиции назад, length >= 1)
"""
from __future__ import annotations

import struct


def lz77_compress(data: bytes, window: int = 4096, lookahead: int = 16) -> bytes:
    if not data:
        return struct.pack("<I", window)
    out = bytearray(struct.pack("<I", window))
    i = 0
    n = len(data)
    while i < n:
        best_len = 0
        best_off = 0
        start = max(0, i - window)
        for j in range(start, i):
            if data[j] != data[i]:
                continue
            ln = 0
            while (
                ln < lookahead
                and i + ln < n
                and data[j + (ln % (i - j))] == data[i + ln]  # поддержка перекрывающегося копирования
            ):
                ln += 1
            if ln > best_len:
                best_len = ln
                best_off = i - j
        if best_len >= 3:
            out += b"\x01" + struct.pack("<HH", best_off, best_len)
            i += best_len
        else:
            out += b"\x00" + bytes([data[i]])
            i += 1
    return bytes(out)


def lz77_decompress(blob: bytes) -> bytes:
    if len(blob) < 4:
        raise ValueError("Короткий заголовок")
    window, = struct.unpack_from("<I", blob, 0)
    pos = 4
    buf = bytearray()
    while pos < len(blob):
        tag = blob[pos]
        pos += 1
        if tag == 0:
            buf.append(blob[pos])
            pos += 1
        elif tag == 1:
            off, ln = struct.unpack_from("<HH", blob, pos)
            pos += 4
            start = len(buf) - off
            for _ in range(ln):
                buf.append(buf[start])
                start += 1
        else:
            raise ValueError("Неизвестный токен")
    return bytes(buf)


def roundtrip(data: bytes) -> bool:
    return lz77_decompress(lz77_compress(data)) == data