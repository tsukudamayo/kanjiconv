import os
import json
from typing import Dict, List
from collections import OrderedDict

import operation as op


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
        # toplevel['kana'] = op.convert_kana(self.data['title'])
        toplevel['kana'] = ''
        toplevel['description'] = ''
        toplevel['dishType'] = 'main'
        toplevel['defaultServing'] = self.data['ingredients']['食材'].split('人')[0] + '人'
        toplevel['introductoryEssay'] = ''
        toplevel['content'] = content
        
        return toplevel

    def build_content(self, dish_servings, instruction_servings):
        content = {"dishServings": dish_servings, "instructionServings": instruction_servings}

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
    
        return op.parse_ingredients(ingredients)


class Instruction:

    def __init__(self, data):
        self.data = data

    def build(self):
        return self.fetch_instruction(self.data)

    def fetch_instruction(self, data: Dict) -> List:
        target = self.data['recipe']
        strings = target.split('\n')
        null_check = [s for s in strings if s]
    
        return [{"step": idx+1, "description": s} for idx, s in enumerate(null_check)]

def convert_servings(data: Dict, servings: int) -> List:
    """
    normalize ingredients quantity by servings

    args
    ****************************************************************
        input: 
        ------------------------------------------------------------
            data: dict
              ex : 
                   {
                       "title": "うずら豆の甘煮",
                       "url": "https://www.bh-recipe.jp/recipe/010100001.html",
                       "recipe": "うずら豆はよく洗い、浮く豆は除きます。鍋に、豆と水カップ４を入れて５～６時間おきます。\nそのまま弱火にかけ、煮立ったら中火にして５～６分煮て、ざるにとり、湯を捨てます。\n豆を鍋にもどし、豆がかくれる程度に水を加えて火にかけ、落しぶたをして、煮立ったら弱火にし、約１時間、ときどき水をたしながら（豆にいつも湯がかぶっているようにする）煮ます。\n豆がやわらかくなったら砂糖を２回に分けて入れ、弱火でさらに２０分煮て、塩を加えて火を止めます。\nそのままさめるまで（できればひと晩）おいて、味を含ませます。\n",
                       "time": "60分以上",
                       "calory": "266kcal",
                       "ingredients": {
                           "食材": "4人分",
                           "うずら豆": "カップ２（３００ｇ）",
                           "砂糖": "９０ｇ",
                           "塩": "小さじ１／５"
                       }
                   }
            servings: int  
               The number of servings which you want to convert
        ------------------------------------------------------------
        output: Dict
            Ingredients which converted quantities

    ****************************************************************        
    """

    default_servings = int(data['ingredients']['食材'].split('人')[0])
    dish_builder = Dish(data)
    dish = dish_builder.build()

    norm = op.normalize_quantity(dish, default_servings)

    return multiply_dish(norm, dish, servings, default_servings)


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
        params = op.multiply_quantity(dish, norm, servings)
        multi = op.Multiplier(dish, params)
        ingredients = multi.build()

        return ingredients


def load_json(filepath: str) -> Dict:
    """
    convert json to OrderedDict python object
        Input:
           filepath: filepath of the target
        Output:
           data: OrederedDict python object
    """
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
    #     import time
    #     time0 = time.time()
    #     print('############################ {} ####################################'.format(count))
    #     src_path = os.path.join(src_dir, f)
    #     dst_path = os.path.join(dst_dir, f)

    #     if not f.endswith('.json'):
    #         continue
    #     if os.path.isfile(dst_path):
    #         continue

    import time
    time0 = time.time()
    src_path = './test_data/10100003.json'
    dst_path = './dest/10100003.json'

    try:
        ingredients_2 = convert_servings(load_json(src_path), 2)
        ingredients_4 = convert_servings(load_json(src_path), 4)
        print('ingredients_2')
        print(ingredients_2)
        print('ingredients_4')
        print(ingredients_4)
    except ValueError:
        print('Value Error')
        # continue
    
    # ---- #
    # dish #
    # ---- #
    dish_builder = Dish(load_json(src_path))
    dish2 = dish_builder.build(ingredients=ingredients_2)
    dish4 = dish_builder.build(ingredients=ingredients_4)
    dish_servings = []
    dish_servings.append({"unit": "2人", "dishes": [dish2]})
    dish_servings.append({"unit": "4人", "dishes": [dish4]})
    
    # ----------- #
    # instruction #
    # ----------- #
    instruction_builder = Instruction(load_json(src_path))
    instruction = instruction_builder.build()
    instruction_servings = []
    instruction_servings.append({"unit": "2人", "instructions": instruction})
    instruction_servings.append({"unit": "4人", "instructions": instruction})
    
    # ------------ #
    # build recipe #
    # ------------ #
    recipe_instance = Recipe(load_json(src_path), dish_servings, instruction_servings)
    recipe = recipe_instance.build()
    
    with open(dst_path, 'w', encoding='utf-8') as w:
        json.dump(recipe, w, indent=4, ensure_ascii=False)

    # count += 1
    time1 = time.time()
    print(time1 - time0)
        

if __name__ == '__main__':
    main()
