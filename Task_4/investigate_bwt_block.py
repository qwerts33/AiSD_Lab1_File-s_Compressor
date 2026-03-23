"""
Задание 4: исследование зависимости энтропии от размера блока BWT+MTF.

Для каждого тестового файла и каждого размера блока:
  1. Разбиваем данные на блоки
  2. Применяем BWT + MTF к каждому блоку
  3. Считаем среднюю энтропию (взвешенную по длине блока)
  4. Сравниваем с исходной энтропией (без BWT+MTF)

Вывод: графики для каждого файла + общий вывод об оптимальном размере блока.
"""

import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# Настройка путей — меняй base_path под свою машину
BASE_PATH = "/Users/emmat/Documents/учеба/аисд_1/"

TEST_FILES = [
    ("karamazov.txt",   "Текст (русский)",     None),
    ("enwik9.txt",      "enwik7",              10_000_000),
    ("wnb.raw",         "Ч/Б изображение",     None),
    ("gray.raw",        "Оттенки серого",       None),
    ("multi_color.raw", "Цветное изображение",  None),
]

BLOCK_SIZES = [
    1_000,
    5_000,
    10_000,
    25_000,
    50_000,
    100_000,
    200_000,
    500_000,
    1_000_000,
]


# ── Импорты алгоритмов ────────────────────────────────────────────────────────

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from Task_2.entropy import entropy
from Task_2.mtf_coding import mtf_encode
from Task_3.bwt_lf import bwt_forward_cyclic


# ── Вычисление средневзвешенной энтропии после BWT+MTF ───────────────────────

def entropy_after_bwt_mtf(data: bytes, block_size: int, ms: int = 8) -> float:
    """
    Разбивает data на блоки block_size байт, применяет BWT+MTF к каждому,
    возвращает среднюю энтропию (взвешенную по числу символов в блоке).
    """
    total_weight = 0
    weighted_entropy = 0.0
    n = len(data)

    for i in range(0, n, block_size):
        block = data[i: i + block_size]
        if not block:
            continue
        try:
            bwt_block, _ = bwt_forward_cyclic(block)
            mtf_block = mtf_encode(bwt_block)
            e = entropy(mtf_block, ms)
        except Exception:
            e = entropy(block, ms)

        w = len(block)
        weighted_entropy += e * w
        total_weight += w

    return weighted_entropy / total_weight if total_weight else 0.0


# ── Основная функция исследования ─────────────────────────────────────────────

def investigate(data: bytes, label: str, ms: int = 8) -> dict:
    """Возвращает словарь с результатами для одного файла."""
    base_entropy = entropy(data, ms)
    print(f"\n  Базовая энтропия: {base_entropy:.4f} бит/символ")
    print(f"  {'Блок':>10}  {'Энтропия после BWT+MTF':>25}  {'Изменение':>12}")
    print("  " + "-" * 52)

    results = []
    for bs in BLOCK_SIZES:
        if bs > len(data):
            # Один блок на весь файл
            e = entropy_after_bwt_mtf(data, len(data), ms)
        else:
            e = entropy_after_bwt_mtf(data, bs, ms)
        delta = e - base_entropy
        results.append(e)
        print(f"  {bs:>10,}  {e:>25.4f}  {delta:>+12.4f}")

    return {
        "label": label,
        "base": base_entropy,
        "block_sizes": BLOCK_SIZES,
        "entropies": results,
    }


# ── Построение графиков ────────────────────────────────────────────────────────

def plot_results(all_results: list[dict], output_path: str = "bwt_mtf_block_entropy.png") -> None:
    n = len(all_results)
    cols = min(3, n)
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(6 * cols, 4 * rows))
    axes = np.array(axes).flatten() if n > 1 else [axes]

    for ax, res in zip(axes, all_results):
        sizes = res["block_sizes"]
        entropies = res["entropies"]
        base = res["base"]

        ax.semilogx(sizes, entropies, "o-", linewidth=2, markersize=7,
                    color="#2196F3", label="После BWT+MTF")
        ax.axhline(base, color="#F44336", linestyle="--", linewidth=1.5,
                   label=f"Исходная ({base:.3f})")

        # Оптимальный блок (минимальная энтропия)
        min_idx = entropies.index(min(entropies))
        ax.scatter([sizes[min_idx]], [entropies[min_idx]],
                   color="#4CAF50", s=100, zorder=5,
                   label=f"Оптимум: {sizes[min_idx]:,}")

        ax.set_title(res["label"])
        ax.set_xlabel("Размер блока (байт)")
        ax.set_ylabel("Энтропия (бит/символ)")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(min(sizes) * 0.8, max(sizes) * 1.2)

    # Скрываем лишние оси
    for ax in axes[n:]:
        ax.set_visible(False)

    fig.suptitle("Зависимость энтропии после BWT+MTF от размера блока",
                 fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"\nГрафик сохранён: {output_path}")
    plt.show()


# ── Точка входа ───────────────────────────────────────────────────────────────

def main():
    all_results = []

    for filename, label, limit in TEST_FILES:
        file_path = os.path.join(BASE_PATH, filename)
        if not os.path.exists(file_path):
            print(f"[Пропуск] Файл не найден: {file_path}")
            continue

        with open(file_path, "rb") as f:
            data = f.read(limit) if limit else f.read()

        print(f"\n{'='*60}")
        print(f"Файл: {label} ({filename}), размер: {len(data):,} байт")

        # Для цветных изображений ms=24, иначе ms=8
        ms = 24 if "color" in filename or "multi" in filename else 8
        result = investigate(data, label, ms=ms)
        all_results.append(result)

    if all_results:
        plot_results(all_results)

    # Итоговый вывод
    print("\n" + "="*60)
    print("ВЫВОД ОБ ОПТИМАЛЬНОМ РАЗМЕРЕ БЛОКА:")
    for res in all_results:
        sizes = res["block_sizes"]
        entropies = res["entropies"]
        min_idx = entropies.index(min(entropies))
        print(f"  {res['label']:<25}: оптимум при блоке {sizes[min_idx]:>10,} байт "
              f"(энтропия {entropies[min_idx]:.4f}, "
              f"базовая {res['base']:.4f})")


if __name__ == "__main__":
    main()