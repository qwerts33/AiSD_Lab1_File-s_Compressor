import matplotlib.pyplot as plt
from Task_3.bwt_lf import bwt_forward_cyclic
from Task_2.entropy import entropy
from Task_2.mtf_coding import mtf_encode

def investigate_bwt_block_entropy(data: bytes, use_mtf: bool = True):
    """Исследует энтропию после BWT+MTF для разных блоков."""
    block_sizes = [1000, 5000, 10000, 50000, 100000, 500000, 1000000]
    block_sizes = [b for b in block_sizes if b <= len(data)]

    entropies = []

    print(f"Исследование BWT на {len(data)} байт")
    print("-" * 60)
    print(f"{'Block size':>12} {'Entropy after BWT':>18} {'Entropy after BWT+MTF':>22}")
    print("-" * 60)

    for bs in block_sizes:
        bwt_parts = []
        mtf_parts = []

        for i in range(0, len(data), bs):
            block = data[i:i + bs]
            if len(block) == 0:
                continue
            bwt, _ = bwt_forward_cyclic(block)
            bwt_parts.append(bwt)
            mtf_parts.append(mtf_encode(bwt))

        bwt_combined = b''.join(bwt_parts)
        mtf_combined = b''.join(mtf_parts)

        ent_bwt = entropy(bwt_combined, ms=8)
        ent_mtf = entropy(mtf_combined, ms=8)
        entropies.append((ent_bwt, ent_mtf))

        print(f"{bs:>12} {ent_bwt:>18.4f} {ent_mtf:>22.4f}")

    # График
    plt.figure(figsize=(12, 6))
    plt.plot(block_sizes, [e[0] for e in entropies], 'o-', label='После BWT', linewidth=2)
    plt.plot(block_sizes, [e[1] for e in entropies], 's--', label='После BWT+MTF', linewidth=2)
    plt.xscale('log')
    plt.xlabel('Размер блока (байт)')
    plt.ylabel('Энтропия (бит/байт)')
    plt.title('Зависимость энтропии от размера блока BWT')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('bwt_block_entropy.png', dpi=150)
    plt.show()

    return block_sizes, entropies


if __name__ == "__main__":
    test_file = "/Users/emmat/Documents/учеба/аисд_1/karamazov.txt"

    try:
        with open(test_file, 'rb') as f:
            data = f.read(2000000)  # 2MB для нормального исследования
        print(f"Загружено {len(data)} байт из {test_file}")
        investigate_bwt_block_entropy(data)
    except FileNotFoundError:
        print("Файл не найден, использую синтетические данные")
        synthetic = b"abc" * 100000 + b"def" * 100000 + b"ghi" * 100000
        investigate_bwt_block_entropy(synthetic)