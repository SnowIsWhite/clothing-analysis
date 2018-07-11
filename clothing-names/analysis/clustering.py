import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as mpatches
from sklearn.cluster import SpectralClustering
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
sys.path.append('../')
from utility import tokenize


n_cluster = 20
class dictionary:
    def __init__(self):
        self.word2num = {}
        self.num2word = {}
        self.word2cnt = {}
        self.total_word = 0

    def put(self, word):
        if word not in self.word2cnt:
            self.word2cnt[word] = 1
        else:
            self.word2cnt[word] += 1

    def rearrange(self):
        temp = []
        for word in self.word2cnt:
            if self.word2cnt[word] < 5:
                temp.append(word)
                continue
            else:
                self.word2num[word] = self.total_word
                self.num2word[self.total_word] = word
                self.total_word += 1

        for word in temp:
            del self.word2cnt[word]


def configure_dictionary(type):
    list_of_words = tokenize(type)
    dic = dictionary()
    for list in list_of_words:
        for word in list:
            dic.put(word)
    dic.rearrange()
    return dic, list_of_words

def print_word_cnt_in_order(dic):
    with open('word_cnt.txt', 'w') as f:
        sorted_by_value = sorted(dic.word2cnt.items(), key=lambda x:x[1], reverse=True)
        for key, val in sorted_by_value:
            f.write('{}\t{}\n'.format(key, val))

def create_vectors(dic, list_of_words):
    print("Start Creating Vectors...")
    vectors = []
    for list in list_of_words:
        vec = np.zeros(dic.total_word)
        for word in list:
            if word not in dic.word2num:
                continue
            else:
                vec[dic.word2num[word]] = 1
        if np.count_nonzero(vec) == 0:
            continue
        else:
            vectors.append(vec.tolist())
    return vectors


def clustering(type, dic, vectors):
    print("Strat Clustering...")
    if type == 'sc':
        sc = SpectralClustering(n_cluster, n_init=10)
        predicted = sc.fit_predict(vectors)
    elif type == 'kmeans':
        X = np.array(vectors)
        kmeans = KMeans(n_clusters=n_cluster, random_state=0).fit(X)
        predicted = kmeans.predict(X)

    result = {}
    for idx, vec in enumerate(vectors):
        words = []
        for arridx, val in enumerate(vec):
            if val == 0:
                continue
            else:
                words.append(dic.num2word[arridx])
        sentence = ' '.join(words)
        if predicted[idx] not in result:
            result[predicted[idx]] = [sentence]
        else:
            result[predicted[idx]].append(sentence)
    fname = 'result/clustering_{}'
    for cluster in result:
        with open(fname.format(cluster+1), 'w') as f:
            for sentence in result[cluster]:
                f.write(sentence + '\n')
    return predicted

def tsne(dic, vectors, predicted):
    print("Start Plotting TSNE...")
    X = np.array(vectors)
    X_embedded = TSNE(n_components=2).fit_transform(X)
    colors = cm.rainbow(np.linspace(0, 1, n_cluster))
    for idx, p in enumerate(predicted):
        plt.scatter(X_embedded[idx,0], X_embedded[idx,1], color=colors[p-1])
    recs = []
    classes = list(range(0, n_cluster))
    for i in range(0,len(colors)):
        recs.append(mpatches.Rectangle((0,0),1,1,fc=colors[i]))
    plt.legend(recs,classes,loc=4)
    plt.savefig('tsne.jpg')


if __name__ == "__main__":
    dic, list_of_words = configure_dictionary('tc')
    print_word_cnt_in_order(dic)
    vectors = create_vectors(dic, list_of_words)
    predicted = clustering('kmeans', dic, vectors)
    tsne(dic, vectors, predicted)
