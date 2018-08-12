import pickle
import ast
import numpy as np
from collections import Counter
from colormath.color_diff_matrix import delta_e_cie2000
from colormath.color_objects import LabColor
from remove_background import remove_background
from PIL import Image
#
# with open('lab-matrix.txt', 'r') as f:
#     data = [ast.literal_eval(line.strip()) for line in f.readlines()]
# lab_matrix = np.array(data)
# print(lab_matrix)
#
# with open('lab-colors.pk', 'rb') as f:
#     lab_color = pickle.load(f)
#
# color = LabColor(lab_l=69.34, lab_a=-0.88, lab_b=-52.57)
# lab_color_vector = np.array([color.lab_l, color.lab_a, color.lab_b])
#
# delta = delta_e_cie2000(lab_color_vector, lab_matrix)
# res = lab_color[np.argmin(delta)]

remove_background('./sample1.jpg', 'out.png')

image = Image.open('out.png')
image = np.array(image)
print(image)
