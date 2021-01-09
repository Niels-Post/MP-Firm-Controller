def is_unsigned_compatible(val: int, bits: int) -> bool:
    return 0 <= int(val) <= pow(2, bits)


def is_bool_compatible(val: int):
    return is_unsigned_compatible(val, 2)
