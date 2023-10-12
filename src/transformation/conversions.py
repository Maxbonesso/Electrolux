from typing import Tuple

import numpy as np

from src.transformation.utils import min_max_scaling


def linear_to_srgb(input_img: np.ndarray) -> np.ndarray:
    """
    Convert a linear image to a srgb image
    :param input_img: linear image
    :return: srgb image
    """
    output_img = np.copy(input_img)

    # creation of the masks
    neg_mask = output_img <= 0
    first_threshold_mask = (output_img > 0) * (output_img <= 0.0031308)  # and bit a bit
    second_threshold_mask = (output_img > 0.0031308) * (output_img <= 1)
    pos_mask = (output_img > 1)

    # application of the masks
    output_img[neg_mask] = 0
    output_img[first_threshold_mask] *= 12.92
    output_img[second_threshold_mask] = (np.power(output_img[second_threshold_mask], 0.41666) * 1.055) - 0.055
    output_img[pos_mask] = 1

    return output_img


def srgb_to_linear(input_img: np.ndarray) -> np.ndarray:
    """
    Convert a srgb image to a linear image
    :param input_img: srgb image
    :return: linear image
    """
    output_img = np.copy(input_img)

    # creation of the masks
    neg_mask = output_img <= 0
    first_threshold_mask = (output_img > 0) * (output_img <= 0.04045)  # and bit a bit
    second_threshold_mask = (output_img > 0.04045) * (output_img <= 1)
    pos_mask = (output_img > 1)

    # application of the masks
    output_img[neg_mask] = 0
    output_img[first_threshold_mask] /= 12.92
    output_img[second_threshold_mask] = np.power((output_img[second_threshold_mask] + 0.055) / 1.055, 2.4)
    output_img[pos_mask] = 1

    return output_img


def compute_diff_spec(orthogonal_filter_img: np.ndarray, parallel_filter_img: np.ndarray) \
        -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute the diffuse and the pure specular images.

    :param orthogonal_filter_img: the orthogonal filter image.
    :param parallel_filter_img: the parallel filter image.
    :return: the diffuse image and the pure specular image.
    """
    # convert input images to linear space
    linear_orthogonal_filter_img = srgb_to_linear(min_max_scaling(orthogonal_filter_img.astype(float), 0, 255))
    linear_parallel_filter_img = srgb_to_linear(min_max_scaling(parallel_filter_img.astype(float), 0, 255))

    # compute diffuse and pure specular
    linear_diffuse = linear_orthogonal_filter_img * 2
    linear_pure_specular = linear_parallel_filter_img - linear_orthogonal_filter_img

    # convert images to srbg
    output_diffuse = linear_to_srgb(linear_diffuse)
    output_pure_specular = linear_to_srgb(linear_pure_specular)

    return output_diffuse, output_pure_specular
