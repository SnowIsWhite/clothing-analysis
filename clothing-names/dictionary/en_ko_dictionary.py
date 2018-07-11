import ast
from google.cloud import translate

client = translate.Client()
dictionary_dir = '/Users/jaeickbae/Documents/projects/data_analysis/brands\
/clothing-names/dictionary/dictionary.txt'

# read existing dictionary
def read_dictionary():
    eng2kor = {}
    kor2eng = {}
    with open(dictionary_dir, 'r') as f:
        for idx, line in enumerate(f.readlines()):
            if idx == 0:
                eng2kor = ast.literal_eval(line)
            else:
                kor2eng = ast.literal_eval(line)
    return eng2kor, kor2eng

# update new word
def update_dictionary(words):
    eng2kor, kor2eng = read_dictionary()
    for word in words:
        if word not in eng2kor:
            if word == 'navy' or word == 'Navy':
                eng2kor[word] = '네이비'
                kor2eng['네이비'] = word
                continue
            if word == 'sweat' or word == 'Sweat':
                eng2kor[word] = '스웨트'
                kor2eng['스웨트'] = word
            translated_result = client.translate(word, target_language='ko')
            eng2kor[word] = translated_result['translatedText']
            kor2eng[translated_result['translatedText']] = word
    write_dictionary_to_file(eng2kor, kor2eng)

# write dictionary
def write_dictionary_to_file(eng2kor, kor2eng):
    with open(dictionary_dir, 'w') as f:
        f.write('{')
        for idx, key in enumerate(eng2kor):
            if idx != 0:
                f.write(',')
            f.write('"' + key + '":"' + eng2kor[key] + '"' )
        f.write('}\n')

        f.write('{')
        for idx, key in enumerate(kor2eng):
            if idx != 0:
                f.write(',')
            f.write('"' + key + '":"' + kor2eng[key] + '"' )
        f.write('}')
