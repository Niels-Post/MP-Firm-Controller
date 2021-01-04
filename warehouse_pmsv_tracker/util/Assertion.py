from typing import Any


def is_unsigned_compatible(val: Any, bits: int) -> bool:
    return 0 <= int(val) <= pow(2, bits)


def is_bool_compatible(val: Any):
    return is_unsigned_compatible(val, 2)
