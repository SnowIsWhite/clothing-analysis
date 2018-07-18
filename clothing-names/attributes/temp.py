import ast
import sys
import string
from nltk.corpus import stopwords
from konlpy.tag import Kkma
sys.path.append('../')
from utility import get_predefined_words, get_category_words, filter_string
sys.path.append('../dictionary/')
from dictionary.en_ko_dictionary import update_dictionary, read_dictionary

files = ['handsome_result.txt']
data_dir = '../data/'
attr_files = ['article.txt', 'collar.txt', 'colors.txt', 'material.txt', 'pattern.txt', 'shape.txt']
stopwords, word2sim, sim2word = get_predefined_words()
cat2word, word2cat = get_category_words()

prod2words = {}
kkma = Kkma()
eng2kor, kor2eng = read_dictionary()
for file in files:
    mall = file.split('_')[0]
    with open(data_dir + file, 'r') as f:
        for line in f.readlines():
            line = ast.literal_eval(line.strip())
            for color in line['color']:
                c, eng2kor = filter_string(color, eng2kor)
                print(c)
