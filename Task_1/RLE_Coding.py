"""
RLE: символ длиной Ms бит, управляющий код длиной Mc бит.
Повтор: младшие (Mc-1) бит — число повторов, старший бит управляющего поля = 0.
Литерал: старший бит = 1, остальное — число символов подряд без кодирования повтором.
Требование: Ms и Mc кратны 8, Mc >= 8.
"""
from __future__ import annotations


def _check_ms_mc(ms: int, mc: int) -> tuple[int, int]:
    if ms < 8 or ms % 8 != 0 or mc < 8 or mc % 8 != 0:
        raise ValueError("Ms и Mc должны быть >= 8 и кратны 8")
    return ms // 8, mc // 8


def _max_count(mc: int) -> int:
    """Максимум для повторов и длины литерального блока (число символов)."""
    return (1 << (mc - 1)) - 1


def pack_control(is_literal: bool, count: int, mc: int) -> bytes:
    cb = mc // 8
    mxc = _max_count(mc)
    if not 1 <= count <= mxc:
        raise ValueError(f"count должен быть в [1, {mxc}]")
    val = count & ((1 << (mc - 1)) - 1)
    if is_literal:
        val |= 1 << (mc - 1)
    return val.to_bytes(cb, "little")


def unpack_control(buf: bytes, mc: int) -> tuple[bool, int, int]:
    """Возвращает (literal, count, control_byte_len)."""
    cb = mc // 8
    val = int.from_bytes(buf[:cb], "little")
    literal = ((val >> (mc - 1)) & 1) != 0
    count = val & ((1 << (mc - 1)) - 1)
    return literal, count, cb


def encode(data: bytes, ms: int = 8, mc: int = 8) -> bytes:
    symbol_size, control_size = _check_ms_mc(ms, mc)
    if len(data) % symbol_size != 0:
        raise ValueError("Длина данных должна быть кратна размеру символа (Ms/8 байт)")
    max_count = _max_count(mc)
    result = bytearray()
    i = 0
    n = len(data)

    while i < n:
        current = data[i : i + symbol_size]
        count = 1
        while (
            i + (count + 1) * symbol_size <= n
            and data[i + count * symbol_size : i + (count + 1) * symbol_size] == current
            and count < max_count
        ):
            count += 1
        if count > 1:
            result.extend(pack_control(False, count, mc))
            result.extend(current)
            i += count * symbol_size
        else:
            start = i
            i += symbol_size
            while i < n and (i - start) // symbol_size < max_count:
                if i + symbol_size < n and data[i : i + symbol_size] == data[
                    i + symbol_size : i + 2 * symbol_size
                ]:
                    break
                i += symbol_size
            count_sym = (i - start) // symbol_size
            result.extend(pack_control(True, count_sym, mc))
            result.extend(data[start : start + count_sym * symbol_size])
    return bytes(result)


def decode(data: bytes, ms: int = 8, mc: int = 8) -> bytes:
    symbol_size, _ = _check_ms_mc(ms, mc)
    result = bytearray()
    i = 0
    n = len(data)
    cb = mc // 8

    while i < n:
        if i + cb > n:
            raise ValueError("Обрезанный управляющий код")
        literal, count, _ = unpack_control(data[i:], mc)
        i += cb
        if not literal:
            if i + symbol_size > n:
                raise ValueError("Обрезанный символ")
            symbol = data[i : i + symbol_size]
            i += symbol_size
            result.extend(symbol * count)
        else:
            length = count * symbol_size
            if i + length > n:
                raise ValueError("Обрезанный литеральный блок")
            result.extend(data[i : i + length])
            i += length
    return bytes(result)
