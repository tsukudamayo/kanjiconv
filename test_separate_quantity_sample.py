from separate_quantity_sample import separate_quantity
from separate_quantity_sample import candidate_border


def test_separate_quantity():

    test_data = {
        "description": "うずら豆",
        "quantityText": "カップ2(300g)"
    }

    expected = ['カップ', '2', '(', '300', 'g)']

    test_strings = test_data['quantityText']
    border = candidate_border(test_strings)
    result = list(separate_quantity(test_strings, border))

    assert result == expected
