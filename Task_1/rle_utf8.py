def utf8_to_codepoints(data: bytes) -> list:
    text = data.decode('utf-8')
    return [ord(ch) for ch in text]


def codepoints_to_utf8(codepoints: list) -> bytes:
    chars = [chr(cp) for cp in codepoints]
    return ''.join(chars).encode('utf-8')


def encode_rle_utf8(data: bytes, ms: int, mc: int) -> bytes:
    codepoints = utf8_to_codepoints(data)
    # Преобразуем кодовые точки в байты (каждая точка занимает 1-4 байта)
    # Для простоты будем кодировать сами кодовые точки как числа
    # Сначала упакуем их в байты
    packed = bytearray()
    for cp in codepoints:
        if cp < 0x80:
            packed.append(cp)
        elif cp < 0x800:
            packed.append(0xC0 | (cp >> 6))
            packed.append(0x80 | (cp & 0x3F))
        elif cp < 0x10000:
            packed.append(0xE0 | (cp >> 12))
            packed.append(0x80 | ((cp >> 6) & 0x3F))
            packed.append(0x80 | (cp & 0x3F))
        else:
            packed.append(0xF0 | (cp >> 18))
            packed.append(0x80 | ((cp >> 12) & 0x3F))
            packed.append(0x80 | ((cp >> 6) & 0x3F))
            packed.append(0x80 | (cp & 0x3F))

    from rle_bitwise import encode_rle, decode_rle
    return encode_rle(bytes(packed), ms, mc)


def decode_rle_utf8(data: bytes, ms: int, mc: int, original_cp_count: int = None) -> bytes:
    from rle_bitwise import decode_rle
    packed = decode_rle(data, ms, mc)
    codepoints = []
    i = 0
    n = len(packed)
    while i < n:
        b = packed[i]
        if b < 0x80:
            codepoints.append(b)
            i += 1
        elif 0xC0 <= b < 0xE0:
            cp = ((b & 0x1F) << 6) | (packed[i + 1] & 0x3F)
            codepoints.append(cp)
            i += 2
        elif 0xE0 <= b < 0xF0:
            cp = ((b & 0x0F) << 12) | ((packed[i + 1] & 0x3F) << 6) | (packed[i + 2] & 0x3F)
            codepoints.append(cp)
            i += 3
        else:
            cp = ((b & 0x07) << 18) | ((packed[i + 1] & 0x3F) << 12) | \
                 ((packed[i + 2] & 0x3F) << 6) | (packed[i + 3] & 0x3F)
            codepoints.append(cp)
            i += 4

    if original_cp_count:
        codepoints = codepoints[:original_cp_count]

    # Преобразуем обратно в UTF-8
    chars = [chr(cp) for cp in codepoints]
    return ''.join(chars).encode('utf-8')


# Тест
if __name__ == "__main__":
    russian_text = "Привет, мир! Это тестовый текст на русском языке.".encode('utf-8')
    print(f"Russian text: {len(russian_text)} bytes")

    encoded = encode_rle_utf8(russian_text, 16, 8)
    decoded = decode_rle_utf8(encoded, 16, 8)
    ok = decoded == russian_text
    print(f"UTF-8 RLE: encoded={len(encoded)} bytes, OK={ok}")