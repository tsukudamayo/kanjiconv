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
    print('data')
    print(data)
    print('normalize_quantity')
    ingredients = data['ingredients']
    print('ingredients')
    print(ingredients)
    hankaku_ingredients = [list(dict_to_hankaku(i)) for i in ingredients]
    hankaku_ingredients = list(itertools.chain.from_iterable(hankaku_ingredients))
    print('hankaku_ingredients')
    print(hankaku_ingredients)
    quantity_text = [list(aggregate_quantities(i)) for i in hankaku_ingredients]
    quantity_text = list(itertools.chain.from_iterable(quantity_text))
    print('quantitiy_text')
    print(quantity_text)
    candidate_borders = [candidate_border(q) for q in quantity_text]
    print('candidate_borders')
    print(candidate_borders)
    separate_quantities = [list(separate_quantity(q, b)) for q, b in zip(quantity_text, candidate_borders)]
    print('separate_quantities')
    print(separate_quantities)
    quantity_types = [[define_input_type(w) for w in s] for s in separate_quantities]
    print('quantity_types')
    print(quantity_types)
    print('separate_quantities')
    print(separate_quantities)
    norm_quantities = [[operation_by_type(t, w, divison) for t, w in zip(types, words)]
                       for types, words in zip(quantity_types, separate_quantities)]

    print('norm_quantities')
    print(norm_quantities)
    
    return norm_quantities


def operation_by_type(type: str, strings: str, division: Any) -> Any:
    if strings == '':
        strings = '0'
    print(type, strings)
    if type == 'real':
        return float(strings) / division
    elif type == 'fraction':
        return Fraction(strings) / division
    else:
        return strings

    
def define_input_type(strings: str) -> str:
    print(strings)
    pattern = re.compile('[()]')
    match = re.search(pattern, strings)
    if strings.isalpha() or match:
        return 'strings'
    else:
        if strings.find('/') >= 0:
            return 'fraction'
        else:
            return 'real'


def separate_quantity(strings: str, border: int) -> List:
    print('separate_quantity/strings')
    print(strings, border)
    first = strings[:border]
    yield first
    second = strings[border:]
    print('second: ', second)
    has_candidate = candidate_border(second)
    print('has_candidate : ', has_candidate)
    if has_candidate:
        yield from separate_quantity(second, has_candidate)
    else:
        yield second
    

def candidate_border(strings: str) -> int:
    print('strings')
    print(strings)

    if strings == '':
        return False
    else:
        fraction_pattern = re.compile('[0-9]{1,}/[0-9]{1,}')  # Fractions are treated as exceptions.
        match = re.match(fraction_pattern, strings)
        flg = strings[0].isdecimal()
        tmp_flg = strings[0].isdecimal()
        change_flg = False

        for idx, t in enumerate(strings):
            print('t : ', t)
            border = idx
            tmp_flg = strings[idx].isdecimal()
            print('flg : tmp_flg', flg, tmp_flg)
            print('flg != tmp_flg: ', flg != tmp_flg)
            if match:
                continue
            if flg != tmp_flg:
                change_flg = True
                print('change')
                return border
                break

        if change_flg is True:
            print('change_flg is True')
            return border
        else:
            print('change_flg is False')
            return False


def aggregate_quantities(dic: Dict) -> str:
    print('dic')
    print(dic)
    if 'items' in dic.keys():
        for d in dic['items']:
            print('d')
            print(d)
            yield from aggregate_quantities(d)
    else:
        if dic['quantityText'] is None:
            quantity_text = ''
        else:
            quantity_text = dic['quantityText']
        yield quantity_text


def dict_to_hankaku(zenkaku_dict: Dict) -> Dict:
    print('zenkaku_dict')
    print(zenkaku_dict)
    if isinstance(zenkaku_dict, dict):
        if 'items' in zenkaku_dict.keys():
            for d in zenkaku_dict['items']:
                yield from dict_to_hankaku(zenkaku_dict['items'])
        else:
            yield {k: value_to_hankaku(v) for k, v in zenkaku_dict.items()}
    elif isinstance(zenkaku_dict, list):
        for d in zenkaku_dict:
            yield from dict_to_hankaku(d)


def value_to_hankaku(value: Any) -> Any:
    if isinstance(value, str):
        hankaku = jaconv.z2h(value, kana=False, digit=True, ascii=True)
        return hankaku
    else:
        return value

# -------- #
# multiply #
# -------- #
def build_mulitply_quantities(data: List, multiparams: List) -> List:
    src_ingredients = data['ingredients']
    str_mulit_params = [[str(i) for i in p] for p in multiparams]
    join_strings = [''.join(i) for i in str_mulit_params]
    convert_ingredients = [dict_to_zenkaku(i, p)
                           for i, p in zip(src_ingredients, join_strings)]
    
    return convert_ingredients


def dict_to_zenkaku(ingredients: Dict, hankaku_param: str) -> List:
    ingredients['quantityText'] = value_to_zenkaku(hankaku_param)

    return ingredients


def value_to_zenkaku(value: str) -> str:
    zenkaku = jaconv.h2z(value, kana=True, digit=True, ascii=True)

    return zenkaku


# TODO merge normalize_quantity
def multiply_quantity(data: List, params: List, multiplier: Any) -> List:
    ingredients = data['ingredients']
    hankaku_ingredients = [dict_to_hankaku(i) for i in ingredients]
    print('multiply_quantity/hankaku_ingredients', hankaku_ingredients)
    quantity_text = [list(aggregate_quantities(i)) for i in hankaku_ingredients]
    print('multiply_quantity/quantity_texst', quantity_text)
    quantity_text = list(itertools.chain.from_iterable(quantity_text))
    print('multiply_quantity/quantity_texst', quantity_text)
    # quantity_text = [i['quantityText'] for i in hankaku_ingredients]
    candidate_borders = [candidate_border(q) for q in quantity_text]
    separate_quantities = [separate_quantity(q, b) for q, b in zip(quantity_text, candidate_borders)]
    quantity_types = [[define_input_type(w) for w in s] for s in separate_quantities]
    output_types = [define_output_type(words) for words in quantity_types]
    multiply_quantities = [[operation_by_output_type(q, t, w, multiplier)
                            for t, w in zip(types, words)]
                           for q, types, words in zip(output_types, quantity_types, params)]
    
    # return separate_quantities, quantity_types, output_types, params
    return multiply_quantities


def define_output_type(words: List) -> str:
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
      

# ---- #
# kana #
# ---- #
def morphological_analysis(text: str, model_path: str, kytea_path: str) -> str:
    print('input text')
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
