import ast
import string
import nltk
from collections import Counter
data_dir = '../../data/'
files = ['handsome_result.txt', 'sivillage_result.txt', 'ssf_result.txt']

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

# bigram
bigrams = [bigram for sent in sentences for bigram in zip(sent[:-1], sent[1:])]

# trigram
trigrams = [trigram for sent in sentences for trigram in zip(sent[:-2], sent[1:-1], sent[2:])]

bigrams = Counter(bigrams).most_common()
trigrams = Counter(trigrams).most_common()

with open('./ko_bigram_count.txt', 'w') as f:
    for k,v in bigrams:
        f.write('{} :\t{}\n'.format(k,v))

with open('./ko_trigram_count.txt', 'w') as f:
    for k,v in trigrams:
        f.write('{} :\t{}\n'.format(k,v))
