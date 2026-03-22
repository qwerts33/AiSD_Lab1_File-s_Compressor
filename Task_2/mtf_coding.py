def mtf_encode(data:bytes) ->bytes:
    table = list(range(256))
    result = []
    for byte in data:
        index = table.index(byte)
        result.append(index)
        table.pop(index)
        table.insert(0,byte)
    return bytes(result)
def mtf_decode(data:bytes)->bytes:
    table = list(range(256))
    result = []
    for index in data:
        value = table[index]
        result.append(value)
        table.pop(index)
        table.insert(0,value)
    return bytes(result)
