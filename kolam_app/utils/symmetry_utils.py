import cv2, numpy as np
from math import radians, cos, sin

def rotational_symmetry_score(image_path, step=30):
    """
    Compare original vs rotated versions every `step` degrees.
    Returns a score 0–1 (1 = perfect symmetry).
    """
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (256,256))
    img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)[1]
    score = 0
    for angle in range(step, 360, step):
        M = cv2.getRotationMatrix2D((128,128), angle, 1.0)
        rotated = cv2.warpAffine(img, M, (256,256))
        diff = cv2.absdiff(img, rotated)
        match = 1.0 - (np.sum(diff) / (255.0 * diff.size))
        score += match
    return score / ((360 // step) - 1)
