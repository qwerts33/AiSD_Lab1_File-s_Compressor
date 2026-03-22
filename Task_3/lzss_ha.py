# Task_3/lzss_ha.py
"""
LZSS + Huffman компрессор.
"""

import struct
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from Task_2.huffman_codec import compress_to_bytes, decompress_from_bytes
from Task_3.lzss_impl import lzss_compress, lzss_decompress


def lzss_ha_compress(data: bytes, window: int = 4096, lookahead: int = 18, min_match: int = 3) -> bytes:
    """
    LZSS + Huffman сжатие.
    Формат: [window:4 байта] + [lookahead:4 байта] + [min_match:4 байта] + [Huffman-сжатые LZSS данные]
    """
    lzss_data = lzss_compress(data, window=window, lookahead=lookahead, min_match=min_match)
    ha_data = compress_to_bytes(lzss_data)

    header = struct.pack("<III", window, lookahead, min_match)
    return header + ha_data


def lzss_ha_decompress(blob: bytes) -> bytes:
    """
    LZSS + Huffman декомпрессия.
    """
    if len(blob) < 12:
        raise ValueError("Короткий заголовок")

    window, lookahead, min_match = struct.unpack_from("<III", blob, 0)
    ha_data = blob[12:]
    lzss_data = decompress_from_bytes(ha_data)
    return lzss_decompress(lzss_data)


def roundtrip(data: bytes, window: int = 4096, lookahead: int = 18, min_match: int = 3) -> bool:
    """Проверка обратимости LZSS+HA."""
    compressed = lzss_ha_compress(data, window, lookahead, min_match)
    decompressed = lzss_ha_decompress(compressed)
    return decompressed == data


if __name__ == "__main__":
    test_data = b"abcabcabcabcabcabcabcabc" * 100
    print(f"Original: {len(test_data)} bytes")

    compressed = lzss_ha_compress(test_data, window=4096)
    decompressed = lzss_ha_decompress(compressed)

    print(f"Compressed: {len(compressed)} bytes")
    print(f"Ratio: {len(compressed) / len(test_data):.3f}")
    print(f"OK: {decompressed == test_data}")