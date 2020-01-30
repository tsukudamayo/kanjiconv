import os
import re
import json
import subprocess
from functools import reduce
from typing import Iterator, Dict, Any
import jaconv
from collections import OrderedDict


_KBM_MODEL = 'kytea-0.4.7/model/jp-0.4.7-1.mod'
_KNM_MODEL = 'kytea-0.4.7/RecipeNE-sample/recipe416.knm'
_KYTEA_PATH = 'kytea'


config = {
    "recipeId": "null",
    "title": "",
    "kana": "",
    "subTitle": "",
    "description": "",
    "dishType": "",
    "cookingMethod": [],
    "recipeGenre": "",
    "foodType": "",
    "video": "",
    "defaultServing": {},
    "recipeSeason": {
    },
    "notes": "",
    "images": {
        "main": "",
    },
    "introductoryEssay": "",
    "description": "",
    "outOfSeasonFlag": 0,
    "content": {
        "dishServings": {
            "unit": {},
            "dishes": {
                "title": "",
                "cookingTool": "",
                "nutrition": {
                    "note": "",
                    "salt": 0.0,
                    "protein": 0.0,
                    "calories": 0,
                    "lipid": 0.0,
                    "carbohydrate": 0.0,
                },
                "ingredients": [],
            },
        },
        "instructionServings": {
            "unit": {},
            "instructions": [],
        },
    },

}


def fetch_subdict(key: str, dic: dict) -> Iterator[Dict[str, Dict[Any, Any]]]:
    for _key, _value in dic.items():
        if isinstance(_value, dict):
            yield from fetch_subdict(key, _value)
        yield {key: {_key: _value}}

def fetch_nest_dict(dic: dict) -> Iterator[Dict[Any, Any]]:
    for key, value in dic.items():
        if isinstance(value, dict):
            yield from fetch_subdict(key, value)
            continue
        yield {key: value}


def inject_instruction(idx: int, strings: str) -> dict:
    """ instruction """
    instruction = {
        "step": 0,
        "description": "",
        "classification": "",
        "note": "",
        "images": {
            "main": "",
        },
        "video": "",
    }
    
    instruction['step'] = idx
    instruction['description'] = strings

    return instruction



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


