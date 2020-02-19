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

        if strings_array[0] == strings_array[1]:
            return strings_array[0]
        elif len(nonstr_idx) > 1:
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
    symbol_pattern = re.compile('[()~]')
    kanji_pattern = regex.compile(r'\p{Script=Han}+')
    symbol = re.search(symbol_pattern, strings)
    kanji = kanji_pattern.search(strings)
    
    if strings == '':
        return 'null'
    elif strings.isalpha() or symbol or kanji:
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
    
    instructions = fetch_instruction(data)
    # print(instructions)
    all_sentences = []
    all_converts = []
    decimal_flg = False

    hankaku_instructions = [list(dict_to_hankaku(i)) for i in instructions]
    hankaku_instructions = list(itertools.chain.from_iterable(hankaku_instructions))
    descriptions = [list(aggregate_description(i)) for i in hankaku_instructions]
    descriptions = list(itertools.chain.from_iterable(descriptions))
    candidate_borders = [candidate_border(q) for q in descriptions]
    separate_quantities = [list(separate_quantity(q, b)) for q, b in zip(descriptions, candidate_borders)]
    separate_quantities = list(itertools.chain.from_iterable(separate_quantities))
    process_fraction = list(itertools.chain.from_iterable(_join_quantity_and_number(separate_quantities)))
    string_types = [[define_input_type(w) for w in s] for s in process_fraction]

    print('process_fraction')
    print(process_fraction)

    for sentence_array, string_type_array in zip(process_fraction, string_types):
        # print('sentences_array')
        # print(sentence_array)
        # print('string_type_array')
        # print(string_type_array)

        convert_sentence = ''
        sentence_length = len(sentence_array)
        for idx, (s, t) in enumerate(zip(sentence_array, string_type_array)):
            decimal_flg = False
            # print('****************')
            # print('s')
            # print(s)
            # print('t')
            # print(t)
            # print('****************')

            if t == 'real':
                # print('idx : ', idx)
                # print('idx-quantity_length : ', sentence[idx-quantity_length])
                try:
                    forward = sentence_array[idx - 1]
                    backward = sentence_array[idx + 1]
                except IndexError:
                    continue
                print('s : ', s)
                print('foraward : ', forward)
                print('backward : ', backward)

                # ------- #
                # forward #
                # ------- #
                forward_candidate = ''
                for i in range(1, (quantity_length+1)):
                    if forward_candidate in quantity_set:
                        decimal = int(s) / servings * multiplier
                        if decimal.is_integer():
                            decimal = int(decimal)
                            zenkaku = jaconv.h2z(str(decimal), digit=True)
                            convert_sentence += zenkaku
                            decimal_flg = True
                            break
                        try:
                            que = forward[-i]
                            # print('que')
                            # print(que)
                            forward_candidate = que + forward_candidate
                        except IndexError:
                            pass
                if decimal_flg:
                    pass
                else:
                    backward_candidate = ''
                    for i in range(quantity_length - 1):
                        # print(i)
                        if backward_candidate in quantity_set:
                            decimal = int(s) / servings * multiplier
                            if decimal.is_integer():
                                decimal = int(decimal)
                            decimal_flg = True
                            zenkaku = jaconv.h2z(str(decimal), digit=True)
                            # print('backward/zenkaku')
                            convert_sentence += zenkaku
                            # print(zenkaku)
                            # print(convert_sentence)
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
    
                if not decimal_flg:
                    convert_sentence += jaconv.h2z(str(s), digit=True)
            else:
                # print('not decimal_flg')
                convert_sentence += s
        all_sentences.append(sentence_array)
        all_converts.append(convert_sentence)
    print(all_sentences)
    print(all_converts)

    return all_converts
                    
                
            # if t == 'real':
            #     if (idx - sentence_length) > 0:
            #         forward_range = idx - len(s)
            #     else:
            #         foward_range = 0
            #     if (idx + quantity_length) > len(s):
            #         backward_range = len(s)
            #     else:
            #         backward_range = idx + len(s)
   
    
    # for sample in instructions:
    #     # print(sample)
    #     sentence = sample['description']
    #     is_decimal = [s.isdecimal() for s in sentence]
    #     # print(is_decimal)
    #     convert_sentence = ''
    #     sentence_length = len(sentence)
    #     for idx, (s, d) in enumerate(zip(sentence, is_decimal)):
    #         decimal_flg = False
    #         # print(idx, s, d)
    #         if d:
    #             # ----- #
    #             # range #
    #             # ----- #
    #             # print('idx : ', idx)
    #             # print('idx-quantity_length : ', sentence[idx-quantity_length])
    #             if (idx - quantity_length) > 0:
    #                 foward_range = idx - quantity_length
    #             else:
    #                 foward_range = 0
    #             if (idx + quantity_length) > len(sentence):
    #                 backward_range = len(sentence)
    #             else:
    #                 backward_range = idx + quantity_length
    #             forward = sentence[foward_range:idx]
    #             backward = sentence[idx+1:idx+(quantity_length+1)]
    #             # print('foraward : ', forward)
    #             # print('backward : ', backward)
    
    #             forward_candidate = ''
    #             for i in range(1, (quantity_length+1)):
    #                 # print('decimal_flg : ', decimal_flg)
    #                 # print(s)
    #                 # print('forward_candidate', forward_candidate)
    #                 # print('forward_candidate in quantity_set : ', forward_candidate in quantity_set)
    #                 # print(forward_candidate in quantity_set)
    #                 # print('convert_sentence : ', convert_sentence)
    #                 # print('i : ', i)
    #                 # print('foward_candidate : ', forward_candidate)
    #                 if forward_candidate in quantity_set:
    #                     decimal = int(s) / servings * multiplier
    #                     if decimal.is_integer():
    #                         decimal = int(decimal)
    #                     decimal_flg = True
    #                     zenkaku = jaconv.h2z(str(decimal), digit=True)
    #                     # print('forward/zenkaku')
    #                     convert_sentence += zenkaku
    #                     # print(zenkaku)
    #                     # print(convert_sentence)
    #                     break
    #                 try:
    #                     que = forward[-i]
    #                     # print('que')
    #                     # print(que)
    #                     forward_candidate = que + forward_candidate
    #                 except IndexError:
    #                     pass
    
    #             if decimal_flg:
    #                 pass
    #             else:
    #                 backward_candidate = ''
    #                 for i in range(quantity_length - 1):
    #                     # print(i)
    #                     if backward_candidate in quantity_set:
    #                         decimal = int(s) / servings * multiplier
    #                         if decimal.is_integer():
    #                             decimal = int(decimal)
    #                         decimal_flg = True
    #                         zenkaku = jaconv.h2z(str(decimal), digit=True)
    #                         # print('backward/zenkaku')
    #                         convert_sentence += zenkaku
    #                         # print(zenkaku)
    #                         # print(convert_sentence)
    #                         break
    #                     try:
    #                         que = backward[i]
    #                         # print('que')
    #                         # print(que)
    #                         backward_candidate = backward_candidate + que
    #                         # print('backward_candidate')
    #                         # print(backward_candidate)
    #                     except IndexError:
    #                         pass
    
    #             if not decimal_flg:
    #                 convert_sentence += s
    #         else:
    #             # print('not decimal_flg')
    #             convert_sentence += s
    #     all_sentences.append(sentence)
    #     all_converts.append(convert_sentence)
    # print(all_sentences)
    # print(all_converts)

    # return all_converts
      

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
