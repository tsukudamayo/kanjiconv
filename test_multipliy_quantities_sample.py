from preprocess_web_recipe import load_json
from preprocess_web_recipe import Dish
from build_multiply_quantities_sample import Multiplier

from operation import normalize_quantity
from operation import multiply_quantity



def test_inject_dict():
    expected = [
                {
                    "description": "枝豆（さやつき）",
                    "quantityText": "１５０ｇ（正味７５ｇ）"
                },
                {
                    "description": "枝豆（さやつき）３００ｇ（正味１５０ｇ）",
                    "quantityText": None
                },
                {
                    "items": [
                        {
                            "description": "砂糖",
                            "quantityText": "大さじ１／２弱"
                        },
                        {
                            "description": "塩",
                            "quantityText": "小さじ１／１２"
                        },
                        {
                            "description": "だし",
                            "quantityText": "大さじ１"
                        }
                    ]
                },
                {
                    "description": "干ししいたけ",
                    "quantityText": "１／２枚"
                },
                {
                    "description": "にんじん",
                    "quantityText": "１５ｇ"
                },
                {
                    "description": "こんにゃく（白）",
                    "quantityText": "１／１０枚"
                },
                {
                    "description": "Ａ",
                    "quantityText": None
                },
                {
                    "items": [
                        {
                            "description": "だし",
                            "quantityText": "カップ１／６"
                        },
                        {
                            "description": "酒",
                            "quantityText": "大さじ１／４"
                        },
                        {
                            "description": "しょうゆ",
                            "quantityText": "小さじ１／２"
                        },
                        {
                            "description": "塩",
                            "quantityText": "少々"
                        }
                    ]
                }
            ]

    test_file = './test_data/10100002.json'
    data = load_json(test_file)
    dish_builder = Dish(data)
    dish = dish_builder.build()
    norm = normalize_quantity(dish, 4)
    params = multiply_quantity(dish, norm, 2)
    multi = Multiplier(dish, params)
    result = multi.build()
    print('result')
    print(result)

    assert result == expected
