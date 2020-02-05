from typing import Dict, Iterator
import itertools


def generator_to_dict(dic: Dict) -> Dict:
    return {"items": list(divide_key_value(dic))}


def divide_key_value(dic: Dict) -> Dict:
    for k, v in dic.items():
        if isinstance(v, dict):
            items = generator_to_dict(v)
            yield {'description': k, 'quantityText': None}
            yield items
        else:
            yield {'description': k, 'quantityText': v}


def parse_ingredients(data):
    key_value_list = [{k: v} for k, v in data.items()]
    generator = [list(divide_key_value(d)) for d in key_value_list]
    
    return list(itertools.chain.from_iterable(generator))
