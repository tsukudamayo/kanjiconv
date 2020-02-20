import os
import json
import re
import regex
import subprocess
import itertools
from typing import Dict, List, Set, Any
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
            yield {'description': k, 'quantityText': None, 'items': list(divide_key_value(v))}
        else:
            yield {'description': k, 'quantityText': v}


def generator_to_dict(dic: Dict) -> Dict:
    return {"items": list(divide_key_value(dic))}


# ---------- #
# preprocess #
# ---------- #
class Preprocessor:

    def __init__(self, data: List):
        ingredients = data['ingredients']
        self.hankaku_ingredients = [list(dict_to_hankaku(i)) for i in ingredients]
        self.hankaku_ingredients = list(itertools.chain.from_iterable(self.hankaku_ingredients))
        self.quantity_text = [list(aggregate_quantities(i)) for i in self.hankaku_ingredients]
        self.quantity_text = list(itertools.chain.from_iterable(self.quantity_text))
        self.candidate_borders = [candidate_border(q) for q in self.quantity_text]
        self.separate_quantities = [list(separate_quantity(q, b)) for q, b in zip(self.quantity_text, self.candidate_borders)]
        self.quantity_types = [[define_input_type(w) for w in s] for s in self.separate_quantities]

    def normalize_quantity(self, division: Any) -> List:
        norm_quantities = [[operation_by_type(t, w, division) for t, w in zip(types, words)]
                           for types, words in zip(self.quantity_types, self.separate_quantities)]
        
        return norm_quantities

    def multiply_quantity(self, params: List, multiplier: Any) -> List:
        output_types = [define_output_type(words) for words in self.quantity_types]
        multiply_quantities = [[operation_by_output_type(q, t, w, multiplier)
                                for t, w in zip(types, words)]
                               for q, types, words in zip(output_types, self.quantity_types, params)]
        
        return multiply_quantities
        

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
        str_multi_params = [[str(i) for i in p] for p in self.params]
        print('src_multi_params')
        print(str_multi_params)
        join_strings = [self.join_quantity_and_number(i) for i in str_multi_params]
        print('join_strings')
        print(join_strings)
        self.queue = join_strings
        convert_ingredients = [list(self.dict_to_zenkaku(i)) for i in src_ingredients]
        convert_ingredients = list(itertools.chain.from_iterable(convert_ingredients))

        return convert_ingredients

    def join_quantity_and_number(self, strings_array: List) -> str:
        print('join_quantity_and_number/strings_array', strings_array)
        types_array = [define_input_type(s) for s in strings_array]
        print('join_quantity_and_number/types_array', types_array)
        nonstr_idx = []
        for idx, (s, t) in enumerate(zip(strings_array, types_array)):
            if t != 'strings':
                nonstr_idx.append(idx)
        print('nonstr_idx')
        print(nonstr_idx)

        operator_pattern = re.compile('[と.]')
        pattern = re.search(operator_pattern, ''.join(strings_array))
        if not strings_array:
            return strings_array[0]
        elif len(nonstr_idx) > 1 and pattern:
            start = nonstr_idx[0]
            end = nonstr_idx[1] + 1
            return self.join_and_compute_fraction(strings_array, start, end)
        else:
            return ''.join(strings_array)


    def join_and_compute_fraction(self, strings_array: List, start: int, end: int) -> str:
        numerical_part = strings_array[start:end]
        print('numercal_part')
        print(numerical_part)
        del strings_array[start:end]
        quantity_part = strings_array
        if '～' in numerical_part:
            result = ''.join(numerical_part)
        else:
            print('0')
            print(numerical_part[0])
            print('1')
            print(numerical_part[-1])
            result = str(Fraction(numerical_part[0]) + Fraction(numerical_part[-1]))
            print('result')
            print(result)

        if start == 0:
            quantity_part.insert(0, result)
        else:
            quantity_part.append(result)

        return ''.join(quantity_part)
 

    def dict_to_zenkaku(self, ingredients: Dict) -> List:
        # TODO TEST
        # print('dict_to_zenkaku/ingredients')
        # print(ingredients)
        if 'items' in ingredients.keys():
            for idx, item in enumerate(ingredients['items']):
                que = self.queue.pop(0)
                # print('que')
                # print(que)
                # print('item')
                # print(item)
                # print(ingredients['items'][idx]['quantityText'])
                ingredients['items'][idx]['quantityText'] = self.value_to_zenkaku(que)
            yield ingredients
        else:
            que = self.queue.pop(0)
            ingredients['quantityText'] = self.value_to_zenkaku(que)
            yield ingredients


    def items_to_zenkaku(self, items: List) -> Dict:
        for item in items:
            yield list(self.dict_to_zenkaku(item))

    def value_to_zenkaku(self, value: str) -> str:
        null_pattern = re.compile(r'null')
        match = re.search(null_pattern, value)
        if match:
            return None
    
        zenkaku = jaconv.h2z(value, kana=True, digit=True, ascii=True)
    
        return zenkaku


