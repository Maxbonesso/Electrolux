import json
from pathlib import Path

import cv2
import numpy as np

from src.components.matrix_cam import MatrixCam
from src.transformation.utils import eval_saturation
from scipy.optimize import minimize


def photo(cam: MatrixCam, exposure: float) -> tuple:
    """
    Take a photo and calculate saturation and luminance
    :param cam: camera
    :param exposure: exposure time
    :return:
    """
    cam.set_exposure(int(exposure))
    img = cam.take_photo()

    saturation_value = eval_saturation(img)

    return img, saturation_value


def binary_search(cam: MatrixCam, acquisition_attributes: json) -> int:
    """
    Search the perfect exposure time and save the image
    :param cam: camera
    :param acquisition_attributes: attributes for the saving of the image
    :return: exposure time
    """
    max_exposure = acquisition_attributes["max_exposure"]
    min_exposure = acquisition_attributes["min_exposure"]
    search = int((min_exposure + max_exposure) / 2)
    while True:
        return_img, saturation_value = photo(cam, search)
        print("exposure:" + str(search))
        print("saturation:" + str(saturation_value))

        if search == 998999:
            return search

        if saturation_value > 0.2:
            max_exposure = search
            search = int((min_exposure + max_exposure) / 2)
        elif saturation_value < 0.2:
            if 0.1 < saturation_value <= 0.2:
                return search
            else:
                min_exposure = search
                search = int((min_exposure + max_exposure) / 2)
                if int(max_exposure) == int(min_exposure):
                    return search
        else:
            return search


def exposure_energy(x0: np.ndarray, params: list) -> float:
    """
    Energy function for the calculate of perfect exposure
    :param x0:
    :param params:
    :return:
    """
    cam, acquisition_attributes = params
    _, saturation_value = photo(cam, x0[0])
    print(x0, saturation_value)
    return abs(saturation_value - 0.2)


def main_automatic_acquisition() -> None:
    """
    Automatic acquisition
    :return: none
    """

    # read json and create list
    config_path = Path("settings") / "config.json"
    with config_path.open() as filestream:
        acquisition_attributes = json.load(filestream)

    # set camera and calculate an initial exposure
    cam = MatrixCam()

    initial_exposure = binary_search(cam, acquisition_attributes["automatic_acquisition"])

    # set information and calculate the perfect exposure whit minimize
    x0 = np.array([initial_exposure])
    params = [cam, acquisition_attributes["automatic_acquisition"]]
    bounds = [(1000, 999000)]
    res = \
        minimize(exposure_energy, x0, args=params, method='Nelder-Mead', tol=1e-2,
                 options={"disp": False, "maxiter": 10},
                 bounds=bounds).x[0]

    # take the optimal photo
    res = int(res)
    img, saturation_value = photo(cam, res)
    print('The optimised exposure value is: {}'.format(res))
    print('The saturation value is: {:.2f}'.format(saturation_value))
    # save the photo
    cv2.imwrite(
        acquisition_attributes["automatic_acquisition"]["directory"] + acquisition_attributes["automatic_acquisition"][
            "material"] + "_" + \
        acquisition_attributes["automatic_acquisition"]["filtro"] + "_00_%06d.png" % res, img)
    cam.close()


if __name__ == '__main__':
    main_automatic_acquisition()
