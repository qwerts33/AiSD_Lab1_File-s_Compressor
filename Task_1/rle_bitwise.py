class BitWriter:
    def __init__(self):
        self.buffer = bytearray()
        self.bit_pos = 0
        self.current_byte = 0

    def write_bits(self, value: int, bits: int):
        for i in range(bits):
            bit = (value >> (bits - 1 - i)) & 1
            self.current_byte = (self.current_byte << 1) | bit
            self.bit_pos += 1
            if self.bit_pos == 8:
                self.buffer.append(self.current_byte)
                self.current_byte = 0
                self.bit_pos = 0

    def flush(self):
        if self.bit_pos > 0:
            self.current_byte <<= (8 - self.bit_pos)
            self.buffer.append(self.current_byte)
        return bytes(self.buffer)


class BitReader:
    def __init__(self, data: bytes):
        self.data = data
        self.byte_pos = 0
        self.bit_pos = 0
        self.current_byte = 0

    def read_bits(self, bits: int) -> int:
        result = 0
        for _ in range(bits):
            if self.bit_pos == 0:
                if self.byte_pos >= len(self.data):
                    raise IndexError("Чтение за пределами данных")
                self.current_byte = self.data[self.byte_pos]
                self.byte_pos += 1
            result = (result << 1) | ((self.current_byte >> (7 - self.bit_pos)) & 1)
            self.bit_pos = (self.bit_pos + 1) % 8
        return result


def encode_rle(data: bytes, ms: int, mc: int) -> bytes:
    if ms < 1 or mc < 1:
        raise ValueError("Ms и Mc должны быть >= 1")

    # Преобразуем байты в последовательность битов
    bits = []
    for b in data:
        for i in range(7, -1, -1):
            bits.append((b >> i) & 1)

    # Группируем в символы по ms бит
    symbols = []
    for i in range(0, len(bits), ms):
        if i + ms <= len(bits):
            val = 0
            for j in range(ms):
                val = (val << 1) | bits[i + j]
            symbols.append(val)
        else:
            # Добиваем нулями последний неполный символ
            val = 0
            remaining = len(bits) - i
            for j in range(remaining):
                val = (val << 1) | bits[i + j]
            val <<= (ms - remaining)
            symbols.append(val)

    # RLE кодирование
    writer = BitWriter()
    i = 0
    n = len(symbols)
    max_count = (1 << (mc - 1)) - 1  # mc-1 бит под число

    while i < n:
        current = symbols[i]
        count = 1
        while i + count < n and symbols[i + count] == current and count < max_count:
            count += 1

        if count > 1:
            # Повтор: старший бит = 0
            writer.write_bits(0, 1)  # флаг "повтор"
            writer.write_bits(count, mc - 1)  # количество
            writer.write_bits(current, ms)  # символ
            i += count
        else:
            start = i
            i += 1
            # Смотрим, сколько уникальных символов подряд
            while i < n and (i - start) < max_count:
                if i + 1 < n and symbols[i] == symbols[i + 1]:
                    break
                i += 1
            lit_count = i - start
            writer.write_bits(1, 1)  # флаг
            writer.write_bits(lit_count, mc - 1)  # количество
            for j in range(lit_count):
                writer.write_bits(symbols[start + j], ms)

    return writer.flush()


def decode_rle(data: bytes, ms: int, mc: int, original_bit_len: int = None) -> bytes:
    reader = BitReader(data)
    symbols = []

    max_count = (1 << (mc - 1)) - 1

    while reader.byte_pos < len(reader.data) or reader.bit_pos > 0:
        try:
            is_literal = reader.read_bits(1)
            count = reader.read_bits(mc - 1)
        except IndexError:
            break
        if is_literal:
            for _ in range(count):
                sym = reader.read_bits(ms)
                symbols.append(sym)
        else:
            sym = reader.read_bits(ms)
            symbols.extend([sym] * count)
    bits = []
    for sym in symbols:
        for i in range(ms - 1, -1, -1):
            bits.append((sym >> i) & 1)

    if original_bit_len:
        bits = bits[:original_bit_len]
    result = bytearray()
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            b = 0
            for j in range(8):
                b = (b << 1) | bits[i + j]
            result.append(b)
        else:
            b = 0
            remaining = len(bits) - i
            for j in range(remaining):
                b = (b << 1) | bits[i + j]
            b <<= (8 - remaining)
            result.append(b)

    return bytes(result)


def roundtrip_rle(data: bytes, ms: int, mc: int) -> bool:
    encoded = encode_rle(data, ms, mc)
    decoded = decode_rle(encoded, ms, mc, len(data) * 8)
    return decoded == data


# Тест
if __name__ == "__main__":
    test_data = b"Hello, World! This is a test."
    print(f"Original: {len(test_data)} bytes")

    for ms, mc in [(8, 8), (7, 8), (9, 12), (16, 16)]:
        encoded = encode_rle(test_data, ms, mc)
        decoded = decode_rle(encoded, ms, mc, len(test_data) * 8)
        ok = decoded == test_data
        print(f"Ms={ms}, Mc={mc}: encoded={len(encoded)} bytes, OK={ok}")