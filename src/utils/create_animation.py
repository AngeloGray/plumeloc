import imageio.v3 as iio
from pathlib import Path

counter = 0
part_num = 0
images = list()
for file in Path("C:/Users/Admin/PycharmProjects/plumeloc/temp_images").iterdir():
    if not file.is_file():
        continue
    images.append(iio.imread(file))
    counter += 1
    if counter > 60:
        part_num += 1
        iio.imwrite(f'animation part {part_num}.gif', images)
        images = list()
        counter = 0
iio.imwrite("animation.gif", images)