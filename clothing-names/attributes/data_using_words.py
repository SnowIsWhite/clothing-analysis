# img2attr 데이터 생성
import ast
import sys
import string
from nltk.corpus import stopwords
from konlpy.tag import Kkma
sys.path.append('../')
from utility import get_predefined_words, get_category_words, filter_string
sys.path.append('../dictionary/')
from dictionary.en_ko_dictionary import update_dictionary, read_dictionary

files = ['handsome_result.txt']
data_dir = '../data/'
attr_files = ['article.txt', 'collar.txt', 'colors.txt', 'material.txt', 'pattern.txt', 'shape.txt']
stopwords, colorwords, word2sim, sim2word = get_predefined_words()
cat2word, word2cat = get_category_words()

def get_attr_vocab():
    # get predefined attribute vocabularies
    attr = {}
    for file in attr_files:
        with open(file, 'r') as f:
            key = file.split('.')[0]
            attr[key] = []
            for line in f.readlines():
                word = line.strip()
                attr[key].append(word)
    return attr

def img_id_and_prods():
    # get all relevant products in an image
    img_and_prod = []
    for file in files:
        mall = file.split('_')[0]
        with open(data_dir + file, 'r') as f:
            for idx, line in enumerate(f.readlines()):
                line = ast.literal_eval(line.strip())
                org_img_id = '{}_{}_{}'.format(mall, str(idx), line['prod_num'])
                prods = [line['prod_num']]
                for color in line['color']:
                    if color == '':
                        img_id = '{}_{}'.format(org_img_id, 'empty')
                    else:
                        img_id = '{}_{}'.format(org_img_id, color)
                    prods += [subdic['rel_prod_num'] for subdic in line['color'][color]['rel']]
                    if len(prods) == 1:
                        break
                    img_and_prod.append({'img_id': img_id, 'prods': prods})
    return img_and_prod

def prod_and_words(attr):
    prod2words = {}
    prod2color = {}
    kkma = Kkma()
    eng2kor, kor2eng = read_dictionary()
    for file in files:
        mall = file.split('_')[0]
        with open(data_dir + file, 'r') as f:
            for line in f.readlines():
                line = ast.literal_eval(line.strip())
                org_prod_id = '{}_{}'.format(mall, line['prod_num'])
                words = []

                # category
                category, eng2kor = filter_string(line['category'], eng2kor)
                category = ''.join(category)
                if category in word2cat:
                    category = cat2word[word2cat[category]]

                # product name
                temp = [word for word in kkma.nouns(line['name'])]
                for idx, temp_word in enumerate(temp):
                    word, engkor = filter_string(temp_word, eng2kor)
                    temp[idx] = word[0]
                words += [word for key in attr for word in temp if word in attr[key]]
                exists = False
                for w in words:
                    if w in attr['article']:
                        exists = True
                if not exists:
                    for key in attr:
                        if category in attr[key]:
                            words.append(category)

                # product description
                sentences = line['prod_desc'].split('.')
                temp = [word for sent in sentences for word in kkma.nouns(sent) if word not in string.punctuation]
                for idx, temp_word in enumerate(temp):
                    word, engkor = filter_string(temp_word, eng2kor)
                    temp[idx] = word[0]

                words += [word for key in attr for word in temp if word in attr[key]]
                words = list(set(words))
                if '반바지' in words and '바지' in words:
                    words = words.remove('바지')
                prod2words[org_prod_id] = words

                # first color
                for col in line['color']:
                    color = col
                    break
                if color == '':
                    color = 'empty'
                else:
                    colors = color.split()
                    colors = [eng2kor[col.lower()] for col in colors]
                    for col in colors:
                        if col in word2sim:
                            color = sim2word[word2sim[col]]
                            prod2color[org_prod_id] = color
    return prod2words, prod2color

def img_id_and_attr(img_and_prod, prod2words, prod2color, attr):
    img2attr = {}
    eng2kor, kor2eng = read_dictionary()
    # {img_id : {'global': [], 'local': []}}
    for image in img_and_prod:
        globe, local = [], []
        img_id = image['img_id']
        prods = image['prods']
        mall = img_id.split('_')[0]
        color = img_id.split('_')[-1]
        if color == 'empty':
            color = ''
        else:
            colors = color.split()
            colors = [eng2kor[col.lower()] for col in colors]
            for col in colors:
                if col in word2sim:
                    col = sim2word[word2sim[col]]
                if col in attr['colors']:
                    color = col

        for idx, prod in enumerate(prods):
            prod = '{}_{}'.format(mall, prod)
            if idx != 0:
                if prod not in prod2color:
                    color = ''
                else:
                    color = prod2color[prod]
            if len(color) > 0:
                globe.append(color)
            if prod not in prod2words:
                continue
            globe += prod2words[prod]
            words = prod2words[prod]
            article = []
            for w in words:
                if w in attr['article']:
                    article.append(w)
            for a in article:
                for w in words:
                    if w in attr['collar']:
                        local.append('{}_{}_{}'.format(a,'collar',w))
                    if w in attr['material']:
                        local.append('{}_{}_{}'.format(a,'material',w))
                    if w in attr['pattern']:
                        local.append('{}_{}_{}'.format(a,'pattern',w))
                    if w in attr['shape']:
                        local.append('{}_{}_{}'.format(a,'shape',w))
                if len(color) > 0:
                    local.append('{}_{}_{}'.format(a,'color', color))
            # local = article _ character _ attr

        img2attr[img_id] = {'global': list(set(globe)), 'local': list(set(local))}
    return img2attr

def write_image_and_attr():
    attr = get_attr_vocab()
    img_and_prod = img_id_and_prods()
    prod2words, prod2color = prod_and_words(attr)
    img2attr = img_id_and_attr(img_and_prod, prod2words, prod2color, attr)
    with open('img2attr.txt', 'w') as f:
        f.write(str(img2attr))

if __name__ == "__main__":
    write_image_and_attr()
