from preprocess_web_recipe import load_json
from preprocess_web_recipe import Dish
from preprocess_web_recipe import Instruction
from operation import normalize_quantity
from operation import value_to_hankaku
from operation import dict_to_hankaku
from operation import multiply_quantity
from operation import build_mulitply_quantities


def load_test_data():
    test_data = './test_data/10100006.json'
    data = load_json(test_data)
    instance = Dish(data)
    dish = instance.build()

    return dish


def test_noramlize():
    expected ={
        "しゅんぎく": "50ｇ",
        "菊の花（食用）": "12.5ｇ",
        "酢": "大さじ1/4",
        "しょうゆ": "大さじ1/8",
        "だし": "大さじ1/4"
    }

    dish = load_test_data()
    ingredients = dish['ingredients']
    result = normalize_quantity(dish, 4)
    print('result')
    print(result)

    assert result == expected
def test_value_to_hankaku():
    expected = '大さじ1/2'
    dish = load_test_data()
    ingredients = dish['ingredients']
    first = ingredients[3]
    print(first['quantityText'])

    result = value_to_hankaku(first['quantityText'])
    print(result)

    assert result == expected


def test_dict_to_hankaku():
    dish = load_test_data()
    expected = {
        "description": "しょうゆ",
        "quantityText": "大さじ1/2",
        "ingredientId": 0,
        "classificationId": 0,
        "intermediateId": 0
    }
    test_data = {
        "description": "しょうゆ",
        "quantityText": "大さじ１／２",
        "ingredientId": 0,
        "classificationId": 0,
        "intermediateId": 0
    }

    result = dict_to_hankaku(test_data)
    print('result')
    print(result)

    assert result == expected
    
    
def test_multiply_quantity():
    expected ={
        "しゅんぎく": "50ｇ",
        "菊の花（食用）": "12.5ｇ",
        "酢": "大さじ1/4",
        "しょうゆ": "大さじ1/8",
        "だし": "大さじ1/4"
    }
    data = load_test_data()
    params = normalize_quantity(data, 4)
    # separate, quantity, output, params = multiply_quantity(data, params, 2)

    result = multiply_quantity(data, params, 2)
    print('****************')
    # print('multiply')
    # print('separate')
    # print(separate)
    # print('quantity')
    # print(quantity)
    # print('output')
    # print(output)
    # print('params')
    # print(params)
    print('result')
    print(result)
    print('****************')
    assert expected == result


def test_build_multiply_quantities():
    expected = ['100g', '25g', '大さじ1/2', '大さじ1/4', '大さじ1/2']
    dish = load_test_data()
    norm = normalize_quantity(dish, 4)
    params = multiply_quantity(dish, norm, 2)
    result = build_mulitply_quantities(dish, params)
    # str_multi = conv_num_str(multi)
    # join_multi = join_num_str(multi)
    print('result join_num_str')
    print(result)

    assert result == expected

    
# def test_build_multiply_quantities():
#     expected = {
#         "しゅんぎく": "100ｇ",
#         "菊の花（食用）": "25ｇ",
#         "酢": "大さじ1/2",
#         "しょうゆ": "大さじ1/4",
#         "だし": "大さじ1/2"
#     }
     
#     dish = load_test_data()
#     norm = normalize_quantity(dish, 4)
#     multi = build_mulitply_quantities(dish, norm)
#     params = multiply_quantity(dish, multi, 2)
#     result = build_mulitply_quantities(dish, params)
#     print('result')
#     print(result)

#     assert result == expected    
