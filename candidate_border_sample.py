import re


def candidate_border(strings: str) -> int:
    print('strings')
    print(strings)

    if strings == '':
        return False
    else:
        # fraction_pattern = re.compile('[0-9]{1,}/[0-9]{1,}')  # Fractions are treated as exceptions.
        # match = re.match(fraction_pattern, strings)
        flg = strings[0].isdecimal()
        tmp_flg = strings[0].isdecimal()
        change_flg = False

        for idx, t in enumerate(strings):
            print('t : ', t)
            border = idx
            tmp_flg = strings[idx].isdecimal()
            print('flg : tmp_flg', flg, tmp_flg)
            print('flg != tmp_flg: ', flg != tmp_flg)
            # if match:
            #     continue
            if t == '/':  # Fractions are treated as exceptions.
                continue
            if flg != tmp_flg:
                change_flg = True
                print('change')
                print('border : ', border)
                return border

        # if change_flg is True:
        #     print('change_flg is True')
        #     print('border : ', border)
        #     return border
        # else:
        #     print('change_flg is False')
        #     return False
