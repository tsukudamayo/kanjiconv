from typing import Dict, List, Any, Iterator


def inject_dict(data: List, que: List) -> Iterator:
    for d in data:
        if len(que) == 0:
            break
        print('d : ', d)
        if isinstance(d, list):
            items = generator_indect_dict(v, que)
            yield {'description': list(d.keys())[0], 'quantityText': None}
            yield items
        else:
            q = que.pop()
            yield {'description': d['description'], 'quantityText': q}


def generator_indect_dict(data: List, que: List) -> Dict:
    return {'items': list(inject_dict(data, que))}
