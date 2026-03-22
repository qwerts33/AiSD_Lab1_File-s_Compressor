# Task_4/final_benchmark.py
"""
Финальный бенчмарк всех компрессоров.
"""

import os
import sys
import time
from pathlib import Path

# Добавляем корневую директорию
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# Импорты всех компрессоров
from Task_1.RLE_Coding import encode as rle_encode, decode as rle_decode
from Task_2.huffman_codec import compress_to_bytes as ha_compress, decompress_from_bytes as ha_decompress
from Task_2.bwt_lf import bwt_forward_cyclic, bwt_inverse_lf
from Task_2.mtf_coding import mtf_encode, mtf_decode
from Task_3.lz77 import lz77_compress, lz77_decompress
from Task_3.lzw import lzw_compress, lzw_decompress
from Task_3.lzss_impl import lzss_compress, lzss_decompress
from Task_3.lzss_ha import lzss_ha_compress, lzss_ha_decompress
from Task_3.lzw_ha import lzw_ha_compress, lzw_ha_decompress


def bwt_rle_compress(data: bytes, block_size: int = 100000, ms: int = 8, mc: int = 8) -> bytes:
    """BWT + RLE."""
    result = bytearray()
    for i in range(0, len(data), block_size):
        block = data[i:i + block_size]
        if len(block) == 0:
            continue
        bwt, idx = bwt_forward_cyclic(block)
        result.extend(idx.to_bytes(4, 'little'))
        rle = rle_encode(bwt, ms=ms, mc=mc)
        result.extend(len(rle).to_bytes(4, 'little'))
        result.extend(rle)
    return bytes(result)


def bwt_rle_decompress(data: bytes, ms: int = 8, mc: int = 8) -> bytes:
    """Декомпрессия BWT + RLE."""
    result = bytearray()
    pos = 0
    while pos < len(data):
        if pos + 8 > len(data):
            break
        idx = int.from_bytes(data[pos:pos + 4], 'little')
        pos += 4
        block_len = int.from_bytes(data[pos:pos + 4], 'little')
        pos += 4
        if pos + block_len > len(data):
            break
        block = data[pos:pos + block_len]
        pos += block_len
        try:
            decoded = rle_decode(block, ms=ms, mc=mc)
            original = bwt_inverse_lf(decoded, idx)
            result.extend(original)
        except Exception as e:
            print(f"Ошибка декодирования блока: {e}")
            continue
    return bytes(result)


def bwt_mtf_ha_compress(data: bytes, block_size: int = 100000) -> bytes:
    """BWT + MTF + Huffman."""
    result = bytearray()
    for i in range(0, len(data), block_size):
        block = data[i:i + block_size]
        if len(block) == 0:
            continue
        bwt, idx = bwt_forward_cyclic(block)
        result.extend(idx.to_bytes(4, 'little'))
        mtf = mtf_encode(bwt)
        ha = ha_compress(mtf)
        result.extend(len(ha).to_bytes(4, 'little'))
        result.extend(ha)
    return bytes(result)


def bwt_mtf_ha_decompress(data: bytes) -> bytes:
    """Декомпрессия BWT + MTF + Huffman."""
    result = bytearray()
    pos = 0
    while pos < len(data):
        if pos + 8 > len(data):
            break
        idx = int.from_bytes(data[pos:pos + 4], 'little')
        pos += 4
        block_len = int.from_bytes(data[pos:pos + 4], 'little')
        pos += 4
        if pos + block_len > len(data):
            break
        block = data[pos:pos + block_len]
        pos += block_len
        try:
            ha = ha_decompress(block)
            mtf = mtf_decode(ha)
            original = bwt_inverse_lf(mtf, idx)
            result.extend(original)
        except Exception as e:
            print(f"Ошибка декодирования блока: {e}")
            continue
    return bytes(result)


def bwt_mtf_rle_ha_compress(data: bytes, block_size: int = 100000, ms: int = 8, mc: int = 8) -> bytes:
    """BWT + MTF + RLE + Huffman."""
    result = bytearray()
    for i in range(0, len(data), block_size):
        block = data[i:i + block_size]
        if len(block) == 0:
            continue
        bwt, idx = bwt_forward_cyclic(block)
        result.extend(idx.to_bytes(4, 'little'))
        mtf = mtf_encode(bwt)
        rle = rle_encode(mtf, ms=ms, mc=mc)
        ha = ha_compress(rle)
        result.extend(len(ha).to_bytes(4, 'little'))
        result.extend(ha)
    return bytes(result)


