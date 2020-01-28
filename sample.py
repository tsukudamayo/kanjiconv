import os
import re
import json
import subprocess
from functools import reduce
import jaconv



_KBM_MODEL = 'kytea-0.4.7/model/jp-0.4.7-1.mod'
_KNM_MODEL = 'kytea-0.4.7/RecipeNE-sample/recipe416.knm'
_KYTEA_PATH = 'kytea'


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


def main():
    print('hello')
    file_list = os.listdir('data/betterhome_recipe')
    first_file = os.listdir('data/betterhome_recipe')[1]
    print(first_file)
    first_file_path = os.path.join('data/betterhome_recipe', '10100001.json')
    with open(first_file_path, 'r', encoding='utf-8') as r:
        data = json.load(r)
    print(data)
    title = data['title']
    result = morphological_analysis(title, _KBM_MODEL, _KYTEA_PATH)

    result_strings = result.split(' ')
    print(result_strings)
    target_array = [s.split('/')[2] for s in result_strings]
    print(target_array)
    join_strings = ''.join(target_array)
    print(join_strings)
    print(type(join_strings))

    regex = re.compile('[\u3041-\u309F]+')
    process_strings = regex.findall(join_strings)
    print(process_strings)

    hiragana = ''.join(process_strings)
    print(hiragana)
    katakana = jaconv.hira2kata(hiragana)
    print(katakana)
    

if __name__ == '__main__':
    main()
