import os
import json
from typing import List, Dict
import itertools
import jaconv

from operation import candidate_border
from operation import separate_quantity


def fetch_instruction(data: Dict) -> List:
    target = data['recipe']
    strings = target.split('\n')
    null_check = [s for s in strings if s]

    return [{"steps": idx+1, "description": s} for idx, s in enumerate(null_check)]


def fetch_nest_value(data: Dict) -> List:
    for k, v in data.items():
        if isinstance(v, dict):
            yield from fetch_nest_value(v)
        else:
            yield v


def main():
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
    print('quantity_set')
    print(quantity_set)
    quantity_length = max([len(q) for q in list(quantity_set)])
    print('quantity_length')
    print(quantity_length)


    # -------- #
    # constant #
    # -------- #
    servings = 4
    multiplier = 2

    f = file_list[0]
    src_path = os.path.join('./test_data', f)
    with open(src_path, 'r', encoding='utf-8') as r:
        data = json.load(r)
    print(data)
    instructions = fetch_instruction(data)
    print(instructions)
    sample = instructions[0]
    print(sample)
    sentence = sample['description']
    print(sentence)
    is_decimal = [s.isdecimal() for s in sentence]
    print(is_decimal)
    convert_sentence = ''
    for idx, (s, d) in enumerate(zip(sentence, is_decimal)):
        print(idx, s, d)
        if d:
            decimal_flg = False
            print('idx : ', idx)
            forward = sentence[idx-(quantity_length):idx]
            backward = sentence[idx+1:idx+(quantity_length+1)]
            print(forward)
            print(backward)
            forward_candidate = ''
            for i in range(1, (quantity_length+1)):
                if forward_candidate in quantity_set:
                    decimal = int(s) / servings * multiplier
                    decimal_flg = True
                    zenkaku = jaconv.h2z(str(decimal), digit=True)
                    convert_sentence += zenkaku
                    break
                que = forward[-i]
                forward_candidate = que + forward_candidate
                print('forward_candidate')
                print(forward_candidate)
            if decimal_flg:
                pass
            else:
                backward_candidate = ''
                for i in range(quantity_length - 1):
                    print(i)
                    if backward_candidate in quantity_set:
                        decimal = int(s) / servings * multiplier
                        decimal_flg = True
                        zenkaku = jaconv.h2z(str(decimal), digit=True)
                        convert_sentence += zenkaku
                        break
                    try:
                        que = backward[i]
                    except IndexError:
                        break
                    forward_candidate = forward_candidate + que
                    print('backward_candidate')
                    print(backward_candidate)
            if not decimal_flg:
                convert_sentence += s
        else:
            convert_sentence += s
    print(convert_sentence)
    

if __name__ == '__main__':
    main()
