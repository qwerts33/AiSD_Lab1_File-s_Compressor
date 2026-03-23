"""
Задание 3, п.1: функция преобразования суффиксного массива в последний столбец BWT.
Задание 4, п.1: эффективное прямое BWT через суффиксный массив (pydivsufsort).

sa_to_bwt(sa, data) — принимает суффиксный массив и исходные данные,
    возвращает последний столбец матрицы BWT (байтовая строка).

Формула: L[i] = data[(sa[i] - 1) % n]
  — для каждой строки матрицы, начинающейся в позиции sa[i],
    предыдущий символ (по кругу) является символом последнего столбца.

Временная сложность: O(n) — один проход по SA.
Пространственная сложность: O(n) — хранение выходного массива.

Для SA, построенного SA-IS (pydivsufsort):
  Временная сложность построения SA: O(n)
  Пространственная сложность: O(n)
"""
from __future__ import annotations

try:
    import pydivsufsort
    _HAS_DIVSUFSORT = True
except ImportError:
    _HAS_DIVSUFSORT = False


def sa_to_bwt(sa: list[int], data: bytes) -> tuple[bytes, int]:
    """
    Преобразует суффиксный массив в последний столбец матрицы BWT.

    Входные данные:
        sa   — суффиксный массив (list[int32]), len(sa) == len(data)
        data — исходная байтовая строка

    Выходные данные:
        (last_column: bytes, primary_index: int)
        primary_index — индекс строки матрицы, соответствующей исходной строке
                        (sa[primary_index] == 0)

    Сложность: O(n) по времени и памяти.
    """
    n = len(data)
    if n == 0:
        return b"", 0

    last = bytearray(n)
    primary_index = 0

    for i, start in enumerate(sa):
        last[i] = data[(start - 1) % n]
        if start == 0:
            primary_index = i

    return bytes(last), primary_index


def bwt_via_sa(data: bytes) -> tuple[bytes, int]:
    """
    Эффективное прямое BWT через суффиксный массив SA-IS (O(n)).
    Использует pydivsufsort для построения SA.

    Сложность построения SA (SA-IS): O(n) время, O(n) память.
    Сложность sa_to_bwt: O(n) время, O(n) память.
    Итого: O(n) время, O(n) память.
    """
    if not _HAS_DIVSUFSORT:
        raise ImportError("pydivsufsort не установлен: pip install pydivsufsort")
    if len(data) == 0:
        return b"", 0

    sa = pydivsufsort.divsufsort(data)
    return sa_to_bwt(list(sa), data)


# ── Тесты ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from Task_3.bwt_lf import bwt_forward_naive, bwt_inverse_lf

    print("── Тест sa_to_bwt ──")

    # Ручной тест: строка "banana" (0x62 0x61 0x6e 0x61 0x6e 0x61)
    banana = b"banana"
    # Суффиксный массив для "banana": [5, 3, 1, 0, 4, 2]
    sa_banana = [5, 3, 1, 0, 4, 2]
    last, pi = sa_to_bwt(sa_banana, banana)
    print(f"banana: last={last}, primary_index={pi}")
    recovered = bwt_inverse_lf(last, pi)
    print(f"recovered: {recovered}, OK: {recovered == banana}")

    print()
    print("── Сравнение bwt_via_sa vs bwt_forward_naive ──")

    test_cases = [
        b"banana",
        b"abracadabra",
        b"mississippi",
        b"hello world",
        b"\xff\x00\xab\xcd" * 20,
    ]

    all_ok = True
    for tc in test_cases:
        naive_last, naive_pi = bwt_forward_naive(tc)
        fast_last, fast_pi = bwt_via_sa(tc)

        # Результат BWT не обязан совпадать побайтово (разные реализации
        # могут отличаться при одинаковых суффиксах), но обратное
        # преобразование должно давать исходную строку
        r_naive = bwt_inverse_lf(naive_last, naive_pi)
        r_fast = bwt_inverse_lf(fast_last, fast_pi)
        ok = r_naive == tc and r_fast == tc
        all_ok = all_ok and ok
        status = "✓" if ok else "✗"
        print(f"  {tc!r:<30} naive_pi={naive_pi}  fast_pi={fast_pi}  {status}")

    print(f"\nВсе тесты: {'OK' if all_ok else 'ЕСТЬ ОШИБКИ'}")

    print()
    print("── Производительность на 1МБ ──")
    import time

    big = bytes(range(256)) * 4096  # 1МБ
    t0 = time.time()
    last, pi = bwt_via_sa(big)
    t1 = time.time()
    print(f"bwt_via_sa (SA-IS):     {t1 - t0:.3f}с на {len(big)//1024}КБ")

    t0 = time.time()
    last2, pi2 = bwt_forward_naive(big[:10000])  # naive только 10КБ — иначе O(n²) долго
    t1 = time.time()
    print(f"bwt_forward_naive:      {t1 - t0:.3f}с на 10КБ (O(n²) — только для сравнения)")