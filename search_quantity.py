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

    f = file_list[6]
    src_path = os.path.join('./test_data', f)
    with open(src_path, 'r', encoding='utf-8') as r:
        data = json.load(r)
    print(data)
    instructions = fetch_instruction(data)
    print(instructions)
    all_sentences = []
    all_converts = []
    for sample in instructions:
        print(sample)
        sentence = sample['description']

        is_decimal = [s.isdecimal() for s in sentence]
        # print(is_decimal)
        convert_sentence = ''
        sentence_length = len(sentence)
        for idx, (s, d) in enumerate(zip(sentence, is_decimal)):
            print(idx, s, d)
            if d:
                decimal_flg = False
                print('idx : ', idx)
                print('idx-quantity_length : ', sentence[idx-quantity_length])
                if (idx - quantity_length) > 0:
                    foward_range = idx - quantity_length
                else:
                    foward_range = 0
                if (idx + quantity_length) > len(sentence):
                    backward_range = len(sentence)
                else:
                    backward_range = idx + quantity_length

                forward = sentence[foward_range:idx]
                backward = sentence[idx+1:idx+(quantity_length+1)]
                print('foraward : ', forward)
                print('backward : ', backward)
                forward_candidate = ''
                for i in range(1, (quantity_length+1)):
                    print('i : ', i)
                    print('foward_candidate : ', forward_candidate)
                    if forward_candidate in quantity_set:
                        decimal = int(s) / servings * multiplier
                        if decimal.is_integer():
                            decimal = int(decimal)
                        decimal_flg = True
                        zenkaku = jaconv.h2z(str(decimal), digit=True)
                        convert_sentence += zenkaku
                        break
                    try:
                        que = forward[-i]
                        print('que')
                        print(que)
                        forward_candidate = que + forward_candidate
                    except IndexError:
                        pass

                if decimal_flg:
                    pass
                else:
                    backward_candidate = ''
                    for i in range(quantity_length - 1):
                        print(i)
                        if backward_candidate in quantity_set:
                            decimal = int(s) / servings * multiplier
                            if decimal.is_integer():
                                decimal = int(decimal)
                            decimal_flg = True
                            zenkaku = jaconv.h2z(str(decimal), digit=True)
                            convert_sentence += zenkaku
                            break
                        try:
                            que = backward[i]
                            print('que')
                            print(que)
                            backward_candidate = backward_candidate + que
                            print('backward_candidate')
                            print(backward_candidate)                            
                        except IndexError:
                            pass

                if not decimal_flg:
                    convert_sentence += s
            else:
                convert_sentence += s
        print('sentence : ', sentence)
        all_sentences.append(sentence)
        print('convert : ' ,convert_sentence)
        all_converts.append(convert_sentence)
    print('sentence')
    print(all_sentences)
    print('convert')
    print(all_converts)
    
    

if __name__ == '__main__':
    main()
