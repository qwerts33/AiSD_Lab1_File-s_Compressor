import struct
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from Task_3.lzw import lzw_compress, lzw_decompress
from Task_2.huffman_codec import compress_to_bytes, decompress_from_bytes


def lzw_ha_compress(data: bytes, max_dict: int = 4096) -> bytes:
    lzw_data = lzw_compress(data, max_dict=max_dict)
    ha_data = compress_to_bytes(lzw_data)

    header = struct.pack("<I", max_dict)
    return header + ha_data


def lzw_ha_decompress(blob: bytes) -> bytes:
    if len(blob) < 4:
        raise ValueError("Короткий заголовок")

    max_dict = struct.unpack_from("<I", blob, 0)[0]
    ha_data = blob[4:]
    lzw_data = decompress_from_bytes(ha_data)
    return lzw_decompress(lzw_data)


def roundtrip(data: bytes, max_dict: int = 4096) -> bool:
    """Проверка обратимости LZW+HA."""
    compressed = lzw_ha_compress(data, max_dict)
    decompressed = lzw_ha_decompress(compressed)
    return decompressed == data


if __name__ == "__main__":
    test_data = b"abcabcabcabcabcabcabcabc" * 100
    print(f"Original: {len(test_data)} bytes")

    compressed = lzw_ha_compress(test_data, max_dict=4096)
    decompressed = lzw_ha_decompress(compressed)

    print(f"Compressed: {len(compressed)} bytes")
    print(f"Ratio: {len(compressed) / len(test_data):.3f}")
    print(f"OK: {decompressed == test_data}")