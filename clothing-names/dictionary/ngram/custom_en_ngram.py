import ast
import sys
import string
import nltk
from collections import Counter
from nltk.corpus import stopwords
sys.path.append('../')
from en_ko_dictionary import update_dictionary
data_dir = '../../data/'
files = ['ssense_results_combined.txt']
stop = set(stopwords.words('english'))

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

unigrams = [unigram for sent in sentences for unigram in sent if unigram not in stop]
update_dictionary(unigrams)
unigrams = Counter(unigrams).most_common()
with open('./en_unigram_count.txt', 'w') as f:
    for k,v in unigrams:
        f.write('{} :\t{}\n'.format(k,v))
# # bigram
# bigrams = [bigram for sent in sentences for bigram in zip(sent[:-1], sent[1:])]
#
# # trigram
# trigrams = [trigram for sent in sentences for trigram in zip(sent[:-2], sent[1:-1], sent[2:])]
#
# bigrams = Counter(bigrams).most_common()
# trigrams = Counter(trigrams).most_common()
#
# with open('./en_bigram_count.txt', 'w') as f:
#     for k,v in bigrams:
#         f.write('{} :\t{}\n'.format(k,v))
#
# with open('./en_trigram_count.txt', 'w') as f:
#     for k,v in trigrams:
#         f.write('{} :\t{}\n'.format(k,v))