def bwt_mtf_rle_ha_decompress(data: bytes, ms: int = 8, mc: int = 8) -> bytes:
    """Декомпрессия BWT + MTF + RLE + Huffman."""
    result = bytearray()
    pos = 0
    while pos < len(data):
        if pos + 8 > len(data):
            break
        idx = int.from_bytes(data[pos:pos + 4], 'little')
        pos += 4
        block_len = int.from_bytes(data[pos:pos + 4], 'little')
        pos += 4
        if pos + block_len > len(data):
            break
        block = data[pos:pos + block_len]
        pos += block_len
        try:
            ha = ha_decompress(block)
            rle = rle_decode(ha, ms=ms, mc=mc)
            mtf = mtf_decode(rle)
            original = bwt_inverse_lf(mtf, idx)
            result.extend(original)
        except Exception as e:
            print(f"Ошибка декодирования блока: {e}")
            continue
    return bytes(result)


# Список всех компрессоров с их функциями
COMPRESSORS = [
    ("RLE", rle_encode, rle_decode),
    ("HA", ha_compress, ha_decompress),
    ("BWT+RLE", bwt_rle_compress, bwt_rle_decompress),
    ("BWT+MTF+HA", bwt_mtf_ha_compress, bwt_mtf_ha_decompress),
    ("BWT+MTF+RLE+HA", bwt_mtf_rle_ha_compress, bwt_mtf_rle_ha_decompress),
    ("LZ77", lz77_compress, lz77_decompress),
    ("LZSS", lzss_compress, lzss_decompress),
    ("LZW", lzw_compress, lzw_decompress),
    ("LZSS+HA", lzss_ha_compress, lzss_ha_decompress),
    ("LZW+HA", lzw_ha_compress, lzw_ha_decompress),
]


def test_compressors(data: bytes, name: str):
    """Тестирует все компрессоры на данных."""
    print(f"\n{'=' * 90}")
    print(f"Тестирование на: {name} ({len(data)} байт)")
    print(f"{'=' * 90}")
    print(f"{'Компрессор':<20} {'Сжатый':>12} {'Коэф.':>10} {'Время сж.':>10} {'Время рас.':>10} {'Статус':>10}")
    print("-" * 90)

    results = []

    for comp_name, compress_func, decompress_func in COMPRESSORS:
        try:
            # Сжатие
            start = time.time()
            compressed = compress_func(data)
            compress_time = time.time() - start

            # Декомпрессия
            start = time.time()
            decompressed = decompress_func(compressed)
            decompress_time = time.time() - start

            ratio = len(compressed) / len(data) if data else 0
            status = "OK" if decompressed == data else "ОШИБКА"

            print(
                f"{comp_name:<20} {len(compressed):>12} {ratio:>10.4f} {compress_time:>10.3f} {decompress_time:>10.3f} {status:>10}")
            results.append((comp_name, len(compressed), ratio, compress_time, decompress_time, status))

        except Exception as e:
            print(f"{comp_name:<20} {'ОШИБКА':>12} {'':>10} {'':>10} {'':>10} {str(e)[:30]:>10}")
            results.append((comp_name, 0, 0, 0, 0, f"ERROR: {str(e)[:20]}"))

    return results


def main():
    """Главная функция."""
    base_path = "/Users/emmat/Documents/учеба/аисд_1/"

    test_files = [
        ("karamazov.txt", 100000, "Текст (русский)"),
        ("enwik9.txt", 200000, "enwik9"),
        ("wnb.raw", None, "Ч/Б изображение"),
        ("gray.raw", None, "Оттенки серого"),
        ("multi_color.raw", None, "Цветное изображение"),
        ("/bin/ls", 100000, "Бинарный файл"),
    ]

    all_results = {}

    for filename, limit, description in test_files:
        if filename.startswith("/"):
            file_path = filename
        else:
            file_path = os.path.join(base_path, filename)

        if not os.path.exists(file_path):
            print(f"Файл не найден: {file_path}")
            continue

        with open(file_path, 'rb') as f:
            data = f.read()

        if limit and len(data) > limit:
            data = data[:limit]
            print(f"Используем первые {limit} байт из {filename}")

        results = test_compressors(data, f"{description} ({filename})")
        all_results[filename] = results

    # Сохраняем результаты в файл
    with open("benchmark_results.txt", "w") as f:
        f.write("Результаты бенчмарка компрессоров\n")
        f.write("=" * 80 + "\n\n")

        for filename, results in all_results.items():
            f.write(f"\n{filename}:\n")
            f.write("-" * 80 + "\n")
            f.write(
                f"{'Компрессор':<20} {'Сжатый':>12} {'Коэф.':>10} {'Время сж.':>10} {'Время рас.':>10} {'Статус':>10}\n")
            f.write("-" * 80 + "\n")
            for comp_name, size, ratio, ct, dt, status in results:
                f.write(f"{comp_name:<20} {size:>12} {ratio:>10.4f} {ct:>10.3f} {dt:>10.3f} {status:>10}\n")

    print("\n" + "=" * 90)
    print("Результаты сохранены в benchmark_results.txt")
    print("=" * 90)


if __name__ == "__main__":
    main()