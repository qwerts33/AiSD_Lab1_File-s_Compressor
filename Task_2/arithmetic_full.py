class ArithmeticEncoder:
    def __init__(self, model):
        self.model = model
        self.low = 0.0
        self.high = 1.0
        self.output = []

    def encode_symbol(self, symbol):
        r = self.high - self.low
        self.low += r * self.model[symbol]
        self.high = self.low + r * (self.model[symbol + 1] - self.model[symbol])

    def encode(self, data):
        for b in data:
            self.encode_symbol(b)
        return (self.low + self.high) / 2

class ArithmeticDecoder:
    def __init__(self, model, value):
        self.model = model
        self.value = value
        self.low = 0.0
        self.high = 1.0

    def decode_symbol(self):
        r = self.high - self.low
        for i in range(256):
            if self.low + r * self.model[i] <= self.value < self.low + r * self.model[i + 1]:
                symbol = i
                break

        self.low += r * self.model[symbol]
        self.high = self.low + r * (self.model[symbol + 1] - self.model[symbol])
        return symbol

    def decode(self, length):
        result = []
        for _ in range(length):
            result.append(self.decode_symbol())
        return bytes(result)


def build_model(data: bytes) -> list:
    from collections import Counter
    freq = Counter(data)
    total = len(data)
    q = [0.0] * 257
    s = 0.0
    for i in range(256):
        s += freq.get(i, 0) / total
        q[i + 1] = s
    return q

def arithmetic_encode(data: bytes) -> float:
    model = build_model(data)
    encoder = ArithmeticEncoder(model)
    return encoder.encode(data)


def arithmetic_decode(value: float, length: int, model: list) -> bytes:
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