import sys
from PIL import Image
import struct
import os


def image_to_raw(input_path, output_path, image_type):
    img = Image.open(input_path)
    width, height = img.size

    if image_type == "bw":
        img = img.convert("1")
        mode = 0
        bytes_per_pixel = 1

        data = bytearray()
        for y in range(height):
            for x in range(width):
                pixel = img.getpixel((x, y))
                data.append(0 if pixel == 0 else 1)

    elif image_type == "gray":
        img = img.convert("L")
        mode = 1
        bytes_per_pixel = 1

        data = img.tobytes()

    else:
        img = img.convert("RGB")
        mode = 2
        bytes_per_pixel = 3

        data = img.tobytes()

    with open(output_path, "wb") as f:
        f.write(struct.pack("B", mode))
        f.write(struct.pack(">I", width))
        f.write(struct.pack(">I", height))
        f.write(data)

    original_size = os.path.getsize(input_path)
    raw_size = os.path.getsize(output_path)

    print(f"\nИсходник: {input_path}")
    print(f"    Размер: {original_size} байт")
    print(f"Raw-файл: {output_path}")
    print(f"    Размер: {raw_size} байт")
    print(f"    Тип: {image_type}")
    print(f"    Разрешение: {width} x {height}")
    print(f"    Размер без метаданных: {width * height * bytes_per_pixel} байт")

    if raw_size != 0:
        print(f"    Коэффициент (RAW / PNG): {raw_size / original_size:.2f}")
        print(f"    Сжатие PNG: {original_size / raw_size:.2f}x\n")


def raw_to_image(raw_path, output_path):
    with open(raw_path, "rb") as f:  # FIX
        mode = struct.unpack("B", f.read(1))[0]
        width = struct.unpack(">I", f.read(4))[0]
        height = struct.unpack(">I", f.read(4))[0]
        data = f.read()

    if mode == 0:
        img = Image.new('1', (width, height))
        pixels = img.load()

        for y in range(height):
            for x in range(width):
                i = y * width + x
                pixels[x, y] = 255 if data[i] > 0 else 0

    elif mode == 1:
        img = Image.new('L', (width, height))
        img.frombytes(data)

    elif mode == 2:
        img = Image.new('RGB', (width, height))
        img.frombytes(data)

    img.save(output_path)
    print(f"Восстановлено изображение: {output_path}")


if __name__ == "__main__":
    base_path = '/Users/emmat/Documents/учеба/аисд_1/'

    image_to_raw(
        os.path.join(base_path, 'WnB.png'),
        os.path.join(base_path, 'wnb.raw'),
        'bw'
    )

    image_to_raw(
        os.path.join(base_path, 'gray.png'),
        os.path.join(base_path, 'gray.raw'),
        'gray'
    )

    image_to_raw(
        os.path.join(base_path, 'multi_color.png'),
        os.path.join(base_path, 'multi_color.raw'),
        'rgb'
    )

    raw_to_image(
        os.path.join(base_path, "wnb.raw"),
        os.path.join(base_path, 'wnb_from_RAW.png')
    )

    raw_to_image(
        os.path.join(base_path, "gray.raw"),
        os.path.join(base_path, 'gray_from_RAW.png')
    )

    raw_to_image(
        os.path.join(base_path, "multi_color.raw"),
        os.path.join(base_path, 'rgb_from_RAW.png')
    )

    print("\nСравнение с оригинальными файлами:")

    test_images = [
        ('WnB.png', 'wnb.raw', 'Ч/Б'),
        ('gray.png', 'gray.raw', 'Оттенки серого'),
        ('multi_color.png', 'multi_color.raw', 'Цветное')
    ]

    for png_file, raw_file, description in test_images:
        png_path = os.path.join(base_path, png_file)
        raw_path = os.path.join(base_path, raw_file)

        if os.path.exists(png_path) and os.path.exists(raw_path):
            size_png = os.path.getsize(png_path)
            size_raw = os.path.getsize(raw_path)

            print(f"\n{description}:")
            print(f"  PNG размер: {size_png} байт")
            print(f"  RAW размер: {size_raw} байт")
            print(f"  PNG сжат в: {size_raw / size_png:.2f} раз")