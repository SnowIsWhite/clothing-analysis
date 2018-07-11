import os
import re
import json
import ast
import math
import numpy as np
import matplotlib.pyplot as plt

DATA_DIR = './result.txt'
IMAGE_DIR = './images/'
TXT_DIR  = './analysis/'
if not os.path.exists(TXT_DIR):
    os.makedirs(TXT_DIR)
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

def read_data():
    data = []
    with open(DATA_DIR, 'r') as f:
        for line in f.readlines():
            data.append(ast.literal_eval(line))
    return data

def analyze_avg_price(upper_class, sub_class, all_sub=False):
    # returns json of brand: avg price
    data = read_data()
    target_data = []

    if all_sub:
        for l in data:
            if l['upper_class'] == upper_class:
                target_data.append(l)
    else:
        for l in data:
            for sub in sub_class:
                if l['upper_class'] == upper_class and l['sub_class'] == sub:
                    target_data.append(l)
    print(len(target_data))
    brands_done = []
    brands_avg = []
    for l in target_data:
        if l['brand'] in brands_done:
            continue
        else:
            curr_brand = l['brand']
            price = 0.
            cnt = 0
            for b in target_data:
                if l['brand'] == curr_brand:
                    price += float(re.sub(',', '', l['price']))
                    cnt += 1
            avg_price = price / cnt
            brands_done.append(curr_brand)
            brands_avg.append(avg_price)

    return brands_done, brands_avg

def plot_graph(brand, price, img_name):
    # save plotted graph
    plt.scatter(range(len(brand)),price)
    plt.savefig(IMAGE_DIR + img_name + '.png')
    return

def save_in_txt(brand, price, term, fname):
    max_price = 0
    for p in price:
        if p > max_price:
            max_price = p
    dividor = max_price / term
    max_price = (dividor + 1) * term
    term_cnt = 1
    temp_storage = {}
    while term_cnt * term <= max_price:
        for i, p in enumerate(price):
            if p < (term_cnt * term) and p >= ((term_cnt -1) * term):
                if term_cnt not in temp_storage:
                    temp_storage[term_cnt] = {'cnt': 1, 'brand': [brand[i]]}
                else:
                    temp_storage[term_cnt]['cnt'] += 1
                    temp_storage[term_cnt]['brand'].append(brand[i])
        term_cnt += 1

    # only numbers
    with open(TXT_DIR + fname + '.txt', 'w') as f:
        f.write('total : {}\n'.format(str(len(brand))))
        for term_cnt in temp_storage:
            line = '{}\t-\t{}\t:\t{}\n'.format(str((term_cnt - 1 ) * term), \
            str(term_cnt * term), str(temp_storage[term_cnt]['cnt']))
            f.write(line)
    # with brand names

    with open(TXT_DIR + fname + '_brands.txt', 'w') as f:
        for term_cnt in temp_storage:
            line = '{}\t-\t{}\t:\t{}'.format(str((term_cnt - 1 ) * term),\
            str(term_cnt * term), str(temp_storage[term_cnt]['cnt']))
            for b in temp_storage[term_cnt]['brand']:
                line += '\t{}'.format(b)
            line += '\n\n'
            f.write(line)

if __name__ == "__main__":
    subclass = ['쇼트 팬츠']
    all_sub = True
    b, p = analyze_avg_price('SHOES', subclass, all_sub)
    save_in_txt(b, p, 10000 , '신발')
