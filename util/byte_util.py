
def int_to_byte(number, byte_count):
    result = []
    bytes = number.to_bytes(byte_count, byteorder='big')
    for i in range(byte_count):
        result.append(bytes[i])

    return result


def byte_to_int(xbytes):
    return int.from_bytes(xbytes, 'big')