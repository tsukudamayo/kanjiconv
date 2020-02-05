from nest_ingredient_sample import parse_ingredients


def test_parse_ingredients_nest2():
    expected = [
        {
            "description": "Ａ",
            "quantityText": None
        },
        {
           "items": [
                 {
                   "description": "だし",
                   "quantityText": "カップ１／３"
                 },
                 {
                   "description": "酒",
                   "quantityText": "大さじ１／２"
                 },
                 {
                   "description": "しょうゆ",
                   "quantityText": "小さじ１"
                 },
                 {
                   "description": "塩",
                   "quantityText": "少々"
                 }
             ]
        }
    ]


    test_data = {
        "Ａ": {
            "だし": "カップ１／３",
            "酒": "大さじ１／２",
            "しょうゆ": "小さじ１",
            "塩": "少々"
        }
    }

    result = parse_ingredients(test_data)
    print('****************************************************************')
    print(result)
    print('****************************************************************')

    assert result == expected


def test_parse_ingredients_normal():
    test_data_2 = {
        "うずら豆": "カップ２（３００ｇ）",
        "砂糖": "９０ｇ",
        "塩": "小さじ１／５"
    }

    expected = [
                {
                    "description": "うずら豆",
                    "quantityText": "カップ２（３００ｇ）"
                },
                {
                    "description": "砂糖",
                    "quantityText": "９０ｇ"
                },
                {
                    "description": "塩",
                    "quantityText": "小さじ１／５"
                }
    ]

    result = parse_ingredients(test_data_2)
    print('result')
    print(result)

    assert result == expected
                
