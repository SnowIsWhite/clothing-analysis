from collections import Counter
import random
import sys
import ast
import os
document_dir = '../../attributes/img2attr.txt'
body_dir = '../../attributes/body_regions/'

def __get_img2attr__():
    with open(document_dir, 'r') as f:
        img2attr = ast.literal_eval(f. readlines()[0])
    return img2attr

def __get_body_regions__():
    bodyparts = {}
    for path, dir, fname in os.walk(body_dir):
        for file in fname:
            with open(os.path.join(path,file), 'r') as f:
                part = file.split('.')[0]
                bodyparts[part] = []
                for line in f.readlines():
                    bodyparts[part].append(line.strip())
    return bodyparts

def get_document():
    img2attr = __get_img2attr__()
    bodyparts = __get_body_regions__()
    region_order = ['upper', 'outer', 'lower', 'hosiery']
    documents = []
    for key in img2attr:
        tmp_doc = {}
        for el in img2attr[key]['local']:
            bp = el.split('_')[0]
            attr = el.split('_')[-1]
            for bkey in bodyparts:
                if bp in bodyparts[bkey]:
                    if bkey not in tmp_doc:
                        tmp_doc[bkey] = [bp, attr]
                    else:
                        tmp_doc[bkey].append(bp)
                        tmp_doc[bkey].append(attr)
        tmp = []
        for order in region_order:
            if order in tmp_doc:
                tmp.append(list(set(tmp_doc[order])))
            else:
                tmp.append([])
        documents.append(tmp)
    return documents

def p_topic_given_document(topic, d, bp, alpha=10):
    return ((document_topic_counts[d][topic] + alpha) /
            (document_lengths[d][bp] + K * alpha))

def p_word_given_topic(word, topic, bp, beta=0.1):
    return ((topic_word_counts[topic][bp][word] + beta) /
            (topic_counts[topic] + V[bp] * beta))

def topic_weight(d, word, k, bp):
    return p_word_given_topic(word, k, bp) * p_topic_given_document(k, d, bp)

def choose_new_topic(d, word, K, bp):
    return sample_from([topic_weight(d, word, k, bp) for k in range(K)])

def sample_from(weights):
    total = sum(weights)
    rnd = total * random.random()
    for i, w in enumerate(weights):
        rnd -= w
        if rnd <= 0:
            return i

documents = get_document()
random.seed(0)
K = 5
n_regions = 4
document_topics = [[[random.randrange(K) for word in region] for region in document]
                    for document in documents]
document_topic_counts = [Counter() for _ in documents]
topic_word_counts = [[Counter() for _ in range(n_regions)] for _ in range(K)]
topic_counts = [0 for _ in range(K)]
document_lengths = [[len(region) for region in document] for document in documents]

distinct_words = [[] for _ in range(n_regions)]
for document in documents:
    for idx, region in enumerate(document):
        distinct_words[idx] += region
distinct_words = [set(region) for region in distinct_words]
V = [len(region) for region in distinct_words]
D = len(documents)

for d in range(D):
    for bp in range(n_regions):
        for word, topic in zip(documents[d][bp], document_topics[d][bp]):
            document_topic_counts[d][topic] += 1
            topic_word_counts[topic][bp][word] += 1
            topic_counts[topic] += 1

def train_poly():
    for iter in range(10000):
        for d in range(D):
            for bp in range(n_regions):
                for i, (word, topic) in enumerate(zip(documents[d][bp], document_topics[d][bp])):
                    document_topic_counts[d][topic] -= 1
                    topic_word_counts[topic][bp][word] -= 1
                    topic_counts[topic] -= 1
                    document_lengths[d][bp] -= 1
                    new_topic = choose_new_topic(d, word, K, bp)
                    document_topics[d][bp][i] = new_topic
                    document_topic_counts[d][topic] += 1
                    topic_word_counts[topic][bp][word] += 1
                    topic_counts[topic] += 1
                    document_lengths[d][bp] += 1
    # save result
    with open('poly_lda_result.txt', 'w') as f:
        for counter in document_topic_counts:
            f.write(str(dict(counter)) + '\n')

if __name__ == "__main__":
    train_poly()