class JsonBuilder:

    def __init__(self, config, filepath):
        self.config = config
        self.filepath = filepath
        self._ingredients_state = 1
        self._item_state = ''
        self.tmp_keyword = ''
        self.ingredients = {
                "description": "",
                "quantityText": "",
                "ingredientId": 0,
                "classificationId": 0,
                "intermediateId": 0,
                "items": [],
        }
        self.nest_ingredients = {
                "description": "",
                "quantityText": "",
                "ingredientId": 0,
                "classificationId": 0,
                "intermediateId": 0,
                "ingredientId": 0,
                "classificationId": 0,
                "intermediateId": 0,
         }

    @property
    def ingredients_state(self):
        return self._ingredients_state

    @ingredients_state.setter
    def ingredients_state(self, state):
        if self._ingredients_state != state:
            self._ingredients_state = state
            self.change_item(state)

    @property
    def item_state(self):
        return self._item_state

    @item_state.setter
    def item_state(self, state):
        print('itemstate:', state)
        if self._item_state != state:
            self._item_state = state
            # self.change_item(state)

    def change_item(self, state):
        if state == 0:
            self.ingredients = {
                "description": "",
                "quantityText": "",
                "ingredientId": 0,
                "classificationId": 0,
                "intermediateId": 0,
                "items": [],
            }
            nest_ingredients = {
                "description": "",
                "quantityText": "",
                "ingredientId": 0,
                "classificationId": 0,
                "intermediateId": 0,
                "ingredientId": 0,
                "classificationId": 0,
                "intermediateId": 0,
            }
        else:
            self.ingredients = {
                "description": "",
                "quantityText": "",
                "ingredientId": 0,
                "classificationId": 0,
                "intermediateId": 0,
                "ingredientId": 0,
                "classificationId": 0,
                "intermediateId": 0,
            }
        print(self.ingredients)

    def build(self):
        self.load_json()
        self.fetch_title()
        self.convert_kana()
        self.parse_unit()
        self.build_instruction()
        self.build_ingredients()

        return self.config
        
    def load_json(self):
        with open(self.filepath, 'r', encoding='utf-8') as r:
            self.data = json.load(r)

        return

    def fetch_title(self):
        """ title """
        title = self.data['title']
        self.config['title'] = title
        self.config['content']['dishServings']['dishes']['title'] = title

        return

    def convert_kana(self):
        """ kana """
        result = morphological_analysis(self.config['title'], _KBM_MODEL, _KYTEA_PATH)
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
        self.config['kana'] = zenkaku

        return

    def parse_unit(self):
        """ unit """
        unit_strings = self.data['ingredients']['食材']
        temporal_unit = '人分'
        unit = {unit_strings.split(temporal_unit)[0]: temporal_unit}
        self.config['content']['dishServings']['unit'] = unit
        self.config['content']['instructionServings']['unit'] = unit

        return

    def build_instruction(self):
        split_recipe = self.data['recipe'].split('\n')
        print(split_recipe)
        null_check = [s for s in split_recipe if s]
        print(null_check)
        instructions = []
        for i, s in enumerate(null_check):
            tmp_instruction = inject_instruction(i+1, s)
            instructions.append(tmp_instruction)
        
        print('instructions')
        print(instructions)
        
        self.config['content']['instructionServings']['instructions'] = instructions

        return

    def inject_ingredient(self, dic: dict) -> dict:

        print('inject_ingredient/dic', dic)
        for key, value in dic.items():

            if isinstance(value, dict):
                self.ingredients_state = 0
            else:
                self.ingredients_state = 1
            
            print('ingredients_state')
            state = self._ingredients_state
            print(state)

            self.item_state = key

            if state == 0:
                ingredients = {
                    "description": "",
                    "quantityText": "",
                    "ingredientId": 0,
                    "classificationId": 0,
                    "intermediateId": 0,
                    "items": [],
                }
                
                # ingredients["description"] = key
                self.nest_ingredients = {
                    "description": "",
                    "quantityText": "",
                    "ingredientId": 0,
                    "classificationId": 0,
                    "intermediateId": 0,
                    "ingredientId": 0,
                    "classificationId": 0,
                    "intermediateId": 0,
                }
                
                self.nest_ingredients['description'] = key
                self.nest_ingredients['quantityText'] = value
                self.ingredients["description"] = key
                
                print('inject_ingredient')
                print(self.ingredients)
                print('inject_ingredient')
                print(self.nest_ingredients)
                print('return')
                print('****************')
                print(self.ingredients)
                print('****************')
                self.tmp_keyword = key
                self.ingredients["items"].append(self.nest_ingredients)
            
            elif state == 1:
                self.ingredients = {
                    "description": "",
                    "quantityText": "",
                    "ingredientId": 0,
                    "classificationId": 0,
                    "intermediateId": 0,
                    "ingredientId": 0,
                    "classificationId": 0,
                    "intermediateId": 0,
                }
            
                self.ingredients["description"] = key
                self.ingredients["quantityText"] = value
                self.tmp_keyword = key

        


        return self.ingredients

    
    def build_ingredients(self):
        """ ingredients """
        ingredients = self.data['ingredients']
        print('ingredients')
        print(ingredients)
        ingredients.pop('食材')
        for k, v in ingredients.items():
            print(k)
            print(v)
        
        print('fetch_nest_dict')
        print(list(fetch_nest_dict(ingredients)))
        ingredients_list = []
        # ingredients_list = [self.inject_ingredient(f) for f in list(fetch_nest_dict(ingredients))]
        for f in list(fetch_nest_dict(ingredients)):
            print('f')
            print(f)
            result = self.inject_ingredient(f)
            print('result')
            print(result)
            ingredients_list.append(result)
        print('ingredients_list')
        print(ingredients_list)
        self.config['content']['dishServings']['dishes']['ingredients']= ingredients_list

        return


def main():
    filepath = os.path.join('data/betterhome_recipe', '10100005.json')
    builder = JsonBuilder(config, filepath)
    result = builder.build()

    print("{}".format(json.dumps(result, indent=4, ensure_ascii=False)))
    with open('config.json', 'w', encoding='utf-8') as ww:
        json.dump(result, ww, indent=4, ensure_ascii=False)

    print('result')
    print(result)


if __name__ == '__main__':
    main()
