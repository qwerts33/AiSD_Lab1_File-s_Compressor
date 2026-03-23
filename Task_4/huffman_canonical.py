import heapq
import struct
from collections import Counter
from pathlib import Path
from typing import Any

MAGIC = b"HCAN"

class _Node:
    __slots__ = ("sym", "freq", "left", "right")

    def __init__(self, sym: int | None = None, freq: int = 0) -> None:
        self.sym = sym
        self.freq = freq
        self.left: "_Node | None" = None
        self.right: "_Node | None" = None

    def __lt__(self, other: Any) -> bool:
        return self.freq < other.freq

def _build_lengths(data: bytes) -> dict[int, int]:
    """Возвращает словарь {символ: длина_кода}."""
    freq = Counter(data)
    if not freq:
        return {}

    heap: list[tuple[int, int, _Node]] = []
    seq = 0
    for b in sorted(freq):
        n = _Node(b, freq[b])
        heapq.heappush(heap, (n.freq, seq, n))
        seq += 1

    if len(heap) == 1:
        _, _, n = heap[0]
        return {n.sym: 1}  # type: ignore[index]

    while len(heap) > 1:
        f1, _, a = heapq.heappop(heap)
        f2, _, b = heapq.heappop(heap)
        p = _Node()
        p.freq = f1 + f2
        p.left, p.right = a, b
        heapq.heappush(heap, (p.freq, seq, p))
        seq += 1

    _, _, root = heap[0]
    lengths: dict[int, int] = {}

    def _walk(node: _Node, depth: int) -> None:
        if node.sym is not None:
            lengths[node.sym] = depth
            return
        if node.left:
            _walk(node.left, depth + 1)
        if node.right:
            _walk(node.right, depth + 1)

    _walk(root, 0)
    return lengths

def build_canonical_codes(lengths: dict[int, int]) -> dict[int, str]:
    if not lengths:
        return {}

    sorted_syms = sorted(lengths.items(), key=lambda x: (x[1], x[0]))
    codes: dict[int, str] = {}
    code = 0
    prev_len = 0

    for sym, length in sorted_syms:
        if prev_len == 0:
            code = 0
        else:
            code = (code + 1) << (length - prev_len)
        codes[sym] = format(code, f"0{length}b")
        prev_len = length

    return codes


def canonical_codes_from_data(data: bytes) -> tuple[dict[int, int], dict[int, str]]:
    lengths = _build_lengths(data)
    codes = build_canonical_codes(lengths)
    return lengths, codes


def build_decode_table(lengths: dict[int, int]) -> dict[str, int]:
    """Строит таблицу {битовая_строка: символ} из длин."""
    codes = build_canonical_codes(lengths)
    return {v: k for k, v in codes.items()}

def _bits_to_bytes(bits: str) -> tuple[bytes, int]:
    total = len(bits)
    pad = (-total) % 8
    padded = bits + "0" * pad
    out = bytearray()
    for i in range(0, len(padded), 8):
        out.append(int(padded[i: i + 8], 2))
    return bytes(out), total


def compress(data: bytes) -> bytes:
    """Сжимает байтовую строку каноническим кодом Хаффмана."""
    if not data:
        return struct.pack("<QH", 0, 0)

    lengths, codes = canonical_codes_from_data(data)

    bits = "".join(codes[b] for b in data)
    payload, total_bits = _bits_to_bytes(bits)

    syms = sorted(lengths.items())
    buf = bytearray()
    buf += struct.pack("<QH", len(data), len(syms))
    for sym, ln in syms:
        buf += struct.pack("<BB", sym, ln)
    buf += struct.pack("<Q", total_bits)
    buf += struct.pack("<I", len(payload))
    buf += payload
    return bytes(buf)


def decompress(blob: bytes) -> bytes:
    """Распаковывает данные, сжатые canonical compress()."""
    orig_len, n_syms = struct.unpack_from("<QH", blob, 0)
    off = 10
    if orig_len == 0:
        return b""

    lengths: dict[int, int] = {}
    for _ in range(n_syms):
        sym, ln = struct.unpack_from("<BB", blob, off)
        off += 2
        lengths[sym] = ln

    total_bits, pay_len = struct.unpack_from("<QI", blob, off)
    off += 12
    payload = blob[off: off + pay_len]

    decode_table = build_decode_table(lengths)

    # Разворачиваем биты
    all_bits: list[str] = []
    for byte in payload:
        for k in range(7, -1, -1):
            if len(all_bits) >= total_bits:
                break
            all_bits.append("1" if (byte >> k) & 1 else "0")

    out = bytearray()
    buf = ""
    for bit in all_bits:
        buf += bit
        if buf in decode_table:
            out.append(decode_table[buf])
            buf = ""
            if len(out) >= orig_len:
                break

    if len(out) != orig_len:
        raise ValueError(f"Длина после декодирования {len(out)} != {orig_len}")
    return bytes(out)


def write_file(data: bytes, path: str | Path) -> None:
    Path(path).write_bytes(MAGIC + compress(data))


def read_file(path: str | Path) -> bytes:
    raw = Path(path).read_bytes()
    if raw[:4] != MAGIC:
        raise ValueError("Неверная сигнатура HCAN")
    return decompress(raw[4:])


def roundtrip(data: bytes) -> bool:
    return decompress(compress(data)) == data


if __name__ == "__main__":

    tests = [
        b"hello world",
        b"aaabbbcccdddeee",
        b"abcdefghijklmnopqrstuvwxyz" * 100,
        bytes(range(256)) * 10,
        b"a",
    ]

    print(f"{'Тест':<35} {'Исх.':>8} {'Сжат.':>8} {'Коэф.':>8} {'OK':>5}")
    print("-" * 70)
    for t in tests:
        compressed = compress(t)
        decompressed = decompress(compressed)
        ok = decompressed == t
        ratio = len(compressed) / len(t) if t else 0
        label = repr(t[:20])[2:-1] + ("..." if len(t) > 20 else "")
        print(f"{label:<35} {len(t):>8} {len(compressed):>8} {ratio:>8.3f} {'✓' if ok else '✗':>5}")

    # Сравнение размера метаданных с обычным Хаффманом
    print("\n── Сравнение метаданных: обычный vs канонический Хаффман ──")
    from Task_2.huffman_codec import compress_to_bytes as huf_compress
    sample = b"abcdefghijklmnopqrstuvwxyz" * 1000
    huf_size = len(huf_compress(sample))
    can_size = len(compress(sample))
    print(f"Обычный Хаффман:     {huf_size} байт")
    print(f"Канонический:        {can_size} байт")
    print(f"Выигрыш:             {huf_size - can_size} байт")