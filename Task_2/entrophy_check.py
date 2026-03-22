import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from Task_2.entropy import entropy
from Task_2.mtf_coding import mtf_decode, mtf_encode
import matplotlib.pyplot as plt

base_path = "/Users/emmat/Documents/учеба/аисд_1/"

files = [
    ("karamazov.txt", 8),
    ("wnb.raw", 8),
    ("gray.raw", 8),
    ("multi_color.raw", 24),
    ("enwik9.txt", 8),
    ("/bin/ls", 8)
]

print(f"{'Файл':30} {'Энтропия':>12} {'Энтропия после MTF':>20} {'MTF восстановление':>20}")
print("-"*95)

def entr_check():
    labels = []
    ent_before_list = []
    ent_after_list = []

    for filename, ms in files:
        if filename.startswith("/"):
            file_path = filename
            display_name = filename
        else:
            file_path = os.path.join(base_path, filename)
            display_name = filename

        if not os.path.exists(file_path):
            print(f"{display_name:30} Файл не найден")
            continue

        with open(file_path, "rb") as f:
            if display_name == "enwik9.txt":
                data = f.read(10_000_000)
            else:
                data = f.read()

        if not data:
            print(f"{display_name:30} Пустой файл")
            continue
        ent_before = entropy(data, ms)

        mtf_data = mtf_encode(data)
        mtf_recovered = mtf_decode(mtf_data)
        ent_after = entropy(mtf_data, ms)
        mtf_ok = "OK" if mtf_recovered == data else "Ошибка"
        labels.append(display_name)
        ent_before_list.append(ent_before)
        ent_after_list.append(ent_after)
        print(f"{display_name:30} {ent_before:12.4f} {ent_after:20.4f} {mtf_ok:>20}")

    x = range(len(labels))
    width = 0.35

    plt.figure(figsize=(12, 6))
    plt.bar([xi - width/2 for xi in x], ent_before_list, width=width, label="До MTF")
    plt.bar([xi + width/2 for xi in x], ent_after_list, width=width, label="После MTF")
    plt.xticks(x, labels, rotation=45, ha='right')
    plt.ylabel("Энтропия (бит)")
    plt.title("Энтропия данных до и после преобразования MTF")
    plt.legend()
    plt.tight_layout()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

if __name__ == "__main__":
    entr_check()