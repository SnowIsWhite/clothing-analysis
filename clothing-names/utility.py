import json
import ast
import re
import sys
from konlpy.tag import Kkma
from konlpy.utils import pprint
from soynlp.word import WordExtractor
sys.path.append('dictionary/')
from dictionary.en_ko_dictionary import update_dictionary, read_dictionary

words_path = '/Users/jaeickbae/Documents/projects/data_analysis/brands/clothing-names/analysis/'
folder_path = '/Users/jaeickbae/Documents/projects/data_analysis/brands/clothing-names/data/'
# files = ['handsome_result.txt', 'sivillage_result.txt', 'ssf_result.txt', 'musinsa_result.txt']
files = ['musinsa_result.txt']
def get_text_data(type):
    # tc: title, category
    # tcd: title, category, description

    result = {}
    for file in files:
        with open(folder_path + file, 'r') as f:
            for line in f.readlines():
                l = ast.literal_eval(line)
                if type == 'tc':
                    if l['category'] not in result:
                        result[l['category']] = [l['name']]
                    else:
                        result[l['category']].append(l['name'])
                if type == 'tcd':
                    if 'prod_desc' in l:
                        if l['category'] not in result:
                            result[l['category']] = [{'name': l['name'], 'desc': l['prod_desc']}]
                        else:
                            result[l['category']].append({'name': l['name'], 'desc': l['prod_desc']})
                    else:
                        if l['category'] not in result:
                            result[l['category']] = [{'name': l['name'], 'desc': ''}]
                        else:
                            result[l['category']].append({'name': l['name'], 'desc': ''})
    return result

def get_predefined_words():
    stopwords = []
    with open(words_path+'stopwords.txt', 'r') as f:
        for line in f.readlines():
            stopwords.append(line.strip())

    colorwords = []
    with open(words_path+'clothing-colors.txt', 'r') as f:
        for line in f.readlines():
            colorwords.append(line.strip())

    word2sim = {}
    sim2word = {}
    with open(words_path+'similar-words.txt', 'r') as f:
        cnt = 1
        for line in f.readlines():
            words = line.split(',')
            for idx, word in enumerate(words):
                if idx == 0:
                    sim2word[cnt] = word
                word = word.strip()
                word2sim[word] = cnt
            cnt += 1
    return stopwords, colorwords, word2sim, sim2word

def get_category_words():
    word2cat = {}
    cat2word = {}
    with open(words_path+'category-words.txt', 'r') as f:
        cnt = 1
        for line in f.readlines():
            words = line.split(',')
            for idx, word in enumerate(words):
                if idx == 0:
                    cat2word[cnt] = word
                word = word.strip()
                word2cat[word] = cnt
            cnt += 1
    return cat2word, word2cat

def filter_string(string, eng2kor):
    stopwords, colorwords, word2sim, sim2word = get_predefined_words()
    filtered = []
    string = string.replace('(', ' ')
    string = string.replace(')', ' ')
    string = string.replace('[', ' ')
    string = string.replace(']', ' ')
    string = string.replace('-', ' ')
    string = string.replace('_', ' ')
    string = string.replace('/', '')
    string = string.replace('}', ' ')
    string = string.replace('{', ' ')
    # ns = string.split()
    ns = [string]
    for n in ns:
        if re.match('[a-zA-Z]+[0-9]+', n) or re.match('[0-9]+[a-zA-Z]+', n):
            continue
        # detect english and translate (not korean)
        if len(re.findall(u'[\u3130-\u318F\uAC00-\uD7A3]+', n)) == 0:
            n = n.lower()
            n = n.replace('"', '')
            n = n.replace('&quot;', '')
            if n not in eng2kor:
                update_dictionary([n])
                eng2kor, _ = read_dictionary()
            n = eng2kor[n]
        # change to standard word
        if n in word2sim:
            n = sim2word[word2sim[n]]
        # remove if stop word
        # if n in stopwords:
        #     continue
        # if n in colorwords:
        #     continue
        filtered.append(n)
    return filtered, eng2kor

def tokenize(type):
    eng2kor, kor2eng = read_dictionary()
    cat2word, word2cat = get_category_words()
    if type == 'tc':
        data = get_text_data('tc')
        list_of_words = []
        target_category = '신발'
        cats = []
        for w in word2cat:
            if word2cat[w] == word2cat[target_category]:
                cats.append(w)

        for c in data:
            for cat in cats:
                if cat == c:
                    print(c)
                    for name in data[c]:
                        words = []
                        filtered, eng2kor = filter_string(name, eng2kor)
                        words += filtered
                        list_of_words.append(words)
    return list_of_words
# if __name__ == "__main__":
#     res = get_text_data('tc')
#     for cat in res:
#         print(cat)
#     # tokenize('tc')
