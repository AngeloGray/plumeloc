from time import sleep
from typing import List, Dict, Tuple
# from src.utils import ros_commands
from src.world.territory import Point, World
from src.objects import UAV

# Задаём количество дронов и их начальные позиции
number_of_uavs: int = 2
UAV_INITIAL_POSITIONS = {
    0: (0, 0),
    1: (52, 0),
}

# Подготавливаем списки для карт территории для каждого дрона и внедряем их в соответствующие объекты дрона
world_uav: List[World] = []
uav: List[UAV] = []

# С помощью цикла для каждого мира дрона:
# 1) создается мир
# 2) Этот мир рисуется в консоль
# 3) Для каждого дрона создается отдельный экземпляр класса UAV с встроенным объектом uav_world
for i in range(number_of_uavs):
    world_uav.append(World())
    world_uav[i].uav_world_create()
    world_uav[i].world_paint()
    uav_id = i
    uav.append(UAV(
        id_=uav_id,
        cur_point=world_uav[i].points[UAV_INITIAL_POSITIONS[uav_id]],
        uav_world=world_uav[i]
    ))
    uav[i].calculate_weights()  # Подсчет весов на карте мира каждого дрона
    uav[i].paint_weights_map()  # Отображение мира каждого дрона в консоли


if number_of_uavs > 1:
    another_worlds: List[World] = []
    for n in range(1, number_of_uavs):
        another_worlds.append(uav[n].uav_world)
    uav[0].merge_weights(another_worlds)
    for n in range(1, number_of_uavs):
        uav[n].uav_world.points = uav[0].uav_world.points

for i in range(number_of_uavs):
    uav[i].paint_weights_map()

world_global = World()
# world_global.world_create()
world_global.test_world_create()
world_global.world_paint()
# world_global.plume_gen()
mission_is_active: bool = True

logs_file = open('painted_movings.txt', 'w')

while mission_is_active:
    for n in range(number_of_uavs):
        uav[n].get_target_point()

    for i in range(number_of_uavs):
        for j in range(number_of_uavs):
            if i != j:
                if uav[i].target_point.id == uav[j].target_point.id:
                    print(f'uav{i} and uav{j} has same target point')
                    logs_file.write(f'uav{i} and uav{j} has same target point')
                    for shift_value in range(8):
                        uav[i].get_target_point(shift=shift_value)
                        if uav[i].target_point.id != uav[j].target_point.id:
                            break


    for n in range(number_of_uavs):
        # uav[n].measure_plume(world_global.points[(int(uav[n].cur_point.x), int(uav[n].cur_point.y))])
        # logs_file.write(f"uav with id {n} measured c = {uav[n].cur_point.c} in Point ({uav[n].cur_point.x}, {uav[n].cur_point.y})\n")
        uav[n].move_to(uav[n].target_point)
        logs_file.write(
            f"uav with id {n} moved to Point ({uav[n].cur_point.x}, {uav[n].cur_point.y})\n")
        uav[n].measure_plume(world_global.points[(int(uav[n].cur_point.x), int(uav[n].cur_point.y))])
        logs_file.write(
        f"uav with id {n} measured c = {uav[n].cur_point.c} in Point ({uav[n].cur_point.x}, {uav[n].cur_point.y})\n")
        if uav[n].cur_point.c == 1.0:
            mission_is_active = False
        else:
            uav[n].cur_point.weight = n
            uav[n].uav_world.points[(int(uav[n].cur_point.x), int(uav[n].cur_point.y))].weight = n


        uav[i].paint_weights_map()
        sleep(0.2)








# first_world_uav = World()
# first_world_uav.uav_world_create()
#
# first_uav_id = 0
# first_uav = UAV(
#     id_=first_uav_id,
#     cur_point=first_world_uav.points[UAV_INITIAL_POSITIONS[first_uav_id]],
#     uav_world=first_world_uav
#     # publisher_obj=ros_commands.initialize_publisher(first_uav_id)
# )
# first_uav.calculate_weights()
# first_uav.paint_weights_map()
#
# second_world_uav = World()
# second_world_uav.uav_world_create()
# second_uav_id = 1
# second_uav = UAV(
#     id_=second_uav_id,
#     cur_point=second_world_uav.points[UAV_INITIAL_POSITIONS[second_uav_id]],
#     uav_world=second_world_uav
#     # publisher_obj=ros_commands.initialize_publisher(first_uav_id)
# )
#
# second_uav.calculate_weights()
# second_uav.paint_weights_map()
#
# first_uav.merge_weights(second_uav.uav_world)
# second_uav.uav_world = first_uav.uav_world
#
# first_uav.paint_weights_map()
# second_uav.paint_weights_map()
#
#
# world_global = World()
# world_global.world_create()
# world_global.plume_gen()
#
# print(f"uav with id {first_uav.id_} is at position: x = {first_uav.cur_point.x}, y = {first_uav.cur_point.y} ")
# first_uav.measure_plume(world_global.points[(int(first_uav.cur_point.x), int(first_uav.cur_point.y))])
# first_uav.mark_point()
#
#
# world_global.world_paint()
# print("meow")
# first_world_uav.world_paint()
# first_uav.move_to(first_world_uav.points[(10, 10)])
# print("meow")
# first_uav.measure_plume(world_global.points[(int(first_uav.cur_point.x), int(first_uav.cur_point.y))])
# first_uav.mark_point()
# print("meow")
# # while True:
# #     sleep(1)
# #     first_uav.post_to_chanel("Ready")
