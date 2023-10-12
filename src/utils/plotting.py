import os

from src.transformation.plotting_function import *
from src.transformation.utils import *


if __name__ == '__main__':
    # create lists, one for every type of image
    no_filtro = []
    filtro_orthogonal = []
    filtro_parallel = []

    # create two lists used for saving min and max gain for every type of image
    max_gains = [0, 0, 0]
    min_gains = [10, 10, 10]

    # take every file in the folder, divide it for type of image and save tha values of the gain
    filename = "data/acquisizione_4/materiale6/"
    for root, dirs, files in os.walk(filename):
        for file in files:
            if file.endswith('.png'):
                type_img = np.array(file.split('_'))[1]
                if type_img == 'nofiltro':
                    no_filtro.append(file)
                    if int(np.array(file.split('_'))[2]) > max_gains[0]:
                        max_gains[0] = int(np.array(file.split('_'))[2])
                    if int(np.array(file.split('_'))[2]) < min_gains[0]:
                        min_gains[0] = int(np.array(file.split('_'))[2])
                if type_img == 'filtroortogonale':
                    filtro_orthogonal.append(file)
                    if int(np.array(file.split('_'))[2]) > max_gains[1]:
                        max_gains[1] = int(np.array(file.split('_'))[2])
                    if int(np.array(file.split('_'))[2]) < min_gains[1]:
                        min_gains[1] = int(np.array(file.split('_'))[2])
                if type_img == 'filtroparallelo':
                    filtro_parallel.append(file)
                    if int(np.array(file.split('_'))[2]) > max_gains[2]:
                        max_gains[2] = int(np.array(file.split('_'))[2])
                    if int(np.array(file.split('_'))[2]) < min_gains[2]:
                        min_gains[2] = int(np.array(file.split('_'))[2])

    # call the function for plotting the plot
    exposure_plot(no_filtro, max_gains[0] + 1, min_gains[0], filename)
    exposure_plot(filtro_orthogonal, max_gains[1] + 1, min_gains[1], filename)
    exposure_plot(filtro_parallel, max_gains[2] + 1, min_gains[2], filename)
