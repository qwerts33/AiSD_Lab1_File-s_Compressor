import heapq
import struct
from collections import Counter
from pathlib import Path
from typing import Any

MAGIC = b"HUF1"

class _Node:
    __slots__ = ("sym", "freq", "left", "right")

    def __init__(self, sym: int | None = None, freq: int = 0) -> None:
        self.sym = sym
        self.freq = freq
        self.left: _Node | None = None
        self.right: _Node | None = None

    def __lt__(self, other: Any) -> bool:
        return self.freq < other.freq


def _build_tree(freq: Counter[int]) -> _Node | None:
    if not freq:
        return None
    heap: list[tuple[int, int, _Node]] = []
    seq = 0
    for b in sorted(freq.keys()):
        n = _Node(b, freq[b])
        heapq.heappush(heap, (n.freq, seq, n))
        seq += 1
    if len(heap) == 1:
        _, _, n = heap[0]
        root = _Node()
        root.freq = n.freq
        root.left = n
        return root
    while len(heap) > 1:
        f1, s1, a = heapq.heappop(heap)
        f2, s2, b = heapq.heappop(heap)
        p = _Node()
        p.freq = f1 + f2
        p.left = a
        p.right = b
        heapq.heappush(heap, (p.freq, seq, p))
        seq += 1
    _, _, root = heap[0]
    return root

def _build_codes(node: _Node | None, prefix: str, out: dict[int, str]) -> None:
    if node is None:
        return
    if node.sym is not None:
        out[node.sym] = prefix if prefix else "0"
        return
    if node.left:
        _build_codes(node.left, prefix + "0", out)
    if node.right:
        _build_codes(node.right, prefix + "1", out)

def build_huffman_codes(data: bytes) -> tuple[_Node | None, dict[int, str]]:
    freq = Counter(data)
    root = _build_tree(freq)
    codes: dict[int, str] = {}
    if root:
        _build_codes(root, "", codes)
    return root, codes

def bits_to_bytes(bits: str) -> tuple[bytes, int]:
    pad = (-len(bits)) % 8
    padded = bits + "0" * pad
    out = bytearray()
    for i in range(0, len(padded), 8):
        out.append(int(padded[i : i + 8], 2))
    return bytes(out), pad

def bytes_to_bits(blob: bytes, total_bits: int) -> str:
    bits: list[str] = []
    for b in blob:
        for k in range(7, -1, -1):
            if len(bits) >= total_bits:
                break
            bits.append("1" if (b >> k) & 1 else "0")
    return "".join(bits)

def huffman_encode_stream(data: bytes) -> tuple[bytes, int, int, dict[int, str]]:
    _, codes = build_huffman_codes(data)
    bits = "".join(codes[b] for b in data)
    total_bits = len(bits)
    payload, pad = bits_to_bytes(bits)
    return payload, total_bits, pad, codes

def huffman_decode_stream(payload: bytes, total_bits: int, orig_len: int, freq: Counter[int]) -> bytes:
    root = _build_tree(freq)
    if root is None or orig_len == 0:
        return b""
    bits = bytes_to_bits(payload, total_bits)
    out = bytearray()
    node = root
    for bit in bits:
        node = node.left if bit == "0" else node.right  # type: ignore
        if node is None:
            raise ValueError("Ошибка декодирования")
        if node.sym is not None:
            out.append(node.sym)
            if len(out) >= orig_len:
                break
            node = root
    if len(out) != orig_len:
        raise ValueError("Длина не совпадает")
    return bytes(out)

def compress_to_bytes(data: bytes) -> bytes:
    freq = Counter(data)
    if not data:
        return struct.pack("<QIBH", 0, 0, 0, 0)
    payload, total_bits, pad, _ = huffman_encode_stream(data)
    syms = sorted(freq.keys())
    buf = bytearray()
    buf += struct.pack("<QIBH", len(data), total_bits, pad, len(syms))
    for s in syms:
        buf += struct.pack("<BI", s, freq[s])
    buf += struct.pack("<I", len(payload))
    buf += payload
    return bytes(buf)

def decompress_from_bytes(blob: bytes) -> bytes:
    if len(blob) < 8 + 4 + 1 + 2:
        raise ValueError("Короткий заголовок")
    orig_len, total_bits, pad, n_syms = struct.unpack_from("<QIBH", blob, 0)
    off = 8 + 4 + 1 + 2
    if orig_len == 0:
        return b""
    freq: Counter[int] = Counter()
    for _ in range(n_syms):
        s, f = struct.unpack_from("<BI", blob, off)
        off += 5
        freq[s] = f
    pay_len, = struct.unpack_from("<I", blob, off)
    off += 4
    payload = blob[off : off + pay_len]
    return huffman_decode_stream(payload, total_bits, orig_len, freq)

def write_huffman_file(data: bytes, path: str | Path) -> None:
    Path(path).write_bytes(MAGIC + compress_to_bytes(data))

def read_huffman_file(path: str | Path) -> bytes:
    raw = Path(path).read_bytes()
    if len(raw) < 4 or raw[:4] != MAGIC:
        raise ValueError("Неверная сигнатура HUF1")
    return decompress_from_bytes(raw[4:])

def roundtrip(data: bytes) -> bool:
    return decompress_from_bytes(compress_to_bytes(data)) == data
