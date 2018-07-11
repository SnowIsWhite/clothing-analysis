from collections import Counter
import random
import sys
import ast
document_dir = '../../attributes/img2attr.txt'

def __get_img2attr__():
    with open(document_dir, 'r') as f:
        img2attr = ast.literal_eval(f. readlines()[0])
    return img2attr
