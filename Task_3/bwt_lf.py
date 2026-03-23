"""
BWT: прямое построение последнего столбца через суффиксный массив (опционально naive),
обратное преобразование за O(n) через LF-mapping.
Массив C (число символов < c) строится сортировкой подсчётом по алфавиту 0..255.

Прямое BWT без sentinel: циклические сдвиги = суффиксы T=S+S со стартом 0..n-1;
SA считается для T, порядок строк — фильтр SA[k] < n, L[k]=T[start+n-1].
(Только SA(S) и формула L[i]=S[(SA[i]-1)%n] — неверны без разделителя.)
"""
from __future__ import annotations

import pydivsufsort


def bwt_forward_cyclic(data: bytes) -> tuple[bytes, int]:
    """BWT по циклическим сдвигам через SA строки T = S + S (длина 2n)."""
    n = len(data)
    if n == 0:
        return b"", 0
    t = data + data
    sa = pydivsufsort.divsufsort(t)
    sorted_starts = [sa[i] for i in range(len(sa)) if sa[i] < n]
    last = bytes(t[ss + n - 1] for ss in sorted_starts)
    primary_index = sorted_starts.index(0)
    return last, primary_index


def bwt_forward_naive(data: bytes) -> tuple[bytes, int]:
    """Прямое BWT через явную матрицу циклических сдвигов (для учебных малых строк)."""
    n = len(data)
    if n == 0:
        return b"", 0
    rots = [data[i:] + data[:i] for i in range(n)]
    rots.sort()
    last = bytes(r[-1] for r in rots)
    idx = rots.index(data)
    return last, idx


def _lf_mapping(last_column: bytes) -> list[int]:
    """LF[i]: позиция в отсортированном первом столбце, соответствующая строке i."""
    n = len(last_column)
    counts = [0] * 256
    for b in last_column:
        counts[b] += 1
    c = [0] * 256
    s = 0
    for b in range(256):
        c[b] = s
        s += counts[b]
    occ = [0] * 256
    lf = [0] * n
    for i, b in enumerate(last_column):
        occ[b] += 1
        lf[i] = c[b] + occ[b] - 1
    return lf


def bwt_inverse_lf(last_column: bytes, primary_index: int) -> bytes:
    """Обратное BWT за O(n) по последнему столбцу и индексу исходной строки."""
    n = len(last_column)
    if n == 0:
        return b""
    lf = _lf_mapping(last_column)
    res = bytearray(n)
    p = primary_index
    for i in range(n - 1, -1, -1):
        res[i] = last_column[p]
        p = lf[p]
    return bytes(res)


def bwt_inverse_counting_sort(last_column: bytes, primary_index: int) -> bytes:
    """
    То же обратное BWT; «сортировка подсчётом» используется при вычислении C[b]
    (число байтов в L, строго меньших b).
    """
    return bwt_inverse_lf(last_column, primary_index)