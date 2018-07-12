
import os
import sys
import ast
sys.path.append('../../../')
from s3utility import get_file_from_bucket

clustering_type = 'kmeans'
lda_type = 'mono'

folder = '{}_{}'.format(lda_type, clustering_type)
if not os.path.exists(folder):
    os.makedirs(folder)

fname = '{}_{}_result.txt'.format(lda_type, clustering_type)

with open(fname, 'r') as f:
    line = ast.literal_eval(f.readlines()[0].strip())

for cluster_num in line:
    folder_name = '{}/cluster-{}'.format(folder, str(cluster_num))
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    files = line[cluster_num]
    save_dir = os.path.join(os.getcwd(), folder_name) + '/'
    get_file_from_bucket(files, save_dir, key_dir='raw/')
