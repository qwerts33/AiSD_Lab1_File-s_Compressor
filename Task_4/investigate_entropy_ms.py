"""
Задание 2, п.1: зависимость энтропии сообщения от длины кода символа (1–4 байта).

Берём английский текст (enwik7 или karamazov), фильтруем символы с кодом > 127,
исследуем энтропию при ms = 8, 16, 24, 32 бит (1–4 байта на символ).

Интерпретация результатов:
  — При ms=8 считаем энтропию по байтам (255 возможных символов).
  — При ms=16 считаем по парам байтов (65535 символов), и т.д.
  — Энтропия в битах на символ растёт с ms, но энтропия в битах на байт
    (= энтропия / (ms/8)) должна стабилизироваться, что означает, что
    источник близок к стационарному.
"""

import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

BASE_PATH = "/Users/emmat/Documents/учеба/аисд_1/"

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from Task_2.entropy import entropy


def filter_ascii(data: bytes) -> bytes:
    """Оставляет только байты < 128 (чистый ASCII)."""
    return bytes(b for b in data if b < 128)


def investigate_entropy_vs_ms(data: bytes, label: str) -> dict:
    """
    Считает энтропию при ms = 8, 16, 24, 32 бит.
    Возвращает словарь с результатами.
    """
    ms_values = [8, 16, 24, 32]
    entropies_per_symbol = []
    entropies_per_byte = []

    print(f"\n{'='*60}")
    print(f"Файл: {label}, размер: {len(data):,} байт")
    print(f"{'ms (бит)':>10}  {'Энтропия (бит/символ)':>22}  {'Энтропия (бит/байт)':>22}")
    print("-" * 58)

    for ms in ms_values:
        e_sym = entropy(data, ms)
        e_byte = e_sym / (ms / 8)
        entropies_per_symbol.append(e_sym)
        entropies_per_byte.append(e_byte)
        print(f"{ms:>10}  {e_sym:>22.4f}  {e_byte:>22.4f}")

    return {
        "label": label,
        "ms_values": ms_values,
        "per_symbol": entropies_per_symbol,
        "per_byte": entropies_per_byte,
    }


def plot_results(all_results: list[dict], output_path: str = "entropy_vs_ms.png") -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    colors = ["#2196F3", "#F44336", "#4CAF50", "#FF9800", "#9C27B0"]

    for i, res in enumerate(all_results):
        c = colors[i % len(colors)]
        ms = res["ms_values"]

        ax1.plot(ms, res["per_symbol"], "o-", color=c, linewidth=2,
                 markersize=8, label=res["label"])
        ax2.plot(ms, res["per_byte"], "o-", color=c, linewidth=2,
                 markersize=8, label=res["label"])

    ax1.set_title("Энтропия (бит на символ)")
    ax1.set_xlabel("Длина кода символа ms (бит)")
    ax1.set_ylabel("Энтропия (бит/символ)")
    ax1.set_xticks([8, 16, 24, 32])
    ax1.set_xticklabels(["8 (1 байт)", "16 (2 байт)", "24 (3 байт)", "32 (4 байт)"])
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.set_title("Энтропия (бит на байт)")
    ax2.set_xlabel("Длина кода символа ms (бит)")
    ax2.set_ylabel("Энтропия (бит/байт)")
    ax2.set_xticks([8, 16, 24, 32])
    ax2.set_xticklabels(["8 (1 байт)", "16 (2 байт)", "24 (3 байт)", "32 (4 байт)"])
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    fig.suptitle("Зависимость энтропии от длины кода символа", fontsize=13)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"\nГрафик сохранён: {output_path}")
    plt.show()


def main():
    files = [
        ("enwik9.txt",    "enwik7 (ASCII)",    10_000_000, True),
        ("karamazov.txt", "Карамазовы (ASCII)", None,       True),
    ]

    all_results = []

    for filename, label, limit, filter_ascii_flag in files:
        path = os.path.join(BASE_PATH, filename)
        if not os.path.exists(path):
            print(f"[Пропуск] Файл не найден: {path}")
            continue

        with open(path, "rb") as f:
            data = f.read(limit) if limit else f.read()

        if filter_ascii_flag:
            data = filter_ascii(data)
            print(f"После фильтрации ASCII: {len(data):,} байт")

        # Нужно выровнять данные до кратности 4 для ms=32
        max_sym_bytes = 4
        trim = len(data) - (len(data) % max_sym_bytes)
        data = data[:trim]

        result = investigate_entropy_vs_ms(data, label)
        all_results.append(result)

    if all_results:
        plot_results(all_results)

    print("\nИНТЕРПРЕТАЦИЯ:")
    print("  Если энтропия в бит/байт стабилизируется при увеличении ms —")
    print("  источник близок к стационарному (символы слабо коррелируют).")
    print("  Если растёт — есть межсимвольные зависимости, которые можно")
    print("  использовать при кодировании (контекстное моделирование, BWT).")


if __name__ == "__main__":
    main()