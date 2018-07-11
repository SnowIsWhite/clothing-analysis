import numpy as np
import ast
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as mpatches
from sklearn.cluster import SpectralClustering
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE

n_cluster = 5
lda_type = 'mono'
document_dir = '../../attributes/img2attr.txt'
clustered_img_dir = './clustered-imgs/'

def __get_vectors__(type):
    print("Collect Document Topic Counts...")
    fname = '{}_lda_result.txt'.format(type)
    with open(fname, 'r') as f:
        lines = f.readlines()
        counter_list = [ast.literal_eval(line.strip()) for line in lines]
        document_topic_counts = []
        for counts in counter_list:
            temp_counts = [0] * n_cluster
            for k in counts:
                temp_counts[k] = counts[k]
            document_topic_counts.append(temp_counts)
    return document_topic_counts

def tsne(vectors, predicted):
    print("Plotting TSNE Graph...")
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
    plt.savefig('lda_tsne.jpg')


def clustering(lda_type, clustering_type):
    document_topic_counts = __get_vectors__(lda_type)
    print("Start Clustering...")
    predicted = np.array([])
    if clustering_type == 'kmeans':
        X = np.array(document_topic_counts)
        kmeans = KMeans(n_clusters=n_cluster, random_state=0).fit(X)
        predicted = kmeans.predict(X)
    if clustering_type == 'spectral':
        sc = SpectralClustering(n_cluster, n_init=10)
        predicted = sc.fit_predict(document_topic_counts)
    # plot tsne graph
    tsne(document_topic_counts, predicted)
    return predicted

def group_by_images(lda_type, clustering_type, predicted):
    with open(document_dir, 'r') as f:
        lines = f.readlines()
        doc = ast.literal_eval(lines[0])

    imgids = [key for key in doc]

    cluster2imgs = {}
    for idx, label in enumerate(predicted):
        if label not in cluster2imgs:
            cluster2imgs[label] = [imgids[idx]]
        else:
            cluster2imgs[label].append(imgids[idx])

    fname = '{}_{}_result.txt'.format(lda_type, clustering_type)
    with open(clustered_img_dir + fname, 'w') as f:
        f.write(str(cluster2imgs))


if __name__ == "__main__":
    lda_type = 'mono'
    clustering_type = 'spectral'
    predicted = clustering(lda_type, clustering_type)
    group_by_images(lda_type, clustering_type, predicted)
