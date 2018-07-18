
import ast
import sys
import string
import nltk
import re
from nltk.corpus import stopwords
from konlpy.tag import Kkma
sys.path.append('../')
from utility import get_predefined_words
sys.path.append('../dictionary/')
from dictionary.en_ko_dictionary import read_dictionary, read_custom_dictionary

kkma = Kkma()

def english_to_korean(sentence):
    custom_dictionary = read_custom_dictionary()
    google_cloud_dictionary, _ = read_dictionary()
    # tokenize
    words = [word for word in nltk.word_tokenize(sentence.lower()) if word not in string.punctuation or word not in stopwords.words("english")]

    # bigram
    bigrams = [bigram for bigram in zip(words[:-1], words[1:])]
    bigrams = [(' '.join([tup[0], tup[1]]), idx) for idx, tup in enumerate(bigrams)]
    bigrams_found = [bigram for bigram in bigrams if bigram[0] in custom_dictionary]
    bigram_word_idx_tmp = [tup[1] for tup in bigrams_found]
    bigram_word_idx = []
    for idx in bigram_word_idx_tmp:
        bigram_word_idx.append(idx)
        bigram_word_idx.append(idx + 1)
    words_not_in_bigrams = [word for idx, word in enumerate(words) if idx not in bigram_word_idx]

    # custom and google translation
    translated = [custom_dictionary[bigram[0]] for bigram in bigrams_found]
    for unigram in words_not_in_bigrams:
        if unigram in custom_dictionary:
            translated.append(custom_dictionary[unigram])
        elif unigram in google_cloud_dictionary:
            translated.append(google_cloud_dictionary[unigram])
    return translated

def filter_korean(sentence, word2sim, sim2word):
    with open('../dictionary/ko_bigram.txt', 'r') as f:
        ko_bigrams = ast.literal_eval(f.readlines()[0])
    # bigram
    words = [word for word in kkma.nouns(sentence)]
    bigrams = [bigram for bigram in zip(words[:-1], words[1:])]
    bigrams = [(' '.join([tup[0], tup[1]]), idx) for idx, tup in enumerate(bigrams)]
    bigrams_found = [bigram for bigram in bigrams if bigram[0] in ko_bigrams]
    bigram_word_idx_tmp = [tup[1] for tup in bigrams_found]
    bigram_word_idx = []
    for idx in bigram_word_idx_tmp:
        bigram_word_idx.append(idx)
        bigram_word_idx.append(idx + 1)
    words_not_in_bigrams = [word for idx, word in enumerate(words) if idx not in bigram_word_idx]

    tokenized = words_not_in_bigrams + [tup[0] for tup in bigrams_found]
    # similar words
    filtered = []
    for word in tokenized:
        if word in word2sim:
            filtered.append(sim2word[word2sim[word]])
        else:
            filtered.append(word)
    return filtered

def get_attr_vocab():
    # get predefined attribute vocabularies
    attr_files = ['article.txt', 'collar.txt', 'material.txt', 'pattern.txt', 'shape.txt']
    attr = {}
    for file in attr_files:
        with open(file, 'r') as f:
            key = file.split('.')[0]
            attr[key] = []
            for line in f.readlines():
                word = line.strip()
                attr[key].append(word)
    colors = {}
    with open('colors.txt', 'r') as f:
        for line in f.readlines():
            words = line.strip().split(',')
            colors[words[0]] = words
    return attr, colors

def tokenize_by_attr(dirty, word2sim, sim2word, lang='ko'):
    # clean dirty characters
    cleaned = []
    for c in dirty:
        if c not in string.punctuation:
            cleaned.append(c)
        else:
            cleaned.append(' ')
    sentence = ''.join(cleaned).strip()

    # seperate korean and english
    words = [word for word in nltk.word_tokenize(sentence)]
    english = []
    korean = []
    for word in words:
        replaced = re.sub(u'[\u3130-\u318F\uAC00-\uD7A3]+', '', word)
        if len(replaced) != 0:
            english.append(replaced)
        else:
            korean.append(word)
    # _, word2sim, sim2word = get_predefined_words()
    english = english_to_korean(' '.join(english))
    english = filter_korean(' '.join(english), word2sim, sim2word)
    korean = filter_korean(' '.join(korean), word2sim, sim2word)

    sentence = english + korean
    return sentence

if __name__ == "__main__":
    # _, word2sim, sim2word = get_predefined_words()
    dirty_sample = "[handsome]우리집은 orange색 goose down parka를 입습니다."
    tokenize_by_attr(dirty_sample)
    # kor_sample = "우리집은 주홍색 담홍색 구스 다운 파카를 입습니다."
    # kor_sample2 = "네이비 데님 자켓"
    # filter_korean(kor_sample, word2sim, sim2word)
    # filter_korean(kor_sample2, word2sim, sim2word)
