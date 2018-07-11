# text file of brand #of data, mean, sd, median, min, max, q1, q3

import ast
import csv
import numpy as np

result_dir = './price-results/'
with open('hyundai1_result.txt', 'r') as f:
    lines = f.readlines()
    raw = [ast.literal_eval(line.strip()) for line in lines]

# data: {'category': 'brand': [prices]}

data = {}
for line in raw:
    category = line['category']
    brand = line['brand']
    price = line['price'].replace(',', '')
    if category not in data:
        data[category] = {}
        if brand not in data[category]:
            data[category][brand] = [float(price)]
        else:
            data[category][brand].append(float(price))
    else:
        if brand not in data[category]:
            data[category][brand] = [float(price)]
        else:
            data[category][brand].append(float(price))

# save calculated values
for category in data:
    fname = '{}.csv'.format(category.replace('/', '-'))
    fieldname = ['brand', '# of data', 'mean', 'sd', 'median', 'min', 'max', 'q1', 'q3']
    contents = []
    for brand in data[category]:
        prices = data[category][brand]
        number = len(prices)
        if number < 5:
            continue
        prices = np.array(prices)
        min = np.min(prices)
        max = np.max(prices)
        median = np.median(prices)
        mean = np.mean(prices)
        sd = np.std(prices)
        q1 = np.percentile(prices, 25)
        q3 = np.percentile(prices, 75)

        content = [brand, str(number), '{0:.2f}'.format(mean), '{0:.2f}'.format(sd), str(median), str(min), str(max), str(q1), str(q3)]
        contents.append(content)

    with open(result_dir + fname, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(fieldname)
        writer.writerows(contents)
