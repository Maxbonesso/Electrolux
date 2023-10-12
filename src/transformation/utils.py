import numpy as np


def min_max_scaling(img: np.ndarray, min_x: float = None, max_x: float = None) -> np.ndarray:
    """
    (img-min_X)/(max_X-min_X)

    :param img: image to scale
    :param min_x: min value
    :param max_x: max value
    :return: rescaled image
    """

    if min_x is None:
        min_x = np.min(img)
    if max_x is None:
        max_x = np.max(img)
    output_img = (img - min_x) / (max_x - min_x)

    return output_img


def eval_saturation(input_img: np.ndarray) -> float:
    """
    Contain % of white pixel in the image
    :param input_img: input image
    :return: float number that represents the % of white pixel
    """

    # create mask and calculate result
    white_mask = input_img == 255
    total_pixel = white_mask.size
    total_white = np.sum(white_mask)
    result_value = (total_white * 100) / total_pixel

    return result_value
