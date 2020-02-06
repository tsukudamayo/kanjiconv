import re
import subprocess
import itertools
from typing import Dict, List, Any
from fractions import Fraction

import jaconv


_KBM_MODEL = 'kytea-0.4.7/model/jp-0.4.7-1.mod'
_KNM_MODEL = 'kytea-0.4.7/RecipeNE-sample/recipe416.knm'
_KYTEA_PATH = 'kytea'


# ---------------- #
# parse ingredints #
# ---------------- #
def parse_ingredients(data: Dict) -> List:
    key_value_list = [{k: v} for k, v in data.items()]
    generator = [list(divide_key_value(d)) for d in key_value_list]
    
    return list(itertools.chain.from_iterable(generator))


def divide_key_value(dic: Dict) -> Dict:
    for k, v in dic.items():
        if isinstance(v, dict):
            items = generator_to_dict(v)
            yield {'description': k, 'quantityText': None}
            yield items
        else:
            yield {'description': k, 'quantityText': v}



def generator_to_dict(dic: Dict) -> Dict:
    return {"items": list(divide_key_value(dic))}


# --------- #
# normalize #
# --------- #
# TODO pytest
def normalize_quantity(data: List, divison: Any) -> List:
    ingredients = data['ingredients']
    print('ingredients')
    print(ingredients)
    hankaku_ingredients = [list(dict_to_hankaku(i)) for i in ingredients]
    hankaku_ingredients = list(itertools.chain.from_iterable(hankaku_ingredients))
    print('normalize_quantitty/hankaku_ingredients')
    print(hankaku_ingredients)
    quantity_text = [list(aggregate_quantities(i)) for i in hankaku_ingredients]
    quantity_text = list(itertools.chain.from_iterable(quantity_text))
    print('normalize_quantitty/quantity_text')
    print(quantity_text)
    candidate_borders = [candidate_border(q) for q in quantity_text]
    print('normalize_quantitty/candidate_borders')
    print(candidate_borders)
    separate_quantities = [list(separate_quantity(q, b)) for q, b in zip(quantity_text, candidate_borders)]
    print('normalize_quantitty/separate_quantities')
    print(separate_quantities)
    quantity_types = [[define_input_type(w) for w in s] for s in separate_quantities]
    norm_quantities = [[operation_by_type(t, w, divison) for t, w in zip(types, words)]
                       for types, words in zip(quantity_types, separate_quantities)]
    print('normalize_quantitty/separate_quantities')
    print(separate_quantities)
    print('normalize_quantitty/quantity_types')
    print(quantity_types)
    print('normalize_quantitty/norm_quantities')
    print(norm_quantities)
    
    return norm_quantities


# ---------------- #
# parse ingredints #
# ---------------- #
def parse_ingredients(data: Dict) -> List:
    key_value_list = [{k: v} for k, v in data.items()]
    generator = [list(divide_key_value(d)) for d in key_value_list]
    
    return list(itertools.chain.from_iterable(generator))


def divide_key_value(dic: Dict) -> Dict:
    for k, v in dic.items():
        if isinstance(v, dict):
            items = generator_to_dict(v)
            yield {'description': k, 'quantityText': None}
            yield items
        else:
            yield {'description': k, 'quantityText': v}



def generator_to_dict(dic: Dict) -> Dict:
    return {"items": list(divide_key_value(dic))}


# -------- #
# multiply #
# -------- #
class Multiplier:
    def __init__(self, template, params):
        self.template = template
        self.params = params
        self.queue = []

    def build(self):
        src_ingredients = self.template['ingredients']
        print('src_ingredients')
        print(src_ingredients)
        print('params')
        print(self.params)
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
            print('dict_to_zenkaku/items')
            print(ingredients)
            items = generator_to_dict(ingredients)
            yield {'description': list(ingredients.keys())[0], 'quantityText': None}
            yield items
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

# TODO merge normalize_quantity
def multiply_quantity(data: List, params: List, multiplier: Any) -> List:
    ingredients = data['ingredients']
    hankaku_ingredients = [list(dict_to_hankaku(i)) for i in ingredients]
    hankaku_ingredients = list(itertools.chain.from_iterable(hankaku_ingredients))
    quantity_text = [list(aggregate_quantities(i)) for i in hankaku_ingredients]
    quantity_text = list(itertools.chain.from_iterable(quantity_text))
    candidate_borders = [candidate_border(q) for q in quantity_text]
    separate_quantities = [list(separate_quantity(q, b)) for q, b in zip(quantity_text, candidate_borders)]
    quantity_types = [[define_input_type(w) for w in s] for s in separate_quantities]

    output_types = [define_output_type(words) for words in quantity_types]
    multiply_quantities = [[operation_by_output_type(q, t, w, multiplier)
                            for t, w in zip(types, words)]
                           for q, types, words in zip(output_types, quantity_types, params)]

    print('multiply_quantities/multiply_quantities : ', multiply_quantities)
    
    # return separate_quantities, quantity_types, output_types, params
    return multiply_quantities


# def build_mulitply_quantities(data: List, multiparams: List) -> List:
#     src_ingredients = data['ingredients']
#     print('build_mulitply_quantities/src_ingredients : ', src_ingredients)
#     str_multi_params = [[str(i) for i in p] for p in multiparams]
#     print('build_mulitply_quantities/str_multi_params : ', str_multi_params)
#     join_strings = [''.join(i) for i in str_multi_params]
#     print('build_mulitply_quantities/join_strings : ', join_strings)
#     convert_ingredients = [dict_to_zenkaku(i, p)
#                            for i, p in zip(src_ingredients, join_strings)]
#     print('build_mulitply_quantities/convert_ingredients : ', convert_ingredients)
    
