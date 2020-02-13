import os
import json
from typing import Dict, List
from collections import OrderedDict

from operation import normalize_quantity
from operation import multiply_quantity
from operation import convert_kana
from operation import parse_ingredients
from operation import Multiplier


class Recipe:
    def __init__(self, data, dish_servings, instruction_servings):
        self.data = data
        self.dish_servings = dish_servings
        self.instruction_servings = instruction_servings

    def build(self):
        content = self.build_content(self.dish_servings, self.instruction_servings)

        return self.build_recipe(content)
        

    def build_recipe(self, content) -> Dict:
        toplevel = OrderedDict()
        toplevel['recipeId'] = None
        toplevel['title'] = self.data['title']
        toplevel['kana'] = convert_kana(self.data['title'])
        toplevel['description'] = ''
        toplevel['dishType'] = 'main'
        toplevel['defaultServing'] = self.data['ingredients']['食材'].split('人')[0] + '人'
        toplevel['introductoryEssay'] = ''
        toplevel['content'] = content
        
        return toplevel

    def build_content(self, dish_servings, instruction_servings):
        content = []
        content.append({"dishServings": dish_servings})
        content.append({"instructionServings": instruction_servings})

        return content


class Dish:

    def __init__(self, data):
        self.data = data

    def build(self, ingredients=None):
        title = self.fetch_title(self.data)
        if not ingredients:
            ingredients = self.fetch_ingredients(self.data)

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
def convert_servings(data: Dict, servings: int) -> List:
    default_servings = int(data['ingredients']['食材'].split('人')[0])
    dish_builder = Dish(data)
    dish = dish_builder.build()

    norm = normalize_quantity(dish, default_servings)

    return multiply_dish(norm, dish, servings, default_servings)


def multiply_dish(norm, dish, servings, default_servings):
    if servings == default_servings:
        ingredients = dish['ingredients']

        return ingredients
    else:
        params = multiply_quantity(dish, norm, servings)
        multi = Multiplier(dish, params)
        ingredients = multi.build()

        return ingredients


def load_json(filepath: str) -> Dict:
    with open(filepath, 'r', encoding='utf-8') as r:
        data = json.load(r, object_pairs_hook=OrderedDict)

    return data


def main():
    # count = 0
    # file_list = sorted(os.listdir('./test_data/betterhome_recipe'))
    # src_dir = './test_data/betterhome_recipe'
    # dst_dir = './dest'
    # if os.path.isdir(dst_dir) is False:
    #     os.makedirs(dst_dir)
    # for f in file_list:
    #     src_path = os.path.join(src_dir, f)
    #     dst_path = os.path.join(dst_dir, f)

    #     if not f.endswith('.json'):
    #         continue
    #     if os.path.isfile(dst_path):
    #         continue

    src_path = './test_data/10100003.json'
    dst_path = './dest/10100003.json'

    ingredients_2 = convert_servings(load_json(src_path), 2)
    ingredients_4 = convert_servings(load_json(src_path), 4)
    print('ingredients_2')
    print(ingredients_2)
    print('ingredients_4')
    print(ingredients_4)

    # ---- #
    # dish #
    # ---- #
    dish_builder = Dish(load_json(src_path))
    dish2 = dish_builder.build(ingredients=ingredients_2)
    dish4 = dish_builder.build(ingredients=ingredients_4)
    dish_servings = []
    dish_servings.append({"unit": "2人", "dishes": dish2})
    dish_servings.append({"unit": "4人", "dishes": dish4})

    # ----------- #
    # instruction #
    # ----------- #
    instruction_builder = Instruction(load_json(src_path))
    instruction = instruction_builder.build()
    instruction_servings = []
    instruction_servings.append({"unit": "2人", "instruction": instruction})
    instruction_servings.append({"unit": "4人", "instruction": instruction})

    # ------------ #
    # build recipe #
    # ------------ #
    recipe_instance = Recipe(load_json(src_path), dish_servings, instruction_servings)
    recipe = recipe_instance.build()
    
    with open(dst_path, 'w', encoding='utf-8') as w:
        json.dump(recipe, w, indent=4, ensure_ascii=False)
        

if __name__ == '__main__':
    main()
