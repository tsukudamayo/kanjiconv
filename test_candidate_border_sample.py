from candidate_border_sample import candidate_border


def test_candidate_border():
    expected = ''

    result = candidate_border('1/5枚')
    print('result')
    print(result)

    assert result == expected
