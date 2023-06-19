import numpy as np
import matplotlib.pyplot as plt
import time
from typing import List
from src.objects import UAV
from src.world.territory import World
from src.config import TERRITORY_SIZE


def mpl_paint_weights_map(uav: List[UAV], time_iter: int, world: World, finish_flag_uav_id: int = None) -> None:
    plume_boxes: List = []
    # Формируем трёхмерный массив точек, матрицу весов:
    array_2d = np.zeros((TERRITORY_SIZE, TERRITORY_SIZE))
    for j in range(TERRITORY_SIZE-1, -1, -1):
        for i in range(TERRITORY_SIZE):
            if world.points[(i, j)].c != 0:
                plume_boxes.append((i, j))
            array_2d[(-j+52)][i] = uav[3].uav_world.points[(i, j)].weight



    fig, ax = plt.subplots()
    fig.set_size_inches(25, 25)
    im = ax.imshow(array_2d)
    x_labels = list(range(TERRITORY_SIZE))
    x_labels = list(map(str, x_labels))
    y_labels = list(range(TERRITORY_SIZE))
    y_labels = list(map(str, y_labels))

    # Show all ticks and label them with the respective list entries
    ax.set_xticks(np.arange(TERRITORY_SIZE), labels=x_labels)
    ax.set_yticks(np.arange(TERRITORY_SIZE), labels=y_labels)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=90, ha="right",
             rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    for i in range(TERRITORY_SIZE):
        for j in range(TERRITORY_SIZE):
            if (j, i) == (26, 26):
                text = ax.text(j, i, round(array_2d[i][j]),
                               ha="center", va="center", color="yellow", backgroundcolor='red',
                               fontsize='xx-small', fontweight='extra bold')
            elif (j, i) in plume_boxes:
                text = ax.text(j, i, round(array_2d[i][j]),
                               ha="center", va="center", color="k", backgroundcolor='red',
                               fontsize='xx-small', fontweight='bold')
            else:
                text = ax.text(j, i, round(array_2d[i][j]),
                               ha="center", va="center", color="k", fontsize='xx-small', fontweight='bold')

    for n in range(len(uav)):
        text = ax.text(uav[n].cur_point.x, (TERRITORY_SIZE - 1) - uav[n].cur_point.y, round(array_2d[uav[n].cur_point.x][uav[n].cur_point.y]),
                       ha="center", va="center", color="black", backgroundcolor='purple',
                       fontsize='xx-small', fontweight='extra bold')
    if finish_flag_uav_id:
        ax.set_title(f"Карта весов для дрона (id = {finish_flag_uav_id}). "
                     f"Итерация t = {time_iter}. Выбирается наибольший слева mode = 0")
    else:
        ax.set_title(
            f"Карта весов для дрона (id = {len(uav)}). Итерация t = {time_iter}. "
            f"Выбирается наибольший слева mode = 0")
    fig.tight_layout()
    #plt.show()
    fig.savefig(f'temp_images/figure{time.time_ns()}.png')
    fig.clear()
    plt.close(fig)
    print('paiting complete!')

# # Попытка реализовать сначала с простыми числами:
# array_2d = np.zeros((TERRITORY_SIZE, TERRITORY_SIZE))
# for i in range(TERRITORY_SIZE):
#     for j in range(TERRITORY_SIZE):
#         array_2d[i][j] = i*j
#
# fig, ax = plt.subplots()
# fig.set_size_inches(15, 15)
# im = ax.imshow(array_2d)
#
# # Show all ticks and label them with the respective list entries
# ax.set_xticks(np.arange(TERRITORY_SIZE))
# ax.set_yticks(np.arange(TERRITORY_SIZE))
#
# # Rotate the tick labels and set their alignment.
# plt.setp(ax.get_xticklabels(), rotation=90, ha="right",
#          rotation_mode="anchor")
#
# # Loop over data dimensions and create text annotations.
# for i in range(TERRITORY_SIZE):
#     for j in range(TERRITORY_SIZE):
#         if (i, j) == (25, 25):
#             text = ax.text(j, i, round(array_2d[i][j]),
#                            ha="center", va="center", color="yellow", fontsize='xx-small', fontweight='extra bold')
#         else:
#             text = ax.text(j, i, round(array_2d[i][j]),
#                            ha="center", va="center", color="k", fontsize='xx-small', fontweight='bold')
#
# ax.set_title("Карта весов для дрона")
# fig.tight_layout()
# plt.show()
# print('paiting complete!')


def _test() -> None:
    vegetables = ["cucumber", "tomato", "lettuce"]
    farmers = ["Farmer Joe", "Upland Bros.", "Smith Gardening"]
    """
    Можно использовать функцию numpy.arange() для создания массива чисел от 1 до 100 и затем преобразовать его в матрицу размером 10 на 10 с помощью метода reshape():

python
import numpy as np

arr = np.arange(1, 101).reshape(10, 10)
print(arr)


Результат:


array([[ 1,  2,  3,  4,  5,  6,  7,  8,  9, 10],
       [11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
       [21, 22, 23, 24, 25, 26, 27, 28, 29, 30],
       [31, 32, 33, 34, 35, 36, 37, 38, 39, 40],
       [41, 42, 43, 44, 45, 46, 47, 48, 49, 50],
       [51, 52, 53, 54, 55, 56, 57, 58, 59, 60],
       [61, 62, 63, 64, 65, 66, 67, 68, 69, 70],
       [71, 72, 73, 74, 75, 76, 77, 78, 79, 80],
       [81, 82, 83, 84, 85, 86, 87, 88, 89, 90],
       [91, 92, 93, 94, 95, 96, 97, 98, 99, 100]])
    """
    harvest = np.array([[ 1,  2,  3,  4,  5,  6,  7,  8,  9, 10],
                       [11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
                       [21, 22, 23, 24, 25, 26, 27, 28, 29, 30],
                       [31, 32, 33, 34, 35, 36, 37, 38, 39, 40],
                       [41, 42, 43, 44, 45, 46, 47, 48, 49, 50],
                       [51, 52, 53, 54, 55, 56, 57, 58, 59, 60],
                       [61, 62, 63, 64, 65, 66, 67, 68, 69, 70],
                       [71, 72, 73, 74, 75, 76, 77, 78, 79, 80],
                       [81, 82, 83, 84, 85, 86, 87, 88, 89, 90],
                       [91, 92, 93, 94, 95, 96, 97, 98, 99, 100]])


    fig, ax = plt.subplots()
    im = ax.imshow(harvest)

    # Show all ticks and label them with the respective list entries
    ax.set_xticks(np.arange(len(farmers)), labels=farmers)
    ax.set_yticks(np.arange(len(vegetables)), labels=vegetables)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    for i in range(10):
        for j in range(10):
            text = ax.text(j, i, harvest[i, j],
                           ha="center", va="center", color="w")
    text = ax.text(0, 1, harvest[0, 1],
                           ha="center", va="center", color="black", backgroundcolor='yellow')
    ax.set_title("Harvest of local farmers (in tons/year)")
    fig.tight_layout()
    plt.show()

_test()