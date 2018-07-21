import ast
import sys
import os
sys.path.append('../')
sys.path.append('../attributes/')
sys.path.append('../dictionary/')
from tokenize_by_attr import tokenize_by_attr, get_attr_vocab
from utility import get_predefined_words
from dictionary.en_ko_dictionary import read_dictionary, read_custom_dictionary

file_dir = '../data/'
target_file = 'ssense_results_combined'

def getToyData(target_file):
    fname = '{}_vectors.txt'.format(target_file)
    if not os.path.exists(fname):
        attrIndicies, prodids, prodVectors = __constructToyData__(target_file)
    else:
        attrIndicies, prodids, prodVectors = __readToyData__(fname)
    return attrIndicies, prodids, prodVectors

def __constructToyData__(target_file):
    file = file_dir + target_file + '.txt'
    lenA, attrIndicies = __getAttributeInfo__()
    prodids, wordsProd = __getIdsAndWords__(file)
    prodVectors = __constructVectors__(lenA, attrIndicies, wordsProd)
    __writeToyData__(target_file, attrIndicies, prodids, prodVectors)
    return attrIndicies, prodids, prodVectors

def __getIdsAndWords__(file):
    imgids, wordsImg = [], []
    data = __readData__(file)
    custom_dictionary, google_cloud_dictionary = __prepareDictionary__()
    word2sim, sim2word = __prepareSimilarWords__()
    attr, colors = __prepareAttrData__()
    for line in data:
        wordsInStandard = __sentence2Words__(line, word2sim, sim2word, custom_dictionary, google_cloud_dictionary, attr, colors)
        if len(wordsInStandard) != 0:
            imgids.append(line['prod_num'])
            wordsImg.append(wordsInStandard)
    return imgids, wordsImg

def __readData__(file):
    with open(file, 'r') as f:
        data = [ast.literal_eval(line.strip()) for line in f.readlines()]
    return data

def __prepareDictionary__():
    custom_dictionary = read_custom_dictionary()
    google_cloud_dictionary = read_dictionary()
    return custom_dictionary, google_cloud_dictionary

def __prepareAttrData__():
    attr, colors = get_attr_vocab()
    return attr, colors

def __prepareSimilarWords__():
    _, word2sim, sim2word = get_predefined_words()
    return word2sim, sim2word

def __sentence2Words__(line, word2sim, sim2word, custom_dictionary, google_cloud_dictionary, attr, colors):
    sentences = __getNeccessarySentences__(line)
    tokenizedWords = []
    for s in sentences:
        tokenizedWords += tokenize_by_attr(s, word2sim, sim2word, custom_dictionary, google_cloud_dictionary)
    wordsInStandard = __checkWordsInAttribute__(tokenizedWords, attr, colors)
    return wordsInStandard

def __getNeccessarySentences__(line):
    sentences = []
    if len(line['category']) != 0:
        sentences.append(line['category'])
    if len(line['name']) != 0:
        sentences.append(line['name'])
    if len(line['prod_desc']) != 0:
        sentences.append(line['prod_desc'])
    return sentences

def __checkWordsInAttribute__(words, attr, colors):
    wordsInStandard = []
    for word in words:
        if word in attr['article'] or word in attr['collar'] or word in attr['material'] or word in attr['pattern'] or word in attr['shape']:
            wordsInStandard.append(word)
        for key in colors:
            if word in colors[key]:
                wordsInStandard.append(key)
    return list(set(wordsInStandard))

def __getAttributeInfo__():
    attr, colors = get_attr_vocab()
    attrIndicies = __getAttributeIndicies__(attr, colors)
    lenA = len(attrIndicies)
    return lenA, attrIndicies

def __getAttributeIndicies__(attr, colors):
    attrIndicies = {}
    attrs = [el for key in attr for el in attr[key]]
    attrs += [col for col in colors]
    cnt = 0
    for el in attrs:
        if el not in attrIndicies:
            attrIndicies[el] = cnt
            cnt += 1
    return attrIndicies

def __constructVectors__(lenA, attrIndicies, wordsProd):
    prodVectors = []
    for line in wordsProd:
        vector = [0] * lenA
        for word in line:
            vector[attrIndicies[word]] = 1
        prodVectors.append(vector)
    return prodVectors

def __writeToyData__(target_file, attrIndicies, prodids, prodVectors):
    fname = '{}_vectors.txt'.format(target_file)
    with open(fname, 'w') as f:
        f.write(str(prodids)+'\n')
        f.write(str(prodVectors))
    with open('attr2idx.txt', 'w') as f:
        f.write(str(attrIndicies))

def __readToyData__(fname):
    with open(fname, 'r') as f:
        lines = f.readlines()
    prodids = ast.literal_eval(lines[0].strip())
    prodVectors = ast.literal_eval(lines[1].strip())
    with open('attr2idx.txt', 'r') as f:
        attrIndicies = ast.literal_eval(f.readlines()[0].strip())
    return attrIndicies, prodids, prodVectors

###############################################################################
# fetch Product
#TODO:
# 1. vectorize keywords
# 2. find exact matches
# 3. clustering
# 4. get center image
###############################################################################
def fetchProduct(keywords, target_file):
    # check existing files
    attrIndicies, prodids, prodVectors = getToyData(target_file)
    matchingIds, matchingVectors = __findMatchingVectors__(attrIndicies, prodids, prodVectors, keywords)
    # clusterFetchedProducts(matchingIds, matchingVectors)
    __writeFetchedProductIds__(matchingIds)

def __findMatchingVectors__(attrIndicies, prodids, prodVectors, keywords):
    filteredKeywords = __filterKeywords__(keywords)
    print("Keywords Filtered: {}".format(' '.join(filteredKeywords)))
    indicies = [attrIndicies[key] for key in filteredKeywords]
    matchingIds, filteredVectors = __filterVectors__(indicies, prodids, prodVectors)
    return matchingIds, filteredVectors

def __filterKeywords__(keywords):
    custom_dictionary, google_cloud_dictionary = __prepareDictionary__()
    word2sim, sim2word = __prepareSimilarWords__()
    attr, colors = __prepareAttrData__()
    tokenizedWords = tokenize_by_attr(keywords, word2sim, sim2word, custom_dictionary, google_cloud_dictionary)
    filteredKeywords = __checkWordsInAttribute__(tokenizedWords, attr, colors)
    return filteredKeywords

def __filterVectors__(indicies, prodids, prodVectors):
    filteredVectors, matchingIds = [], []
    stdVec = __getStandardVector__(indicies, prodVectors)
    for idx, vec in enumerate(prodVectors):
        temp_vec = [a*b for a,b in zip(vec,stdVec)]
        if stdVec == [a*b for a,b in zip(vec,stdVec)]:
            filteredVectors.append(vec)
            matchingIds.append(prodids[idx])
    return matchingIds, filteredVectors

def __getStandardVector__(indicies, prodVectors):
    stdVec = [0] * len(prodVectors[0])
    for idx in indicies:
        stdVec[idx] = 1
    return stdVec

def clusterFetchedProducts(ids, vectors):
    # cluster
    # get center image
    # write results
    pass

def __writeFetchedProductIds__(matchingIds):
    with open('fetched_product.txt', 'w') as f:
        f.write(str(matchingIds))

if __name__ == "__main__":
    keywords = '데님 셔츠'
    fetchProduct(keywords, target_file)
