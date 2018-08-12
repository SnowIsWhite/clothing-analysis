import ast
import pickle
import numpy as np
from skimage import io, color
from PIL import Image
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import euclidean_distances
from colormath.color_diff_matrix import delta_e_cie2000
from colormath.color_objects import LabColor, sRGBColor
from colormath.color_conversions import convert_color
from collections import Counter
from remove_background import remove_background

def readXkcdRGB():
    with open('./xkcd_color_rgb.txt', 'r') as f:
        xkcdRGB = [(ast.literal_eval(''.join(line.strip().split(' ')[:3])), \
        ' '.join(line.strip().split(' ')[3:])) for line in f.readlines()]
    return xkcdRGB

def writeXkcdLab(convertedColor):
    with open('./xkcd_color_lab.txt', 'w') as f:
        for (lab, name) in convertedColor:
            f.write('{}\t{}\n'.format(lab, name))

# convert xkcd color to lab color
def xkcdRGB2Lab():
    xkcdRgb = readXkcdRGB()
    labColors = []
    for (arr, name) in xkcdRgb:
        rgb = sRGBColor(arr[0], arr[1], arr[2], is_upscaled=True)
        lab = LabColor.get_value_tuple(convert_color(rgb, LabColor))
        labColors.append((lab, name))
    writeXkcdLab(labColors)

def rgb2lab(rgb_color, is_upscaled=True):
    rgb = sRGBColor(rgb_color[0], rgb_color[1], rgb_color[2], is_upscaled=is_upscaled)
    lab_color = convert_color(rgb, LabColor)
    return lab_color

def getLystLabColor():
    with open('lab-colors.pk', 'rb') as f:
        lab_color = pickle.load(f)
    return lab_color

def getLystColorMatrix():
    with open('lab-matrix.txt', 'r') as f:
        data = [ast.literal_eval(line.strip()) for line in f.readlines()]
    lab_matrix = np.array(data)
    return lab_matrix

def labColor2LystColor(target_color):
    # target_color is a lab converted color
    lab_color = getLystLabColor()
    lab_matrix = getLystColorMatrix()
    lab_color_vector = np.array([target_color.lab_l, target_color.lab_a, target_color.lab_b])
    delta = delta_e_cie2000(lab_color_vector, lab_matrix)
    color = lab_color[np.argmin(delta)]
    return color

def _getRGBArrays(image):
    RGBcolors = []
    for width in image:
        for height in width:
            if height[-1] != 0:
                RGBcolors.append(height[:-1].tolist())
    return RGBcolors

def _getCenterOfClusters(kmeans, RGBcolors):
    centers = kmeans.cluster_centers_
    dist = euclidean_distances(centers, RGBcolors)
    centerPixels = [RGBcolors[np.argmin(d)] for d in dist]
    centerLabels = [kmeans.labels_[np.argmin(d)] for d in dist]
    return centerPixels, centerLabels

def _getProportionOfClusters(kmeans):
    centerNum = Counter((kmeans.labels_).tolist()).most_common()
    prop = {}
    total = len(kmeans.labels_)
    for k, v in centerNum:
        prop[k] = v/float(total) * 100
    return prop

def _getMainPixels(RGBcolors):
    X = np.array(RGBcolors)
    kmeans = KMeans(n_clusters=3, random_state=0).fit(X)
    centerPixels, centerLabels = _getCenterOfClusters(kmeans, RGBcolors)
    proportion = _getProportionOfClusters(kmeans)
    centerProp = [proportion[c] for c in centerLabels]
    return centerPixels, centerProp

# get main colors
def getMainColors(image):
    # image is png format
    image = Image.open(image)
    image = np.array(image)
    RGBcolors = _getRGBArrays(image)
    rgb_colors, prop = _getMainPixels(RGBcolors)
    colors = {}
    for idx, k in enumerate(rgb_colors):
        lab = rgb2lab(k)
        lystColor = labColor2LystColor(lab)
        if lystColor not in colors:
            colors[lystColor] = prop[idx]
        else:
            colors[lystColor] += prop[idx]
    print(colors)