def multiply_dish(norm, dish, servings, default_servings):
    """
    multiply normalized ingredients by servings
    Input: 
        norm: dict normalized ingreidents by function op.normalize_quantity()
        dish: dict return value Dish.build()
        servings: int 
            servings which you want to convert
        default_servings: int
            ex:
            data = load_json(src_path)
            default_servings = data['ingredients']['食材'].split('人')[0]

    Output:
        dict: multiplied ingredients
    """

    if servings == default_servings:
        ingredients = dish['ingredients']

        return ingredients
    else:
        preprocess = Preprocessor(dish)
        params = preprocess.multiply_quantity(norm, servings)
        multi = Multiplier(dish, params)
        ingredients = multi.build()

        # # TODO TEST
        # print('multiply_dish/preprocess')
        # print(preprocess)
        # print(params)
        # print(ingredients)

        return ingredients


def operation_by_type(types: str, strings: str, division: Any) -> Any:
    if types == 'real':
        try:
            result = float(strings) / division
        except ValueError:
            return None
        if result.is_integer():
            return int(result)
        elif not result.is_integer():
            return result
    elif types == 'fraction':
        return Fraction(strings) / division
    else:
        return strings

    
def define_input_type(strings: str) -> str:
    print('strings')
    print(strings)
    symbol_pattern = re.compile('[()~、]')
    kanji_pattern = regex.compile(r'\p{Script=Han}+')
    symbol = re.search(symbol_pattern, strings)
    kanji = kanji_pattern.search(strings)

    print('is_alpha() : ', strings.isalpha())
    if strings == '':
        return 'null'
    elif strings.isalpha() or symbol or kanji:
        return 'strings'
    else:
        if strings.find('/') >= 0:
            return 'fraction'
        else:
            return 'real'


# TODO first == second test
def separate_quantity(strings: str, border: int) -> List:
    first = strings[:border]
    yield first
    second = strings[border:]
    has_candidate = candidate_border(second)
    if has_candidate:
        yield from separate_quantity(second, has_candidate)
    else:
        if first == second:
            pass
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


def aggregate_description(dic: Dict) -> str:
    instruction = dic['description']
    yield instruction


def dict_to_hankaku(zenkaku_dict: Dict) -> Dict:
    if 'items' in zenkaku_dict:
        items_value = zenkaku_dict['items']
        items = generator_to_hankaku(items_value)
        yield items
    else:
        yield {k: value_to_hankaku(v) for k, v in zenkaku_dict.items()}


def generator_to_hankaku(items: List) -> Dict:
    return {"items": list(itertools.chain.from_iterable(list(generator_to_items(items))))}


def generator_to_items(items: List):
    return [list(dict_to_hankaku(item)) for item in items]


def value_to_hankaku(value: Any) -> Any:
    if isinstance(value, str):
        hankaku = jaconv.z2h(value, kana=False, digit=True, ascii=True)
        return hankaku
    else:
        return value


def define_output_type(words: List) -> str:
    null_check = [w == 'null' for w in words]
    if all(null_check):
        return 'null'
    if words[0] == 'strings':
        return 'fraction'
    else:
        return 'real'

# TODO test bug fraction to float
def operation_by_output_type(quantity_type: str, word_type:str, strings: str,  multiplier: Any) -> List:
    # print('quantity_type : ', quantity_type)
    # print('word_type : ', word_type)
    # print('strings : ' ,strings)
    # print('multiplier : ', multiplier)
    if not strings:
        return 'null'
    if quantity_type == 'fraction':
        if word_type == 'strings':
            # print('fraction/strings')
            return strings
        else:
            fr = Fraction(strings) * multiplier
            return fr.limit_denominator(5)
    elif quantity_type == 'real':
        if word_type == 'strings':
            # print('real/strings')
            return strings
        elif word_type == 'fraction':
            fr = Fraction(strings) * multiplier
            return fr.limit_denominator(5)
        else:
            # print('real/else')
            if (float(strings) * multiplier).is_integer():
                return int(float(strings) * multiplier)
            else:
                return round((float(strings) * multiplier), 1)
    elif quantity_type == 'null':
        return 'null'


