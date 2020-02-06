import re
import itertools
from typing import List, Dict, Any

import jaconv


class Multiplier:
    def __init__(self, template, params):
        self.template = template
        self.params = params
        self.queue = []

    def build(self):
        src_ingredients = self.template['ingredients']
        print('src_ingredients')
        print(src_ingredients)
        str_multi_params = [[str(i) for i in p] for p in self.params]
        print('str_multi_params')
        print(str_multi_params)
        join_strings = [''.join(i) for i in str_multi_params]
        print('join_strings')
        print(join_strings)
        self.queue = join_strings
        convert_ingredients = [list(self.dict_to_zenkaku(i)) for i in src_ingredients]
        convert_ingredients = list(itertools.chain.from_iterable(convert_ingredients))
        print('convert_ingredients')
        print(convert_ingredients)

        return convert_ingredients

    def dict_to_zenkaku(self, ingredients: Dict) -> List:
        print('self.queue')
        print(self.queue)
        print('ingredients before : ', ingredients)
        if 'items' in ingredients.keys():
            for item in ingredients['items']:
                yield from self.dict_to_zenkaku(item)
        else:
            que = self.queue.pop(0)
            print('que')
            print(que)
            ingredients['quantityText'] = self.value_to_zenkaku(que)
            print('ingredients after : ', ingredients)
            yield ingredients
        

    def value_to_zenkaku(self, value: str) -> str:
        print('value_to_zenkaku/value : ', value)
        null_pattern = re.compile(r'null')
        match = re.search(null_pattern, value)
        if match:
            return None
    
        zenkaku = jaconv.h2z(value, kana=True, digit=True, ascii=True)
        print('value_to_zenkaku/zenkaku', zenkaku)
    
        return zenkaku


# def build_mulitply_quantities(data: List, multiparams: List) -> List:
#     src_ingredients = data['ingredients']
#     print('build_mulitply_quantities/src_ingredients : ', src_ingredients)
#     str_multi_params = [[str(i) for i in p] for p in multiparams]
#     print('build_mulitply_quantities/str_multi_params : ', str_multi_params)
#     join_strings = [''.join(i) for i in str_multi_params]
#     print('build_mulitply_quantities/join_strings : ', join_strings)
#     convert_ingredients = [list(dict_to_zenkaku(i, p))
#                            for i, p in zip(src_ingredients, join_strings)]
#     print('build_mulitply_quantities/convert_ingredients : ', convert_ingredients)
    
#     return convert_ingredients


# def dict_to_zenkaku(ingredients: Dict, hankaku_param: str) -> List:
#     if 'items' in ingredients.keys():
#         for i in ingredients['items']:
            
#         yield from generator_to_zenkaku(ingredients['items'], hankaku_param)
#     else:
#         ingredients['quantityText'] = value_to_zenkaku(hankaku_param)
#         yield ingredients





# def generator_to_zenkaku(dic: Dict, hankaku_param: str) -> Dict:
#     return {"items": list(dict_to_zenkaku(dic, hankaku_param))}





