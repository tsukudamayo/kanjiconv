import os
import json
from typing import Dict, List
from collections import OrderedDict

from operation import normalize_quantity
from operation import multiply_quantity
from operation import convert_kana
from operation import parse_ingredients
from operation import Multiplier


def load_json(filepath: str) -> Dict:
    with open(filepath, 'r', encoding='utf-8') as r:
        data = json.load(r, object_pairs_hook=OrderedDict)

    return data


def fetch_unit(data: Dict) -> str:

    return data['ingredients']['食材']


class Dish:

    def __init__(self, data):
        self.data = data

    def build(self):
        title = self.fetch_title(self.data)
        ingredients = self.fetch_ingredients(self.data)
        print('****************************************************************')
        print('ingredients')
        print(ingredients)
        print('****************************************************************')

        return self.build_dishes(title, ingredients)

    def build_dishes(self, title: str, ingredients: List) -> Dict:
        cookingtool = ""
        nutrition  = {
            "note":  "",
            "salt": 0,
            "protein": 0,
            "calory": self.fetch_calory(self.data),
            "lipid": 0,
            "carbohydrate": 0,
        }
                     
        return {
            "title": title,
            "cookingTool": cookingtool,
            "nutrition": nutrition,
            "ingredients": ingredients,
        }
    
    def fetch_title(self, data: Dict) -> str: return data['title']

    def fetch_calory(self, data: Dict) -> str: return data['calory'].split('kcal')[0]
    
    def fetch_ingredients(self, data: Dict) -> Dict:
    
        ingredients = data['ingredients']
        ingredients.pop('食材')
    
        return parse_ingredients(ingredients)


class Instruction:

    def __init__(self, data):
        self.data = data

    def build(self):
        return self.fetch_instruction(self.data)

    def fetch_instruction(self, data: Dict) -> List:
        target = self.data['recipe']
        strings = target.split('\n')
        null_check = [s for s in strings if s]
    
        return [{"steps": idx+1, "description": s} for idx, s in enumerate(null_check)]


def main():
    # count = 0
    # file_list = os.listdir('./test_data')
    # src_dir = './test_data'
    # dst_dir = './dest'
    # if os.path.isdir(dst_dir) is False:
    #     os.makedirs(dst_dir)
    # for f in file_list:
    #     src_path = os.path.join(src_dir, f)
    #     dst_path = os.path.join(dst_dir, f)

    src_path = './test_data/10100002.json'
    dst_path = './dest/10100002.json'
    data = load_json(src_path)
    dish_servings = []
    dish_builder = Dish(data)
    dish = dish_builder.build()
    dish4 = dish
    print('**************** dish4 ****************')
    print(dish4)
    for k, v in dish4.items():
        print('dish4 : ', k, v)
   
    # ------ #
    # dish 2 #
    # ------ #
    data = load_json(src_path)
    dish2_builder = Dish(data)
    dish2 = dish2_builder.build()
    norm = normalize_quantity(dish2, 4)
    params = multiply_quantity(dish2, norm, 2)
    multi = Multiplier(dish, params)
    dish2_ing = multi.build()
    print('***************************************')
    print('len norm : ', len(norm))
    print('len parmas : ', len(params))
    print('**************** norm ****************')
    for n in norm:
        print('n  : ', n)
    print('**************** params ****************')
    for p in params:
        print('p : ', p)
    print('**************** dish2 ****************')
    print(dish2_ing)
    for d in dish2_ing:
        print('dish2 : ', d)
    print('****************++++++++****************')
    print('len dish2_ing - params', len(dish2_ing), len(params))
    with open('dish4_config.json', 'w', encoding='utf-8') as w4:
        json.dump(dish4, w4, indent=4, ensure_ascii=False)
    with open('dish2_config.json', 'w', encoding='utf-8') as w2:
        json.dump(dish2_ing, w2, indent=4, ensure_ascii=False)

    cookingtool = ""
    nutrition  = {
        "note":  "",
        "salt": 0,
        "protein": 0,
        "calory": data['calory'].split('kcal')[0],
        "lipid": 0,
        "carbohydrate": 0,
    }
    dish2 = {
        "title": data['title'],
        "cookingTool": '',
        "nutrition": nutrition,
        "ingredients": dish2_ing
    }
  
    # ------------- #
    # dish_servings #
    # ------------- #
    dish_servings.append({"unit": "2人", "dishes": dish2})
    dish_servings.append({"unit": "4人", "dishes": dish4})
    
    instruction_builder = Instruction(data)
    instruction = instruction_builder.build()
    print('instruction')
    print(instruction)
    
    # -------------------- #
    # instruction_servings #
    # -------------------- #
    instruction_servings = []
    instruction_servings.append({"unit": "2人", "instruction": instruction})
    instruction_servings.append({"unit": "4人", "instruction": instruction})
    
    # content
    content = []
    content.append({"dishServings": dish_servings})
    content.append({"instructionServings": instruction_servings})
    
    # toplevel
    toplevel = OrderedDict()
    toplevel['recipeId'] = None
    toplevel['title'] = data['title']
    toplevel['kana'] = convert_kana(data['title'])
    toplevel['description'] = ''
    toplevel['dishType'] = 'main'
    toplevel['defaultServing'] = '4人'
    toplevel['introductoryEssay'] = ''
    toplevel['content'] = content
    
    print('result')
    print(toplevel)
    
    with open(dst_path, 'w', encoding='utf-8') as w:
        json.dump(toplevel, w, indent=4, ensure_ascii=False)

        # count += 1

        # if count == 2:
        #     break


if __name__ == '__main__':
    main()
