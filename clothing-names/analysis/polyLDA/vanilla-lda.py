from collections import Counter
import random
import sys
import ast
sys.path.append('../attributes/')

document_dir = '../../attributes/img2attr.txt'

def __get_img2attr__():
    with open(document_dir, 'r') as f:
        img2attr = ast.literal_eval(f. readlines()[0])
    return img2attr

def get_document():
    img2attr = __get_img2attr__()
    document = [img2attr[key]['local'] for key in img2attr]
    return document

def p_topic_given_document(topic, d, alpha=0.1):
    return ((document_topic_counts[d][topic] + alpha) /
            (document_lengths[d] + K * alpha))

def p_word_given_topic(word, topic, beta=0.1):
    return ((topic_word_counts[topic][word] + beta) /
            (topic_counts[topic] + V * beta))

def topic_weight(d, word, k):
    return p_word_given_topic(word, k) * p_topic_given_document(k, d)

def choose_new_topic(d, word, K):
    return sample_from([topic_weight(d, word, k) for k in range(K)])

def sample_from(weights):
    total = sum(weights)
    rnd = total * random.random()
    for i, w in enumerate(weights):
        rnd -= w
        if rnd <= 0:
            return i

documents = get_document()
random.seed(0)
K=5
# assign random topics to each word in each doucument
# has to change: random topic for word in body region for body region in doc
document_topics = [[random.randrange(K) for word in document]
                    for document in documents]
document_topic_counts = [Counter() for _ in documents]
topic_word_counts = [Counter() for _ in range(K)]
topic_counts = [0 for _ in range(K)]
document_lengths = [len(document) for document in documents]
distinct_words = set(word for document in documents for word in document)
V = len(distinct_words)
D = len(documents)

# assign counts
for d in range(D):
    for word, topic in zip(documents[d], document_topics[d]):
        document_topic_counts[d][topic] += 1
        topic_word_counts[topic][word] += 1
        topic_counts[topic] += 1

def train_mono():
    for iter in range(1000):
        for d in range(D):
            # for body parts
            for i, (word, topic) in enumerate(zip(documents[d],
                                                  document_topics[d])):
                document_topic_counts[d][topic] -= 1
                topic_word_counts[topic][word] -= 1
                topic_counts[topic] -= 1
                document_lengths[d] -= 1
                new_topic = choose_new_topic(d, word, K)
                document_topics[d][i] = new_topic
                document_topic_counts[d][new_topic] += 1
                topic_word_counts[new_topic][word] += 1
                topic_counts[new_topic] += 1
                document_lengths[d] += 1

    # save result
    with open('mono_lda_result.txt', 'w') as f:
        for counter in document_topic_counts:
            f.write(str(dict(counter)) + '\n')

if __name__ == "__main__":
    train_mono()