# ----------- #
# Instruction #
# ----------- #
def fetch_nest_value(data: Dict) -> List:
    for k, v in data.items():
        if isinstance(v, dict):
            yield from fetch_nest_value(v)
        else:
            yield v


def fetch_all_words_in_ingredients():
    quantity_list = []
    file_list = sorted(os.listdir('./test_data/betterhome_recipe'))
    for f in file_list:
        src_path = os.path.join('./test_data/betterhome_recipe', f)
        if not src_path.endswith('.json'):
            continue
        with open(src_path, 'r', encoding='utf-8') as r:
            data = json.load(r)
        values = list(fetch_nest_value(data['ingredients']))
        candidate_borders = [candidate_border(v) for v in values]
        separate_quantities = [list(separate_quantity(v, b))
                               for v, b
                               in zip(values, candidate_borders)]
        flatten = list(itertools.chain.from_iterable(separate_quantities))
        only_quantity = [s for s in flatten if s.isalpha()]
        quantity_list.extend(only_quantity)

    quantity_set = set(quantity_list)
    # print('quantity_set')
    # print(quantity_set)
    quantity_length = max([len(q) for q in list(quantity_set)])
    # print('quantity_length')
    # print(quantity_length)

    return quantity_set, quantity_length


def convert_instructions(data: Dict, servings: int, multiplier: int,
                         quantity_set: Set, quantity_length: int) -> List:

    def fetch_instruction(data: Dict) -> List:
        target = data['recipe']
        strings = target.split('\n')
        null_check = [s for s in strings if s]
        
        return [{"steps": idx+1, "description": s} for idx, s in enumerate(null_check)]

    def preprocess_mixed_number(sentences: List, types: List) -> List:
        strings_operator = set(['.', 'と'])
        operator_flg = False
        preprocessed_array = []
        for idx, (s, t) in enumerate(zip(sentences, types)):
            if operator_flg:
                operator_flg = False
                continue
            elif s in strings_operator and types[idx-1] != 'strings' and types[idx+1] != 'strings':
                operator_flg = True
                preprocessed_array.pop()
                join_array = [sentences[idx-1], s, sentences[idx+1]]
                joined_array = ''.join(join_array)
                preprocessed_array.append(joined_array)
            else:
                preprocessed_array.append(s)

        return preprocessed_array


    def compute_mixed_number(sentences: List, types: List) -> List:
        compute_fraction = []
        summation_pattern = re.compile('[と.]')
        for s, t in zip(sentences, types):
            pattern = re.search(summation_pattern, s)
            if t == 'fraction' and pattern:
                split_string = s.split(pattern.group(0))
                compute = str(Fraction(split_string[0]) + Fraction(split_string[1]))
                compute_fraction.append(compute)
            else:
                compute_fraction.append(s)

        return compute_fraction
             

    def _join_quantity_and_number(strings_array: List) -> str:
        print('join_quantity_and_number/strings_array', strings_array)
        types_array = [define_input_type(s) for s in strings_array]
        print('join_quantity_and_number/types_array', types_array)
        nonstr_idx = []
        for idx, (s, t) in enumerate(zip(strings_array, types_array)):
            if t != 'strings':
                nonstr_idx.append(idx)
        print('nonstr_idx')
        print(nonstr_idx)

        if strings_array[0] == strings_array[1]:
            return strings_array[0]
        elif len(nonstr_idx) > 1:
            start = nonstr_idx[0]
            end = nonstr_idx[1] + 1
            return _join_and_compute_fraction(strings_array, start, end)
        else:
            return ''.join(strings_array)


    def _join_and_compute_fraction(strings_array: List, start: int, end: int) -> str:
        numerical_part = strings_array[start:end]
        print('numercal_part')
        print(numerical_part)
        del strings_array[start:end]
        quantity_part = strings_array
        if '～' in numerical_part:
            result = ''.join(numerical_part)
        else:
            print('0')
            print(numerical_part[0])
            print('1')
            print(numerical_part[-1])
            result = str(Fraction(numerical_part[0]) + Fraction(numerical_part[-1]))
            print('result')
            print(result)

        if start == 0:
            quantity_part.insert(0, result)
        else:
            quantity_part.append(result)

        return ''.join(quantity_part)


    def _value_to_zenkaku(value: str) -> str:
        null_pattern = re.compile(r'null')
        match = re.search(null_pattern, value)
        if match:
            return None
    
        zenkaku = jaconv.h2z(value, kana=True, digit=True, ascii=True)
    
        return zenkaku

    def multiply_parameter(sentences: List, types: List, servings: int, multiplier: int) -> List:
        convert_sentence = ''
        for idx, (s, t) in enumerate(zip(sentences, types)):
            print('s : ', s)
            print('t : ', t)            
            convert_flg = False
            if t != 'strings':
                try:
                    forward = sentences[idx - 1]
                    backward = sentences[idx + 1]
                except IndexError:
                    continue
                forward_candidate = ''
                for i in range(1, quantity_length + 1):
                    print('convert_sentence')
                    print(convert_sentence)
                    if forward_candidate in quantity_set:
                        if t == 'real':
                            decimal = float(s) / servings * multiplier
                            if decimal.is_integer():
                                decimal = int(decimal)
                                convert_sentence += str(decimal)
                            else:
                                decimal = float(decimal)
                                convert_sentence += str(decimal)
                        elif t == 'fraction':
                            decimal = Fraction(s) / servings * multiplier
                            convert_sentence += str(decimal)
                        convert_flg = True
                        break
                    try:
                        que = forward[-i]
                        print('que')
                        print(que)
                        print('forward_candidate')
                        print(forward_candidate)
                        forward_candidate = que + forward_candidate
                        print('forward_candidate')
                        print(forward_candidate)
                        
                    except IndexError:
                        pass
                if decimal_flg:
                    pass
                else:
                    backward_candidate = ''
                    for i in range(quantity_length - 1):
                        # print(i)
                        if backward_candidate in quantity_set:
                            if t == 'real':
                                decimal = float(s) / servings * multiplier
                                if decimal.is_integer():
                                    decimal = int(decimal)
                                    convert_sentence += str(decimal)
                                else:
                                    decimal = float(decimal)
                                    convert_sentence += str(decimal)
                            elif t == 'fraction':
                                decimal = Fraction(s) / servings * multiplier
                                convert_sentence += str(decimal)
                            convert_flg = True
                            break
                        try:
                            que = backward[i]
                            # print('que')
                            # print(que)
                            backward_candidate = backward_candidate + que
                            # print('backward_candidate')
                            # print(backward_candidate)
                        except IndexError:
                            pass
                    if not convert_flg:
                        convert_sentence += s
            else:
                convert_sentence += s
        print('compute_multiply/convert_sentence')
        print(convert_sentence)
            
        return convert_sentence

        
    
    instructions = fetch_instruction(data)
    print('instructions')
    print(instructions)
    all_sentences = []
    all_converts = []
    decimal_flg = False

    hankaku_instructions = [list(dict_to_hankaku(i)) for i in instructions]
    hankaku_instructions = list(itertools.chain.from_iterable(hankaku_instructions))
    print('hankaku_instructions')
    print(hankaku_instructions)
    descriptions = [list(aggregate_description(i)) for i in hankaku_instructions]
    descriptions = list(itertools.chain.from_iterable(descriptions))
    print('descriptions')
    print(descriptions)
    candidate_borders = [candidate_border(q) for q in descriptions]
    print('candidate_borders')
    print(candidate_borders)
    separate_quantities = [list(separate_quantity(q, b)) for q, b in zip(descriptions, candidate_borders)]
    string_types = [[define_input_type(w) for w in s] for s in separate_quantities]
    print('separate_quantities')
    print(separate_quantities)
    print('string_types')
    print(string_types)
    preprocess = [preprocess_mixed_number(s, t) for s, t in zip(separate_quantities, string_types)]
    print('preprocess')
    print(preprocess)
    preprocess_type = [[define_input_type(w) for w in p] for p in preprocess]
    print('preprocess_type')
    print(preprocess_type)
    preprocess_fraction = [compute_mixed_number(s, t) for s, t in zip(preprocess, preprocess_type)]
    print('preprocess_fraction')
    print(preprocess_fraction)
    multiply_servings = [multiply_parameter(s, t, servings, multiplier) for s, t in zip(preprocess_fraction, preprocess_type)]
    print('multiply_servings')
    print(multiply_servings)

    convert_instructions = [[''.join(list(_value_to_zenkaku(w))) for w in a] for a in multiply_servings]
    convert_instructions = [''.join(l) for l in convert_instructions]
    print('convert_instructions')
    print(convert_instructions)

    return convert_instructions


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
    hiragana = ''.join(process_strings)
    katakana = jaconv.hira2kata(hiragana)
    zenkaku = jaconv.h2z(katakana, digit=True, ascii=True)

    return zenkaku
