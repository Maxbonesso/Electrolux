from pathlib import Path

import cv2

from src.transformation.conversions import compute_diff_spec

if __name__ == '__main__':
    common_img_path = Path('data') / 'acquisizione1'
    output_img_path = Path('data') / 'acquisizione1'
    orthogonal_img_path = common_img_path / 'forno1_ortogonale_00_757950.png'
    parallel_img_path = common_img_path / 'forno1_parallelo_00_101693.png'

    albedo = cv2.imread(str(orthogonal_img_path))
    specular = cv2.imread(str(parallel_img_path))
    output_diffuse, output_pure_specular = compute_diff_spec(albedo, specular)

    cv2.imwrite(str(output_img_path / 'forno1_speculare_00_0000000.png'), 255 * output_pure_specular)
    cv2.imwrite(str(output_img_path / 'forno1_diffuse_00_0000000.png'), 255 * output_diffuse)
    cv2.waitKey(0)
