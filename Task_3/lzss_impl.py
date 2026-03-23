# Task_3/lzss_impl.py
"""
LZSS — улучшенная версия LZ77 с разделением на литералы и копии.
"""

import struct


def lzss_compress(data: bytes, window: int = 4096, lookahead: int = 18, min_match: int = 3) -> bytes:
    """
    LZSS сжатие.
    Формат токенов:
    - 0: литерал (1 байт)
    - 1: копия (offset 2 байта, length 2 байта)
    """
    if not data:
        return struct.pack("<I", window)

    out = bytearray(struct.pack("<I", window))
    i = 0
    n = len(data)

    while i < n:
        best_len = 0
        best_off = 0
        start = max(0, i - window)

        # Ищем лучшее совпадение
        for j in range(start, i):
            if data[j] != data[i]:
                continue

            ln = 0
            while (ln < lookahead and
                   i + ln < n and
                   data[j + (ln % (i - j))] == data[i + ln]):  # поддержка перекрывающегося копирования
                ln += 1

            if ln > best_len:
                best_len = ln
                best_off = i - j

        # LZSS: используем копию только если длина >= min_match
        if best_len >= min_match:
            out += b"\x01" + struct.pack("<HH", best_off, best_len)
            i += best_len
        else:
            out += b"\x00" + bytes([data[i]])
            i += 1

    return bytes(out)


def lzss_decompress(blob: bytes) -> bytes:
    """LZSS декомпрессия."""
    if len(blob) < 4:
        raise ValueError("Короткий заголовок")

    window, = struct.unpack_from("<I", blob, 0)
    pos = 4
    buf = bytearray()

    while pos < len(blob):
        tag = blob[pos]
        pos += 1

        if tag == 0:
            # Литерал
            if pos >= len(blob):
                break
            buf.append(blob[pos])
            pos += 1
        elif tag == 1:
            # Копия
            if pos + 4 > len(blob):
                break
            off, ln = struct.unpack_from("<HH", blob, pos)
            pos += 4
            start = len(buf) - off
            for _ in range(ln):
                buf.append(buf[start])
                start += 1
        else:
            raise ValueError(f"Неизвестный токен: {tag}")

    return bytes(buf)


def roundtrip(data: bytes, window: int = 4096, lookahead: int = 18, min_match: int = 3) -> bool:
    """Проверка обратимости LZSS."""
    compressed = lzss_compress(data, window, lookahead, min_match)
    decompressed = lzss_decompress(compressed)
    return decompressed == data


if __name__ == "__main__":
    # Тест
    test_data = b"abcabcabcabcabcabcabcabc"
    print(f"Original: {len(test_data)} bytes")

    compressed = lzss_compress(test_data, window=256, min_match=3)
    decompressed = lzss_decompress(compressed)

    print(f"Compressed: {len(compressed)} bytes")
    print(f"Ratio: {len(compressed) / len(test_data):.3f}")
    print(f"OK: {decompressed == test_data}")