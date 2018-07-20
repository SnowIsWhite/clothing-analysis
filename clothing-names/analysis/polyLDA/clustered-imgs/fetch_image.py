
import os
import sys
import ast
import random
sys.path.append('../../../')
from s3utility import get_file_from_bucket

clustering_type = 'kmeans'
lda_type = 'mono'
signature = 'handsome'
numSelectElements = 10

folder = '{}_{}_{}'.format(signature, lda_type, clustering_type)
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
    chosenFiles = __randomSelect__(files)
    save_dir = os.path.join(os.getcwd(), folder_name) + '/'
    get_file_from_bucket(chosenFiles, save_dir, key_dir='raw/')

def __randomSelect__(files):
    chosenFiles = []
    for i in range(numSelectElements):
        if len(files) == 0:
            break
        choice = random.choice(files)
        files.remove(choice)
        chosenFiles.append(choice)
    return choseFiles
