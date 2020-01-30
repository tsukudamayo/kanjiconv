import json
from collections import OrderedDict
from preprocess_web_recipe import load_json
from preprocess_web_recipe import fetch_ingredients
from preprocess_web_recipe import fetch_instruction
from preprocess_web_recipe import fetch_title
from preprocess_web_recipe import build_dishes
from preprocess_web_recipe import fetch_unit


def test_load_json():
    expected = {
        "a": "あ",
        "b": "い",
        "c": {
            "d": "う",
            "e": "え",
        },
    }

    test_data = './test_data/sample_test_json.json'
    result = load_json(test_data)

    assert result == expected


def test_fetch_ingredients():
    expected = [
                OrderedDict([
                             ("description", "しゅんぎく"),
                             ("quantityText", "２００ｇ"),
                             ("ingredientId", 0),
                             ("classificationId", 0),
                             ("intermediateId", 0)
                             ]),
                OrderedDict([
                             ("description", "菊の花（食用）"),
                             ("quantityText", "５０ｇ"),
                             ("ingredientId", 0),
                             ("classificationId", 0),
                             ("intermediateId", 0)
                             ]),
                OrderedDict([
                            ("description", "酢"),
                            ("quantityText", "大さじ１"),
                            ("ingredientId", 0),
                            ("classificationId", 0),
                            ("intermediateId", 0)
                            ]),
                OrderedDict([
                            ("description", "しょうゆ"),
                            ("quantityText", "大さじ１／２"),
                            ("ingredientId", 0),
                            ("classificationId", 0),
                            ("intermediateId", 0)
                            ]),
                OrderedDict([
                            ("description", "だし"),
                            ("quantityText", "大さじ１"),
                            ("ingredientId", 0),
                            ("classificationId", 0),
                            ("intermediateId", 0)
                            ]),
    ]
    test_data = './test_data/10100006.json'
    data = load_json(test_data)
    result = fetch_ingredients(data)

    assert result == expected

    
def test_fetch_instruction():
    expected = [
                {
                    "steps": 1,
                    "description": "しゅんぎくは、茎のかたいところはとり除き、洗います。",
                },
                {
                    "steps": 2,
                    "description": "熱湯で３０秒ほどゆで、すぐ水にとってさまし、手早く水気をしぼって、４ｃｍ長さに切ります。",
                },
                {
                    "steps": 3,
                    "description": "菊の花は、花びらをむしります。",
                },
                {
                    "steps": 4,
                    "description": "水カップ３をわかして酢を入れ、菊の花びらを約２０秒ゆでます。水にとってさらし、水気をしっかりしぼります。",
                },
                {
                    "steps": 5,
                    "description": "しょうゆとだしを合わせます（割りじょうゆ）。",
                },
                {
                    "steps": 6,
                    "description": "しゅんぎくと菊の花をほぐして混ぜ、割りじょうゆをかけます。",
                },
                
               ]
                
    
    test_data = './test_data/10100006.json'
    data = load_json(test_data)
    result = fetch_instruction(data)

    assert result == expected


def test_fetch_title():
    expected = "しゅんぎくと菊の花のおひたし"
    test_data = './test_data/10100006.json'
    data = load_json(test_data)
    result = fetch_title(data)

    assert result == expected


def test_build_dishes():
     expected = {
         "title": "しゅんぎくと菊の花のおひたし",
         "cookingTool": "",
         "nutrition": [
                       {"note": ""},
                       {"salt": 0.0},
                       {"protein": 0.0},
                       {"calory": 15},
                       {"lipid": 0.0},
                       {"carbohydrate": 0.0},
                      ],
         "ingredients": [
                OrderedDict([
                             ("description", "しゅんぎく"),
                             ("quantityText", "２００ｇ"),
                             ("ingredientId", 0),
                             ("classificationId", 0),
                             ("intermediateId", 0)
                             ]),
                OrderedDict([
                             ("description", "菊の花（食用）"),
                             ("quantityText", "５０ｇ"),
                             ("ingredientId", 0),
                             ("classificationId", 0),
                             ("intermediateId", 0)
                             ]),
                OrderedDict([
                            ("description", "酢"),
                            ("quantityText", "大さじ１"),
                            ("ingredientId", 0),
                            ("classificationId", 0),
                            ("intermediateId", 0)
                            ]),
                OrderedDict([
                            ("description", "しょうゆ"),
                            ("quantityText", "大さじ１／２"),
                            ("ingredientId", 0),
                            ("classificationId", 0),
                            ("intermediateId", 0)
                            ]),
                OrderedDict([
                            ("description", "だし"),
                            ("quantityText", "大さじ１"),
                            ("ingredientId", 0),
                            ("classificationId", 0),
                            ("intermediateId", 0)
                            ]),
               ],
     }

     test_data = './test_data/10100006.json'
     data = load_json(test_data)
     title = fetch_title(data)
     ingredients = fetch_ingredients(data)
     result = build_dishes(title, ingredients)

     assert result == expected


def test_fetch_units():
    expected = "4人分"

    test_data = './test_data/10100006.json'
    data = load_json(test_data)
    result = fetch_unit(data)

    assert result == expected
