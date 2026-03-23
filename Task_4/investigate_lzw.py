import matplotlib.pyplot as plt
from Task_3.lzw import lzw_compress


def investigate_lzw_dict(data: bytes):
    """Исследует зависимость от размера словаря."""
    dict_sizes = [256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]
    ratios = []
    sizes = []

    print(f"Исследование LZW на {len(data)} байт")
    print("-" * 60)
    print(f"{'Dict size':>12} {'Compressed':>12} {'Ratio':>10}")
    print("-" * 60)

    for d in dict_sizes:
        try:
            compressed = lzw_compress(data, max_dict=d)
            size = len(compressed)
            ratio = size / len(data)
            ratios.append(ratio)
            sizes.append(size)
            print(f"{d:>12} {size:>12} {ratio:>10.4f}")
        except MemoryError:
            print(f"{d:>12} {'MEM ERROR':>12} {'':>10}")
            ratios.append(1.0)
            sizes.append(len(data))

    # График
    plt.figure(figsize=(10, 6))
    plt.plot(dict_sizes, ratios, 'o-', linewidth=2, markersize=8)
    plt.xscale('log')
    plt.xlabel('Размер словаря (max_dict)')
    plt.ylabel('Коэффициент сжатия')
    plt.title('Зависимость коэффициента сжатия LZW от размера словаря')
    plt.grid(True, alpha=0.3)
    plt.axhline(y=1.0, color='r', linestyle='--', alpha=0.5)

    # Находим оптимальный
    min_ratio = min([r for r in ratios if r < 1.0])
    best_idx = ratios.index(min_ratio)
    best_dict = dict_sizes[best_idx]
    plt.scatter([best_dict], [min_ratio], color='red', s=100, zorder=5)
    plt.annotate(f'Оптимум: {best_dict} ({min_ratio:.4f})',
                 xy=(best_dict, min_ratio),
                 xytext=(best_dict * 1.5, min_ratio + 0.05),
                 arrowprops=dict(arrowstyle='->'))

    plt.tight_layout()
    plt.savefig('lzw_dict_investigation.png', dpi=150)
    plt.show()

    return dict_sizes, ratios


if __name__ == "__main__":
    test_file = "/Users/emmat/Documents/учеба/аисд_1/karamazov.txt"

    try:
        with open(test_file, 'rb') as f:
            data = f.read(200000)
        print(f"Загружено {len(data)} байт из {test_file}")
        investigate_lzw_dict(data)
    except FileNotFoundError:
        print("Файл не найден, использую синтетические данные")
        synthetic = b"abc" * 50000 + b"def" * 50000 + b"ghi" * 50000
        investigate_lzw_dict(synthetic)