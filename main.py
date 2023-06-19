import time
from typing import List, Dict, Tuple
# from src.utils import ros_commands
from src.world.territory import Point, World
from src.objects import UAV
from src.utils.data_visualisation import mpl_paint_weights_map

# Задаём количество дронов и их начальные позиции
number_of_uavs: int = 4
UAV_INITIAL_POSITIONS = {
    0: (0, 0),
    1: (100, 0),
    2: (100, 100),
    3: (0, 100)
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
    uav_id = i
    uav.append(UAV(
        id=uav_id,
        cur_point=world_uav[i].points[UAV_INITIAL_POSITIONS[uav_id]],
        uav_world=world_uav[i],
        cur_mode='SEARCH',
    ))
    uav[i].calculate_weights()  # Подсчет весов на карте мира каждого дрона
    uav[i].paint_weights_map()  # Отображение мира каждого дрона в консоли
    #mpl_paint_weights_map(uav[i], time_iter=0, uav_id=0)


# Если дронов - несколько их миры должны быть одинаковыми после того как все веса перемножатся:
if number_of_uavs > 1:
    another_worlds: List[World] = []
    for n in range(1, number_of_uavs):
        another_worlds.append(uav[n].uav_world)
    uav[0].merge_weights(another_worlds)
    for n in range(1, number_of_uavs):
        uav[n].uav_world.points = uav[0].uav_world.points

# Отображаем локальные карты территории каждго дрона и убеждаемся, что они одинаковые
for i in range(number_of_uavs):
    uav[i].paint_weights_map()

# СОздаем объект глобальной карты территории с априорными данными, которые недоступны дронам и которые им придется
# исследовать во время работы алгоритма
world_global = World()
world_global.world_create()  # Создание глобальной карты

# test_time_stamp = 1000
# mpl_paint_weights_map(uav, test_time_stamp, world_global)

logs_file = open('painted_movings.txt', 'w')

# # debug:
# uav[0].cur_point = uav[0].uav_world.points[(22, 22)]
# uav[1].cur_point = uav[1].uav_world.points[(30, 22)]
# uav[2].cur_point = uav[2].uav_world.points[(30, 30)]
# uav[3].cur_point = uav[3].uav_world.points[(22, 30)]

# time_stamp: int = 0
# temp_time = time.time_ns()
# mission_is_active: bool = True

# while mission_is_active:
#
#     for n in range(number_of_uavs):
#         uav[n].get_target_point()
#
#     for i in range(number_of_uavs):
#         for j in range(number_of_uavs):
#             if i != j:
#                 if uav[i].target_point.id == uav[j].target_point.id:
#                     print(f'uav{i} and uav{j} has same target point')
#                     logs_file.write(f'uav{i} and uav{j} has same target point')
#                     for shift_value in range(8):
#                         uav[i].get_target_point(shift=shift_value)
#                         if uav[i].target_point.id != uav[j].target_point.id:
#                             break
#
#     for n in range(number_of_uavs):
#         # uav[n].measure_plume(world_global.points[(int(uav[n].cur_point.x), int(uav[n].cur_point.y))])
#         # logs_file.write(f"uav with id {n} measured c = {uav[n].cur_point.c} in Point ({uav[n].cur_point.x}, {uav[n].cur_point.y})\n")
#         uav[n].move_to(uav[n].target_point)
#         logs_file.write(
#             f"uav with id {n} moved to Point ({uav[n].cur_point.x}, {uav[n].cur_point.y})\n")
#         uav[n].measure_plume(world_global.points[(int(uav[n].cur_point.x), int(uav[n].cur_point.y))])
#         logs_file.write(
#         f"uav with id {n} measured c = {uav[n].cur_point.c} in Point ({uav[n].cur_point.x}, {uav[n].cur_point.y})\n")
#         if uav[n].cur_point.c == 1.0:
#             mission_is_active = False
#         else:
#             uav[n].cur_point.weight = n
#             uav[n].uav_world.points[(int(uav[n].cur_point.x), int(uav[n].cur_point.y))].weight = n
#         uav[n].paint_weights_map()
#         if (n + 1) % number_of_uavs == 0:
#             print(f'creating image for timestamp t = {time_stamp}, Задержка: {(time.time_ns() - temp_time)/(10**9)}')
#             mpl_paint_weights_map(uav[n], time_stamp, n)
#             temp_time = time.time_ns()
#         print(f'\niter {time_stamp}  for uav id{n} complete\n- - - - - - - - - - - - - - - - - - - - - - -')
#     time_stamp += 1

# Модифицированный цикл прохождения по алгоритму с добавлением режима локализации
mission_is_active: bool = True
uav_found_plume: int = -1
time_stamp: int = 0
temp_time = time.time_ns()

while mission_is_active:
    logs_file.write(f"- - - - - - - \nMISSION is at time stamp t = {time_stamp } iteration started\n- - - - - - - \n")
    # Выбор следующей целевой точки, в которую происходит движение исходя из режима в котором находится дрон
    for n in range(number_of_uavs):
        if uav[n].cur_mode == 'SEARCH':
            print(f"uav{n} getting target point in SEARCH mode")
            uav[n].get_target_point_searching()
        elif uav[n].cur_mode == 'LOCALIZE':
            print(f"uav{n} getting target point in LOCALIZE mode")
            uav[n].get_target_point_localization()
        elif uav[n].cur_mode == 'REACH':
            print(f"uav{n} getting target point in REACH mode")
            uav[n].get_target_point_reaching()

    # Условие для недопуска одновременного движения двух дронов на одну и ту же координату (на доработке)
    for i in range(number_of_uavs):
        for j in range(number_of_uavs):
            if i != j:
                if uav[i].target_point.id == uav[j].target_point.id:
                    print(f'uav{i} and uav{j} has same target point')
                    logs_file.write(f'uav{i} and uav{j} has same target point')
                    if uav[i].cur_mode == 'SEARCH':
                        uav[i].target_point = uav[i].cur_point  # Дрон просто стоит на месте пока другой пройдет.
                        logs_file.write(f'uav{i} waits at point {uav[i].cur_point}')
                        break
                    # for shift_value in range(8):
                    #     uav[i].get_target_point(shift=shift_value)
                    #     if uav[i].target_point.id != uav[j].target_point.id:
                    #         break

    # Для каждого из дронов:
    for n in range(number_of_uavs):
        # 1) передвижение на точку target_point
        uav[n].move_to(uav[n].target_point)
        logs_file.write(f"uav with id {n} moved to Point ({uav[n].cur_point.x}, {uav[n].cur_point.y})\n")

    for n in range(number_of_uavs):
        # 2) Измерение уровня концентрации ЗВ в точке, на который переместился дрон
        uav[n].measure_plume(world_global.points[(int(uav[n].cur_point.x), int(uav[n].cur_point.y))])
        logs_file.write(
            f"uav with id {n} measured c = {uav[n].cur_point.c} in Point ({uav[n].cur_point.x},{uav[n].cur_point.y})\n")

    for n in range(number_of_uavs):
        # 3) Проверка отличия загрязнения от нулевого:

        # Если обнаружен источник - конец миссии
        if uav[n].cur_point.c == 1.0:
            logs_file.write(f"uav with id {n} found the SOURCE, at ({uav[n].cur_point.x},{uav[n].cur_point.y})\n"
                            f"----------------------\nMISSION COMPLETED\n---------------------\n")
            uav[n].cur_point.weight = n
            mpl_paint_weights_map(uav, time_stamp, world_global, finish_flag_uav_id=n)
            mission_is_active = False
            break

        # Если обнаружено загрязнение при режиме поиска - переход в режим локализации
        elif uav[n].cur_point.c != 0 and uav[n].cur_mode == 'SEARCH':
            uav[n].cur_point.weight = n
            # Установка режима локализации
            uav[n].cur_mode = 'LOCALIZE'
            logs_file.write(f"uav with id {n} switched mode to 'LOCALIZE'")
            # Измерение направления ветра
            uav[n].measure_wind_direction(world_global.points[(int(uav[n].cur_point.x), int(uav[n].cur_point.y))])
            logs_file.write(f"uav with id {n} measured wind at Point ({uav[n].cur_point.x},{uav[n].cur_point.y})\n")

            # Установка стадии локализации "движение по направлению ветра"
            uav[n].localize_stage = "MOVE_AGAINST_WIND"
            # с этого момента для других дронов местоположение данного дрона становится целевой точкой
            # до тех пор пока они сами не настигнут загрязнение или сам дрон
            # но обработка этого должна происходить только после того как каждый дрон обработает последнее движение
            # поэтому - установка флага
            if uav_found_plume == -1:
                uav_found_plume = n  # флаг устанавливается лишь однажды и равен id дрона-обнаружителя
                # если одоновременно несколько дронов нашли загрязнение - ведущим будет только один из них с
                # меньшим id. Имеет смысл разработать механизм, где ведущим для каждого из дронов будет ближайший.


        # Если обнаружено загрязнение при режиме достижения - переход в режим локализации
        elif uav[n].cur_point.c != 0 and uav[n].cur_mode == 'REACH':
            uav[n].cur_point.weight = n
            # Установка режима локализации
            uav[n].cur_mode = 'LOCALIZE'
            logs_file.write(f"uav with id {n} switched mode to 'LOCALIZE'")

            # Измерение направления ветра
            uav[n].measure_wind_direction(world_global.points[(int(uav[n].cur_point.x), int(uav[n].cur_point.y))])
            logs_file.write(f"uav with id {n} measured wind at Point ({uav[n].cur_point.x},{uav[n].cur_point.y})\n")

            # Установка стадии локализации "движение по направлению ветра"
            uav[n].localize_stage = "MOVE_AGAINST_WIND"

        # Если не обнаружено загрязнение при режиме достижения - продолжение движения в целевую точку
        elif uav[n].cur_point.c == 0 and uav[n].cur_mode == 'REACH':
            uav[n].cur_point.weight = n
            uav[n].reach_point = uav[uav_found_plume - number_of_uavs].cur_point
            uav[n].move_to_reach_point()


        # Если обнаружено загрязнение при режиме локализации - продолжение движения против ветра
        elif uav[n].cur_point.c != 0 and uav[n].cur_mode == 'LOCALIZE':
            uav[n].cur_point.weight = n
            logs_file.write(f"uav with id {n} continuing localizing,"
                            f" passed Point ({uav[n].cur_point.x},{uav[n].cur_point.y})\n")

        # Если загрязнения в режиме локализации не обнаружено - стадия возвращения к загрязнению
        elif uav[n].cur_point.c == 0 and uav[n].cur_mode == 'LOCALIZE':
            uav[n].cur_point.weight = n
            # Выход за загрязнение - необходимо вернуться к загрязнению
            uav[n].localize_stage = "RETURN_TO_PLUME"
            logs_file.write(f"uav with id {n} switched mode to 'RETURN_TO_PLUME', {uav[n].return_stage}\n")

        # Если загрязнение в режиме возвращения обнаруживается - выбрано правильное из двух направлений, возвращение
        # в режим движения против ветра
        elif uav[n].cur_point.c != 0 and uav[n].cur_mode == 'RETURN_TO_PLUME':
            uav[n].cur_point.weight = n
            uav[n].cur_mode = 'LOCALIZE'
            if uav[n].return_stage != 'DIR_FOUND':
                uav[n].return_stage = 'DIR_FOUND'
                uav[n].to_plume_direction = uav[n].temp_moving_direction
            logs_file.write(f"uav with id {n} continuing localizing,"
                            f" passed Point ({uav[n].cur_point.x},{uav[n].cur_point.y})\n")

        # Если загрязнения в режиме возвращения не обнаружится - выбрано неправильное из двух направлений
        elif uav[n].cur_point.c == 0 and uav[n].cur_mode == 'RETURN_TO_PLUME':
            uav[n].cur_point.weight = n
            if uav[n].return_stage == "STEP_2":
                logs_file.write(f"uav with id {n} continuing returning to plume,"
                                f" direction {uav[n].temp_moving_direction} not valid - choosing against it)\n")
            else:
                logs_file.write(f"uav with id {n} continuing returning to plume,"
                                f"valid direction is {uav[n].temp_moving_direction}\n")


        # Если загрязнения не обнаружено в режиме поиска - зануление текущего веса, переход к следующей точке
        elif uav[n].cur_point.c == 0 and uav[n].cur_mode == 'SEARCH':
            # Зануление веса текущей координаты как у дронов
            uav[n].cur_point.weight = n
            # так и в общем графе
            uav[n].uav_world.points[(int(uav[n].cur_point.x), int(uav[n].cur_point.y))].weight = n
            logs_file.write(f"uav with id {n} continuing SEARCHing\n")
            # uav[n].paint_weights_map()

        print(f'\niter {time_stamp}  for uav id{n} complete\n- - - - - - - - - - - - - - - - - - - - - - -')

    if 0 <= uav_found_plume < number_of_uavs:
        uav_found_plume += number_of_uavs
        for n in range(number_of_uavs):
            if n != uav_found_plume and uav[n].cur_mode == 'SEARCH':
                uav[n].cur_mode = 'REACH'
                logs_file.write(f"uav with id {n} switched mode to 'REACH'")
                uav[n].reach_point = uav[n].cur_point
                logs_file.write(f"uav with id {n} gor reach_point - {uav[n].reach_point}")

    mpl_paint_weights_map(uav, time_stamp, world_global)
    print(
        f'creating image for timestamp t = {time_stamp}, Задержка: {(time.time_ns() - temp_time) / (10 ** 9)}')
    temp_time = time.time_ns()
    time_stamp += 1






















# first_world_uav = World()
# first_world_uav.uav_world_create()
#
# first_uav_id = 0
# first_uav = UAV(
#     id=first_uav_id,
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
#     id=second_uav_id,
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
# print(f"uav with id {first_uav.id} is at position: x = {first_uav.cur_point.x}, y = {first_uav.cur_point.y} ")
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
