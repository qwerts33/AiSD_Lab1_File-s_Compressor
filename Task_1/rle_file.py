import struct
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from Task_1.RLE_Coding import decode, encode

MAGIC = b"RLE1"


def write_rle_file(
    src_path: str | Path,
    dst_path: str | Path,
    ms: int = 8,
    mc: int = 8,
) -> None:
    data = Path(src_path).read_bytes()
    payload = encode(data, ms=ms, mc=mc)
    header = MAGIC + struct.pack("<IIQI", ms, mc, len(data), len(payload))
    Path(dst_path).write_bytes(header + payload)


def read_rle_file(path: str | Path) -> bytes:
    """Читает Ms, Mc из заголовка и декодирует полезную нагрузку."""
    raw = Path(path).read_bytes()
    if len(raw) < 24:
        raise ValueError("Слишком короткий файл")
    if raw[:4] != MAGIC:
        raise ValueError("Неверная сигнатура")
    h_ms, h_mc, orig_len, pay_len = struct.unpack_from("<IIQI", raw, 4)
    off = 24
    payload = raw[off : off + pay_len]
    if len(payload) != pay_len:
        raise ValueError("Неверная длина полезной нагрузки")
    out = decode(payload, ms=h_ms, mc=h_mc)
    if len(out) != orig_len:
        raise ValueError("Длина после декодирования не совпадает с заголовком")
    return out


def roundtrip_test(src_path: str | Path, tmp_path: str | Path, ms: int = 8, mc: int = 8) -> bool:
    src = Path(src_path).read_bytes()
    write_rle_file(src_path, tmp_path, ms=ms, mc=mc)
    dec = read_rle_file(tmp_path)
    return dec == src
