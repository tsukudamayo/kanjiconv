from typing import List


def separate_quantity(strings: str, border: int) -> List:
    first = strings[:border]
    yield first
    second = strings[border:]
    has_candidate = candidate_border(second)
    if has_candidate:
        yield from separate_quantity(second, has_candidate)
    else:
        yield second
    

def candidate_border(strings: str) -> int:
    flg = strings[0].isdecimal()
    for idx, t in enumerate(strings):
        border = idx
        tmp_flg = strings[idx].isdecimal()
        if flg != tmp_flg:
            return border
            break

    return False
