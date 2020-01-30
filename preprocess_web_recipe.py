import json
from typing import Dict, List
from collections import OrderedDict


def load_json(filepath: str) -> Dict:
    with open(filepath, 'r', encoding='utf-8') as r:
        data = json.load(r, object_pairs_hook=OrderedDict)

    return data


def fetch_unit(data: Dict) -> str:

    return data['ingredients']['食材']


class BuildDish:

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


class BuildInstruction:

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
    dish_builder = BuildDish(data)
    dish = dish_builder.build()
    print('dish')
    print(dish)

    instruction_builder = BuildInstruction(data)
    instruction = instruction_builder.build()
    print('instruction')
    print(instruction)


if __name__ == '__main__':
    main()
