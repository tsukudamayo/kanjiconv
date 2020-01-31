import re
import subprocess
from typing import Dict, List, Any
from fractions import Fraction

import jaconv


_KBM_MODEL = 'kytea-0.4.7/model/jp-0.4.7-1.mod'
_KNM_MODEL = 'kytea-0.4.7/RecipeNE-sample/recipe416.knm'
_KYTEA_PATH = 'kytea'


# --------- #
# normalize #
# --------- #
# TODO pytest
def normalize_quantity(data: List, divison: Any) -> List:
    ingredients = data['ingredients']
    hankaku_ingredients = [dict_to_hankaku(i) for i in ingredients]
    quantity_text = [i['quantityText'] for i in hankaku_ingredients]
    candidate_borders = [candidate_border(q) for q in quantity_text]
    separate_quantities = [separate_quantity(q, b) for q, b in zip(quantity_text, candidate_borders)]
    quantity_types = [[define_input_type(w) for w in s] for s in separate_quantities]
    norm_quantities = [[operation_by_type(t, w, divison) for t, w in zip(types, words)]
                       for types, words in zip(quantity_types, separate_quantities)]
    
    return norm_quantities


def operation_by_type(type: str, strings: str, division: Any) -> Any:
    if type == 'real':
        return float(strings) / division
    elif type == 'fraction':
        return Fraction(strings) / division
    else:
        return strings

    
def define_input_type(strings: str) -> str:
    if strings.isalpha():
        return 'strings'
    else:
        if strings.find('/') >= 0:
            return 'fraction'
        else:
            return 'real'



def separate_quantity(strings: str, border: int) -> List:
    first = strings[:border]
    second = strings[border:]

    return [first, second]
    

def candidate_border(strings: str) -> int:
    flg = strings[0].isdecimal()
    for idx, t in enumerate(strings):
        border = idx
        tmp_flg = strings[idx].isdecimal()
        if flg != tmp_flg:
            break

    return border


def dict_to_hankaku(zenkaku_dict: Dict) -> Dict:
    return {k: value_to_hankaku(v) for k, v in zenkaku_dict.items()}


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
    quantity_text = [i['quantityText'] for i in hankaku_ingredients]
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