#     return convert_ingredients


def operation_by_type(types: str, strings: str, division: Any) -> Any:
    print('operation_by_type : types - strings ', types, strings)
    if types == 'real':
        return float(strings) / division
    elif types == 'fraction':
        return Fraction(strings) / division
    else:
        return strings

    
def define_input_type(strings: str) -> str:
    pattern = re.compile('[()]')
    match = re.search(pattern, strings)
    if strings == '':
        return 'null'
    elif strings.isalpha() or match:
        return 'strings'
    else:
        if strings.find('/') >= 0:
            return 'fraction'
        else:
            return 'real'


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
    if strings == '':
        return False
    else:
        # fraction_pattern = re.compile('[0-9]{1,}/[0-9]{1,}')  # Fractions are treated as exceptions.
        # match = re.match(fraction_pattern, strings)
        flg = strings[0].isdecimal()
        tmp_flg = strings[0].isdecimal()
        change_flg = False

        for idx, t in enumerate(strings):
            border = idx
            tmp_flg = strings[idx].isdecimal()
            # if match:
            #     continue
            if t == '/':
                continue
            if flg != tmp_flg:
                change_flg = True
                return border
                break


def aggregate_quantities(dic: Dict) -> str:
    if 'items' in dic.keys():
        for d in dic['items']:
            yield from aggregate_quantities(d)
    else:
        if dic['quantityText'] is None:
            quantity_text = ''
        else:
            quantity_text = dic['quantityText']
        yield quantity_text


# def dict_to_hankaku(zenkaku_dict: Dict) -> Dict:
#     print('dict_to_hankaku/hankaku_dict')
#     print(zenkaku_dict)
#     if isinstance(zenkaku_dict, dict):
#         print('dict_to_hankaku/isinstace_dict')
#         if 'items' in zenkaku_dict.keys():
#             for d in zenkaku_dict['items']:
#                 yield from dict_to_hankaku(zenkaku_dict['items'])
#         else:
#             yield {k: value_to_hankaku(v) for k, v in zenkaku_dict.items()}
#     elif isinstance(zenkaku_dict, list):
#         print('dict_to_hankaku/isinstance_list')
#         print(zenkaku_dict)
#         for d in zenkaku_dict:
#             yield from dict_to_hankaku(d)


def dict_to_hankaku(zenkaku_dict: Dict) -> Dict:
    print('zenkaku_dict')
    print(zenkaku_dict)
    if 'items' in zenkaku_dict:
        for d in zenkaku_dict['items']:
            print({k: value_to_hankaku(v) for k, v in d.items()})
            yield {k: value_to_hankaku(v) for k, v in d.items()}
    else:
        print({k: value_to_hankaku(v) for k, v in zenkaku_dict.items()})
        yield {k: value_to_hankaku(v) for k, v in zenkaku_dict.items()}


def generator_to_hankaku(dic: Dict) -> Dict:
    return {"items": list(dict_to_hankaku(dic))}

# def dict_to_zenkaku(ingredients: Dict, hankaku_param: str) -> List:
#     ingredients['quantityText'] = value_to_zenkaku(hankaku_param)

#     return ingredients
            

def value_to_hankaku(value: Any) -> Any:
    if isinstance(value, str):
        hankaku = jaconv.z2h(value, kana=False, digit=True, ascii=True)
        return hankaku
    else:
        return value


# def value_to_zenkaku(value: str) -> str:
#     null_pattern = re.compile(r'null')
#     match = re.search(null_pattern, value)
#     if match:
#         return None

#     zenkaku = jaconv.h2z(value, kana=True, digit=True, ascii=True)

#     return zenkaku


def define_output_type(words: List) -> str:
    null_check = [w == 'null' for w in words]
    if all(null_check):
        return 'null'
    if words[0] == 'strings':
        return 'fraction'
    else:
        return 'real'


def operation_by_output_type(quantity_type: str, word_type:str, strings: str,  multiplier: Any) -> List:
    if quantity_type == 'fraction':
        if word_type == 'strings':
            return strings
        else:
            return Fraction(strings) * multiplier
    elif quantity_type == 'real':
        if word_type == 'strings':
            return strings
        else:
            return float(strings) * multiplier
    elif quantity_type == 'null':
        return 'null'
      

# ---- #
# kana #
# ---- #
def morphological_analysis(text: str, model_path: str, kytea_path: str) -> str:
    cmd_echo = subprocess.Popen(
        ['echo', text],
        stdout=subprocess.PIPE,
    )
    cmd_kytea = subprocess.Popen(
        [kytea_path, '-model', model_path],
        stdin=cmd_echo.stdout,
        stdout=subprocess.PIPE
    )

    end_of_pipe = cmd_kytea.communicate()[0].decode('utf-8')

    return end_of_pipe


def convert_kana(strings):
    """ kana """
    result = morphological_analysis(strings, _KBM_MODEL, _KYTEA_PATH)
    result_strings = result.split(' ')
    target_array = [s.split('/')[2] for s in result_strings]
    join_strings = ''.join(target_array)
    regex = re.compile('[\u3041-\u309F]+')
    process_strings = regex.findall(join_strings)
    print(process_strings)
    hiragana = ''.join(process_strings)
    print(hiragana)
    katakana = jaconv.hira2kata(hiragana)
    print(katakana)
    zenkaku = jaconv.h2z(katakana, digit=True, ascii=True)
    print(zenkaku)

    return zenkaku
