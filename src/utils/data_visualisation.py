import numpy as np
import matplotlib.pyplot as plt
import time
from typing import List
from src.objects import UAV
from src.world.territory import World
from src.config import TERRITORY_SIZE


def mpl_paint_weights_map(uav: List[UAV], time_iter: int, uav_id: int, world: World, mode: str) -> None:
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
            if (i, j) == (26, 26):
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
        text = ax.text(uav[n].cur_point.x, uav[n].cur_point.y, round(array_2d[uav[n].cur_point.y][uav[n].cur_point.x]),
                       ha="center", va="center", color="black", backgroundcolor='purple',
                       fontsize='xx-small', fontweight='extra bold')

    ax.set_title(f"Карта весов для дрона (id = {uav_id}). Итерация t = {time_iter}. Выбирается наибольший слева mode = 0")
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

# vegetables = ["cucumber", "tomato", "lettuce"]
# farmers = ["Farmer Joe", "Upland Bros.", "Smith Gardening"]
#
# harvest = np.array([[7, 8, 9],
#                     [4, 5, 6],
#                     [1, 2, 3]])
#
#
# fig, ax = plt.subplots()
# im = ax.imshow(harvest)
#
# # Show all ticks and label them with the respective list entries
# ax.set_xticks(np.arange(len(farmers)), labels=farmers)
# ax.set_yticks(np.arange(len(vegetables)), labels=vegetables)
#
# # Rotate the tick labels and set their alignment.
# plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
#          rotation_mode="anchor")
#
# # Loop over data dimensions and create text annotations.
# for i in range(len(vegetables)):
#     for j in range(len(farmers)):
#         text = ax.text(j, i, harvest[i, j],
#                        ha="center", va="center", color="w")
# text = ax.text(6, 6, harvest[0,0],
#                        ha="center", va="center", color="black")
# ax.set_title("Harvest of local farmers (in tons/year)")
# fig.tight_layout()
# plt.show()e
