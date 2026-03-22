import os
from RLE_Coding import encode, decode
base_path = "/Users/emmat/Documents/учеба/аисд_1/"
files = [
    ("karamazov.txt", 8),
    ("wnb.raw", 8),
    ("gray.raw", 8),
    ("multi_color.raw", 24),
    ("enwik9.txt", 8),
    ("/bin/ls", 8)
]
print(f"{'Файл':30} {'Исх.размер':>12} {'RLE размер':>12} {'Коэф. сжатия':>15} {'Статус':>10}")
print("-"*85)
def check():
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
            if filename!="enwik9.txt":
                data = f.read()
            else:
                data = f.read(10_000_000)

        encoded = encode(data, ms=ms, mc=8)
        decoded = decode(encoded, ms=ms, mc=8)

        status = "OK" if decoded == data else "Ошибка"
        original_size = len(data)
        encoded_size = len(encoded)
        ratio = encoded_size / original_size

        print(f"{filename:30} {original_size:12} {encoded_size:12} {ratio:15.2f} {status:>10}")
if __name__ == "__main__":
    check()