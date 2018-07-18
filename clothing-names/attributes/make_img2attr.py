import sys
import ast
from tokenize_by_attr import tokenize_by_attr, get_attr_vocab
from collections import Counter
sys.path.append('../')
from utility import get_predefined_words

target_files = ['handsome_result.txt']
data_dir = '../data/'

def __find_rel_prod_desc__(file, prod_num):
    with open(data_dir + file, 'r') as f:
        for line in f.readlines():
            line = ast.literal_eval(line.strip())
            if line['prod_num'] == prod_num:
                return line['prod_desc'], line['category']
    return '', ''

def __imgid2desc__():
    imgid2desc = []
    for file in target_files:
        mall = file.split('_')[0]
        with open(data_dir + file, 'r') as f:
            for idx, line in enumerate(f.readlines()):
                if idx < 100:
                    continue
                line = ast.literal_eval(line.strip())
                tmp_img_id = '{}_{}_{}'.format(mall, str(idx), line['prod_num'])
                prods = []
                sentences = []
                if len(line['category']) != 0:
                    sentences.append(line['category'])
                if len(line['name']) != 0:
                    sentences.append(line['name'])
                if len(line['prod_desc']) != 0:
                    sentences.append(line['prod_desc'])
                pre_prods = [sent for sent in sentences]
                for color in line['color']:
                    sentences = [sent for sent in pre_prods]
                    if color == '':
                        img_id = '{}_{}'.format(tmp_img_id, 'empty')
                    else:
                        img_id = '{}_{}'.format(tmp_img_id, color)
                        sentences.append(color)
                    tmp_prods = [sent for sent in prods]
                    prods.append(sentences)
                    sub_dics = line['color'][color]['rel']
                    for sub_dic in sub_dics:
                        sentences = []
                        rel_prod_desc_done = False
                        if 'rel_prod_num' in sub_dic:
                            if len(sub_dic['rel_prod_num']) != 0:
                                if 'rel_prod_desc' in sub_dic:
                                    if len(sub_dic['rel_prod_desc']) != 0:
                                        # use rel_prod_desc
                                        sentences.append(sub_dic['rel_prod_desc'])
                                        rel_prod_desc_done = True
                                if not rel_prod_desc_done:
                                    # go to rel prod num
                                    rel_prod_desc, rel_category= __find_rel_prod_desc__(file, sub_dic['rel_prod_num'])
                                    if len(rel_prod_desc) != 0:
                                        sentences.append(rel_prod_desc)
                                        rel_prod_desc_done = True
                                    if len(rel_category) != 0:
                                        sentences.append(rel_category)
                        if 'rel_name' in sub_dic:
                            if len(sub_dic['rel_name']) != 0:
                                sentences.append(sub_dic['rel_name'])
                        prods.append(sentences)
                    if len(prods) > 1:
                        imgid2desc.append({'img_id': img_id, 'prods': prods})
                    prods = [sent for sent in tmp_prods]
    return imgid2desc


def img2attr():
    _, word2sim, sim2word = get_predefined_words()
    attr, colors = get_attr_vocab()
    img2attr = {}
    imgid2desc = __imgid2desc__()
    for descdic in imgid2desc:
        globe, local = [], []
        for sentences in descdic['prods']:
            attr2word = {'article': [], 'collar': [], 'material': [], 'pattern': [],\
            'shape': [], 'color': []}
            for sentence in sentences:
                sents = sentence.split('.')
                for s in sents:
                    tokenized = tokenize_by_attr(s, word2sim, sim2word)
                    for word in tokenized:
                        if word in attr['article']:
                            attr2word['article'].append(word)
                        if word in attr['collar']:
                            attr2word['collar'].append(word)
                        if word in attr['material']:
                            attr2word['material'].append(word)
                        if word in attr['pattern']:
                            attr2word['pattern'].append(word)
                        if word in attr['shape']:
                            attr2word['shape'].append(word)
                        for key in colors:
                            if word in colors[key]:
                                attr2word['color'].append(key)
            # add global attributes
            for key in attr2word:
                globe += list(set(attr2word[key]))
            # count the most frequent article
            if len(attr2word['article']) == 0:
                print(descdic)
                print(attr2word)
            article_counter = Counter(attr2word['article']).most_common()
            article = article_counter[0][0]
            # make local attribute
            for key in attr2word:
                if key == 'article':
                    continue
                words = list(set(attr2word[key]))
                for w in words:
                    local.append('{}_{}_{}'.format(article, key, w))
        article = [el.split('_')[0] for el in local]
        if len(list(set(article))) < 2:
            continue
        globe = list(set(globe))
        img2attr[descdic['img_id']] = {'global': globe, 'local': local}

    with open('img2attr.txt', 'w') as f:
        f.write(str(img2attr))

if __name__ == "__main__":
    img2attr()
