import math
from collections import Counter


def entropy(data: bytes, ms=8) -> float:
    symbol_size = ms // 8
    symbols = [data[i:i+symbol_size] for i in range(0, len(data), symbol_size)]
    total = len(symbols)
    freq = Counter(symbols)
    entropy = 0
    for count in freq.values():
        p = count / total
        entropy+= -p * math.log(p, 2)
    return entropy
