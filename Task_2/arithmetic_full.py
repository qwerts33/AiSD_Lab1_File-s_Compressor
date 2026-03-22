# arithmetic_full.py
"""
Полноценное арифметическое кодирование/декодирование.
"""


class ArithmeticEncoder:
    def __init__(self, model):
        self.model = model  # кумулятивные вероятности
        self.low = 0.0
        self.high = 1.0
        self.output = []

    def encode_symbol(self, symbol):
        r = self.high - self.low
        self.low += r * self.model[symbol]
        self.high = self.low + r * (self.model[symbol + 1] - self.model[symbol])

        # Нормализация (простейший вариант — без масштабирования)

    def encode(self, data):
        for b in data:
            self.encode_symbol(b)
        # Возвращаем среднюю точку
        return (self.low + self.high) / 2


class ArithmeticDecoder:
    def __init__(self, model, value):
        self.model = model
        self.value = value
        self.low = 0.0
        self.high = 1.0

    def decode_symbol(self):
        r = self.high - self.low
        # Находим символ
        for i in range(256):
            if self.low + r * self.model[i] <= self.value < self.low + r * self.model[i + 1]:
                symbol = i
                break

        # Обновляем интервал
        self.low += r * self.model[symbol]
        self.high = self.low + r * (self.model[symbol + 1] - self.model[symbol])
        return symbol

    def decode(self, length):
        result = []
        for _ in range(length):
            result.append(self.decode_symbol())
        return bytes(result)


def build_model(data: bytes) -> list:
    """Строит кумулятивную вероятностную модель."""
    from collections import Counter
    freq = Counter(data)
    total = len(data)
    cum = [0.0] * 257
    s = 0.0
    for i in range(256):
        s += freq.get(i, 0) / total
        cum[i + 1] = s
    return cum


def arithmetic_encode(data: bytes) -> float:
    """Кодирует данные в число с плавающей точкой."""
    model = build_model(data)
    encoder = ArithmeticEncoder(model)
    return encoder.encode(data)


def arithmetic_decode(value: float, length: int, model: list) -> bytes:
    """Декодирует из числа."""
    decoder = ArithmeticDecoder(model, value)
    return decoder.decode(length)


# Тест
if __name__ == "__main__":
    test = b"hello world"
    model = build_model(test)
    encoded = arithmetic_encode(test)
    decoded = arithmetic_decode(encoded, len(test), model)
    print(f"Original: {test}")
    print(f"Encoded: {encoded}")
    print(f"Decoded: {decoded}")
    print(f"OK: {decoded == test}")