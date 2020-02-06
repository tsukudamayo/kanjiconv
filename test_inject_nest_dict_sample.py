from inject_nest_dict_sample import inject_dict


def test_inject_dict():
    expected = [
        {"description": "a", "quantityText": "1"},
        {"description": "a", "quantityText": "2"},
        {"description": "a", "quantityText": "3"},
        {"description": "a", "quantityText": "4"},
        {"description": "a", "quantityText": "5"}
    ]
    test_data = [
        {"description": "a", "quantityText": "5"},
        {"description": "a", "quantityText": "5"},
        {"description": "a", "quantityText": "5"},
        {"description": "a", "quantityText": "5"},
        {"description": "a", "quantityText": "5"}
    ]
    params = ["1", "2", "3", "4", "5"]

    result = list(inject_dict(test_data, params))

    assert result == expected


def test_inject_nest_dict():
    expected = [
        {"description": "a", "quantityText": "1"},
        {"description": "b", "quqntityText": None},
        {"items": [
                   {"description": "a", "quantityText": "2"},
                   {"description": "a", "quantityText": "3"},
                   {"description": "a", "quantityText": "4"},
                   {"description": "a", "quantityText": "5"}
                   ]
        }
    ]
    test_data = [
        {"description": "a", "quantityText": "5"},
        {"description": "b", "quqntityText": None},
        {"items": [
                   {"description": "a", "quantityText": "5"},
                   {"description": "a", "quantityText": "5"},
                   {"description": "a", "quantityText": "5"},
                   {"description": "a", "quantityText": "5"}
                   ]
        }
    ]
    params = ["1", None, "2", "3", "4", "5"]

    print('**************** result ****************')
    result = list(inject_dict(test_data, params))
    print(result)

    assert result == expected
