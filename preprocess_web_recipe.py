import json
from typing import Dict, List
from collections import OrderedDict

from operation import normalize_quantity
from operation import multiply_quantity
from operation import build_mulitply_quantities
from operation import convert_kana


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

        return self.build_dishes(title, ingredients)

    def build_dishes(self, title: str, ingredients: List) -> Dict:
        cookingtool = ""
        nutrition  = [
                      {"note":  ""},
                      {"salt": 0.0},
                      {"protein": 0.0},
                      {"calory": 15},
                      {"lipid": 0.0},
                      {"carbohydrate": 0.0},
                     ]
        return {
            "title": title,
            "cookingTool": cookingtool,
            "nutrition": nutrition,
            "ingredients": ingredients,
        }
    
    
    def fetch_title(self, data: Dict) -> str:
    
        return data['title']
    
    
    def fetch_ingredients(self, data: Dict) -> Dict:
    
        ingredients = data['ingredients']
        ingredients.pop('食材')
        def generate_ordered_params(k: str, v: str) -> Dict:
            ordered_params = OrderedDict()
            ordered_params["description"] = k
            ordered_params["quantityText"] = v
            ordered_params["ingredientId"] = 0
            ordered_params["classificationId"] = 0
            ordered_params["intermediateId"] = 0
            
            return ordered_params
    
        return [generate_ordered_params(k, v) for k, v in ingredients.items()]


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
    test_data = './test_data/10100006.json'
    data = load_json(test_data)
    dish_builder = Dish(data)
    dish = dish_builder.build()
    dish4 = dish
    # ------------- #
    # dish_servings #
    # ------------- #
    dish_servings = []
    dish_servings.append({"unit": 

    dish_servings['4人前'] = dish

    test_data = './test_data/10100006.json'
    data = load_json(test_data)
    dish_builder = Dish(data)
    dish = dish_builder.build()
    norm = normalize_quantity(dish, 4)
    params = multiply_quantity(dish, norm, 2)
    dish2_ing = build_mulitply_quantities(dish, params)
    print('dish2_ing')
    print(dish2_ing)

    print('dish')
    print(dish)
    with open('dish4_config.json', 'w', encoding='utf-8') as w:
        json.dump(dish4, w, indent=4, ensure_ascii=False)

    with open('dish2_config.json', 'w', encoding='utf-8') as ww:
        json.dump(dish2_ing, ww, indent=4, ensure_ascii=False)

    # ------------- #
    # dish_servings #
    # ------------- #
    cookingtool = ""
    nutrition  = [
                  {"note":  ""},
                  {"salt": 0.0},
                  {"protein": 0.0},
                  {"calory": 15},
                  {"lipid": 0.0},
                  {"carbohydrate": 0.0},
                 ]
    dish2 = {
        "title": data['title'],
        "cookingTool": '',
        "nutrition": nutrition,
        "ingredients": dish2_ing
    }
        
    dish_servings['2人前'] = dish2

    with open('dishSerivngs.json', 'w', encoding='utf-8') as d:
        json.dump(dish_servings, d, indent=4, ensure_ascii=False)
    

    instruction_builder = Instruction(data)
    instruction = instruction_builder.build()
    print('instruction')
    print(instruction)

    # -------------------- #
    # instruction_servings #
    # -------------------- #
    instruction_servings = OrderedDict()
    instruction_servings['2人前'] = instruction
    instruction_servings['4人前'] = instruction

    # content
    content = OrderedDict()
    content["dishSerivings"] = dish_servings
    content["instructionServings"] = instruction_servings

    # toplevel
    toplevel = OrderedDict()
    toplevel['recipeId'] = None
    toplevel['title'] = data['title']
    toplevel['kana'] = convert_kana(data['title'])
    toplevel['description'] = ''
    toplevel['dishType'] = 'main'
    toplevel['defaultServing'] = '4人'
    toplevel['content'] = content

    with open('recipes.json', 'w', encoding='utf-8') as w:
        json.dump(toplevel, w, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()
