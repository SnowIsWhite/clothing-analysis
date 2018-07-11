import nltk
import string
import ast
from collections import Counter
from gensim.models.phrases import Phraser
from gensim.models.phrases import Phrases
from gensim.models import Word2Vec
from nltk.corpus import stopwords


files = ['ssense_result.txt']
data_dir = '../data/'
sentences = []
for file in files:
    with open(data_dir + file, 'r') as f:
        for line in f.readlines():
            l = ast.literal_eval(line)
            sentence = [word for word in nltk.word_tokenize(l['name'].lower()) if word not in string.punctuation]
            sentences.append(sentence)
            tmps = [sent for sent in l['prod_desc'].split('.') if len(sent) != 0]
            for sent in tmps:
                sentence = [word for word in nltk.word_tokenize(sent.lower()) if word not in string.punctuation]
                sentences.append(sentence)
phrases = Phrases(sentences)
bigram = Phraser(phrases)


bigram_list = []
for line in list(bigram[sentences]):
    for word in line:
        if word not in stopwords.words("english"):
            ws = word.split('_')
            if len(ws) > 1:
                bigram_list.append(word)

bigram_counter = Counter(bigram_list)
print(bigram_counter)
