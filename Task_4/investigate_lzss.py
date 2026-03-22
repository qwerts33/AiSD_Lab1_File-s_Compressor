# investigate_lzss.py
"""
Исследование зависимости коэффициента сжатия LZSS от размера буфера.
"""

import matplotlib.pyplot as plt


def investigate_lzss_buffer(data: bytes, lookahead: int = 18, min_match: int = 3):
    """Исследует зависимость от размера буфера (window)."""
    from lzss_impl import lzss_compress

    windows = [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768]
    ratios = []
    sizes = []

    print(f"Исследование LZSS на {len(data)} байт")
    print("-" * 60)
    print(f"{'Window':>10} {'Compressed':>12} {'Ratio':>10}")
    print("-" * 60)

    for w in windows:
        compressed = lzss_compress(data, window=w, lookahead=lookahead, min_match=min_match)
        size = len(compressed)
        ratio = size / len(data)
        ratios.append(ratio)
        sizes.append(size)
        print(f"{w:>10} {size:>12} {ratio:>10.4f}")

    # График
    plt.figure(figsize=(10, 6))
    plt.plot(windows, ratios, 'o-', linewidth=2, markersize=8)
    plt.xscale('log')
    plt.xlabel('Размер буфера (window), байт')
    plt.ylabel('Коэффициент сжатия')
    plt.title('Зависимость коэффициента сжатия LZSS от размера буфера')
    plt.grid(True, alpha=0.3)
    plt.axhline(y=1.0, color='r', linestyle='--', alpha=0.5)

    # Находим оптимальный
    best_idx = ratios.index(min(ratios))
    best_window = windows[best_idx]
    best_ratio = ratios[best_idx]
    plt.scatter([best_window], [best_ratio], color='red', s=100, zorder=5)
    plt.annotate(f'Оптимум: {best_window} ({best_ratio:.4f})',
                 xy=(best_window, best_ratio),
                 xytext=(best_window * 1.5, best_ratio + 0.05),
                 arrowprops=dict(arrowstyle='->'))

    plt.tight_layout()
    plt.savefig('lzss_buffer_investigation.png', dpi=150)
    plt.show()

    return windows, ratios


if __name__ == "__main__":
    # Загружаем тестовые данные
    test_file = "/Users/emmat/Documents/учеба/аисд_1/karamazov.txt"

    try:
        with open(test_file, 'rb') as f:
            data = f.read(500_000)  # 500KB для быстрого теста
        print(f"Загружено {len(data)} байт из {test_file}")
        investigate_lzss_buffer(data)
    except FileNotFoundError:
        print("Файл не найден, использую синтетические данные")
        synthetic = b"abc" * 10000 + b"def" * 10000 + b"ghi" * 10000
        investigate_lzss_buffer(synthetic)