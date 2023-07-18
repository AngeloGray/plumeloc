"""
This file specifies the world as territory where UAV's and plume are
placed. It has shape of square with size of N. Separated into similar
subsquares with coordinates {x,y} and plume concentration values V{x.y}
"""
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any
from math import sqrt

from src.config import TERRITORY_SIZE, PLUME_SIZE, WIND_DIRECTION, MASHTAB_COEF, PLUME_LOCATION, PLUME_CUSTOM_COORDS


@dataclass
class Point:
    """Defines point object which is included in world dictionary"""
    # coords: Coords
    id: int
    x: int
    y: int
    wind: str
    c: float = 0.0
#    is_checked: bool = False
    weight: float = 0


@dataclass
class World:
    logs_file: Any
    points: Dict[Tuple[int, int], Point] = field(default_factory=dict)
    world_size: int = TERRITORY_SIZE
    plume_size: int = PLUME_SIZE
    plume_location: str = "CENTRAL"
    wind_direction: str = WIND_DIRECTION

    # Основные методы:
    def world_create(self) -> None:
        """
        Основной метод, который исполняет последовательность действий для реализации объекта World
        """
        self._set_coords()  # Формирование графа World из объектов Point
        self.plume_gen()  # Формирование загрязнения в соответствии с параметрами из config
        self.world_paint()  # Вывод получившегося графа в консоль.

    def world_create_uav(self) -> None:
        """
        Метод формирования подграфа для дрона UAV
        Намеренно выведен как отдельный для внесения изменений, если таковые потребуются
        """
        self._set_coords_uav()

    def plume_gen(self) -> None:
        """
        Основная фукнция для определения алгоритма создания загрязнения и его интеграции в глобальный граф.
        """
        # Выбор одной из двух моделей загрязнения в зависимости от наличия ветра
        if WIND_DIRECTION != 'STILL':
            temp_points = self._set_temp_coords(mode='PLUME')  # Создание промежуточного графа, формируется загрязнение
            # Алгоритм по формированию загрязнения и присвоению его глобальному графу следующий:
            # 1) Формируем загрязнение необходимого размера:
            self.points = self._plume_gen_directed(temp_points)





            # [debug]
           # self._plume_gen_directed()
            self._plume_rotate()



        else:
            # [В разработке] Экспериментальная фича, надобность в которой находится под вопросом
            pass




    def _set_coords(self) -> None:
        point_id = 0
        for i in range(self.world_size):
            for j in range(self.world_size):
                cur_point = Point(id=point_id, x=j, y=i, wind=self.wind_direction)
                self.points[(j, i)] = cur_point
                point_id += 1

    def _set_temp_coords(self, mode: str = 'DEFAULT') -> Dict[Tuple[int, int], Point]:
        points_temp: Dict[Tuple[int, int], Point] = {}
        point_id = 0
        # Допуск, что граф - квадрат с одинаковыми сторонами
        # Требуется доработка и рефакторинг для использования отличных от квадрата форм - т.к. модель использует только
        # механизм для прохода по квадратным графам
        # Здесь 24 - размер минимальной конфигурации загрязнения с коэффициентом 1
        # [Требуется доработка нахождения зависимости, а не хардкодинг]
        size = 53 if mode == 'PLUME' else self.world_size
        for i in range(size):
            for j in range(size):
                cur_point = Point(id=point_id, x=j, y=i, wind=self.wind_direction)
                points_temp[(j, i)] = cur_point
                point_id += 1
        return points_temp

    def _set_coords_uav(self) -> None:
        point_id = 0
        for i in range(self.world_size):
            for j in range(self.world_size):
                cur_point = Point(id=point_id, x=j, y=i, wind="UNKNOWN")
                self.points[(j, i)] = cur_point
                point_id += 1

    def _plume_gen_normal(self):
        """
        [Неиспользуемо] Экспериментальная функция
        """
        if self.plume_location == "CENTRAL":
            xc = yc = (self.world_size - 1) / 2
            plume_value: float = 1.0
            for r in range(self.plume_size):
                for i in range(self.world_size):
                    for j in range(self.world_size):
                        if (abs(self.points[(j, i)].x - xc) == r and abs(self.points[(j, i)].y - yc) <= r) or (abs(self.points[(j, i)].x - xc) <= r and abs(self.points[(j, i)].y - yc) == r):
                            self.points[(i, j)].c = plume_value
                plume_value -= 1.0 / (self.plume_size + 1)
                plume_value = round(plume_value, 1)

    def _plume_gen_directed(self, points: Dict[Tuple[int, int], Point]) -> Dict[Tuple[int, int], Point]:
        Ms = MASHTAB_COEF
        xc = yc = int((self.world_size - 1) / 2)
        lij = 4 * Ms  # гиперпараметр
        lij_half = int(lij / 2)
        lijk = int(lij / 2)  # гиперпараметр lijk = 2
        lijk_half = int(lijk / 2)
        li0 = lij + lijk  # гиперпараметр li0 = 6, уменьшается на 2 каждый раз
        Lli = li0 + lij + 1  # гиперпараметр для изначального лепестка Ll1 = 11, увеличивается на 4 каждый раз

        for leaf_id in range(0, 5):
            if leaf_id == 0:
                points[(xc, yc)].c = 1  # точка с источником

            if leaf_id == 1:
                for i in range(0, leaf_id + 1):
                    if i == 0:
                        for m in range(1, Lli + 1): # от 1 до 11
                            points[(xc + m, yc)].c = (1 - 0.25 * leaf_id)
                    if i == 1:
                        for m in range(li0 + (lij * (i - 1)) + 1, li0 + (i * lij) + 1):  # от 7 до 10 сверху и снизу
                            points[(xc + m, yc + i)].c = (1 - 0.25 * leaf_id)
                            points[(xc + m, yc - i)].c = (1 - 0.25 * leaf_id)

            if leaf_id == 2:
                Lli += lij # Изменение в соответствии с моделью
                li0 -= lijk  # Изменение в соответствии с моделью
                for i in range(0, leaf_id + 1):
                    if i == 0:
                        for m in range(Lli - lij + 1, Lli + 1): # от 12 до 15 - середина
                            points[(xc + m, yc)].c = (1 - 0.25 * leaf_id)
                    if i == 1:
                        # от 5,6 & 11,12,13,14 для верхней и нижней части лепестка
                        for m in range(li0 + 1, li0 + lij_half + 1):  # 5, 6
                            points[(xc + m, yc + i)].c = (1 - 0.25 * leaf_id)
                            points[(xc + m, yc - i)].c = (1 - 0.25 * leaf_id)
                        for m in range(Lli - lij, (Lli - 1) + 1):  # 11, 12, 13, 14
                            points[(xc + m, yc + i)].c = (1 - 0.25 * leaf_id)
                            points[(xc + m, yc - i)].c = (1 - 0.25 * leaf_id)
                    if i == 2:
                        for m in range(li0 + (lij * (i - 1)) + 1, li0 + (i * lij) + 1):  # от 9 до 12
                            points[(xc + m, yc + i)].c = (1 - 0.25 * leaf_id)
                            points[(xc + m, yc - i)].c = (1 - 0.25 * leaf_id)

            if leaf_id == 3:
                Lli += lij  # Изменение в соответствии с моделью
                li0 -= lijk  # Изменение в соответствии с моделью
                for i in range(0, leaf_id + 1):
                    if i == 0:
                        for m in range(Lli - lij + 1, Lli + 1):  # от 16 до 19 - середина
                            points[(xc + m, yc)].c = (1 - 0.25 * leaf_id)
                    if i == 1:
                        # от 3,4 & 15,16,17,18 для верхней и нижней части лепестка
                        for m in range(li0 + (lij * (i - 1)) + 1, li0 + (lij * (i - 1)) + lij_half + 1):  # 3, 4
                            points[(xc + m, yc + i)].c = (1 - 0.25 * leaf_id)
                            points[(xc + m, yc - i)].c = (1 - 0.25 * leaf_id)
                        for m in range(Lli - lij - lijk * (i - 1), (Lli - 1 - 1 * (i - 1)) + 1):  #15, 16, 17, 18
                            points[(xc + m, yc + i)].c = (1 - 0.25 * leaf_id)
                            points[(xc + m, yc - i)].c = (1 - 0.25 * leaf_id)
                    if i == 2:
                        # от 7, 8 & 13, 14, 15 ,16 для верхней и нижней части лепестка
                        for m in range(li0 + (lij * (i - 1)) + 1, li0 + (lij * (i - 1)) + lij_half + 1):  # 7, 8
                            points[(xc + m, yc + i)].c = (1 - 0.25 * leaf_id)
                            points[(xc + m, yc - i)].c = (1 - 0.25 * leaf_id)
                        for m in range(Lli - lij - lijk * (i - 1), (Lli - 1 - lijk * (i - 1)) + 1):  # 13, 14, 15, 16
                            points[(xc + m, yc + i)].c = (1 - 0.25 * leaf_id)
                            points[(xc + m, yc - i)].c = (1 - 0.25 * leaf_id)
                    if i == 3:
                        for m in range(li0 + (lij * (i - 1)) + 1, li0 + (i * lij) + 1):  # от 11 до 14
                            points[(xc + m, yc + i)].c = (1 - 0.25 * leaf_id)
                            points[(xc + m, yc - i)].c = (1 - 0.25 * leaf_id)

            if leaf_id == 4:
                Lli += lij  # Изменение в соответствии с моделью
                li0 -= lijk  # Изменение в соответствии с моделью
                for i in range(0, leaf_id + 1):
                    if i == 0:
                        for m in range(Lli - lij + 1, Lli + 1):  # от 20 до 23 - середина
                            points[(xc + m, yc)].c = 0.1
                    if i == 1:
                        # от 1,2 & 19, 20, 21, 22 для верхней и нижней части лепестка
                        for m in range(li0 + (lij * (i - 1)) + 1, li0 + (lij * (i - 1)) + lij_half + 1):  #1 2
                            points[(xc + m, yc + i)].c = 0.1
                            self.points[(xc + m, yc - i)].c = 0.1
                        for m in range(Lli - lij - lijk * (i - 1),
                                       (Lli - 1 - lijk * (i - 1)) + 1):  # 19, 20, 21, 22
                            points[(xc + m, yc + i)].c = 0.1
                            points[(xc + m, yc - i)].c = 0.1
                    if i == 2:
                        # от 5, 6 & 17, 18, 19, 20 для верхней и нижней части лепестка
                        for m in range(li0 + (lij * (i - 1)) + 1, li0 + (lij * (i - 1)) + lij_half + 1):  # 5, 6
                            points[(xc + m, yc + i)].c = 0.1
                            points[(xc + m, yc - i)].c = 0.1
                        for m in range(Lli - lij - lijk * (i - 1),
                                       (Lli - 1 - lijk * (i - 1)) + 1):  # 17, 18, 19, 20
                            points[(xc + m, yc + i)].c = 0.1
                            points[(xc + m, yc - i)].c = 0.1
                    if i == 3:
                        # от 9, 10 & 15, 16, 17, 18 для верхней и нижней части лепестка
                        for m in range(li0 + (lij * (i - 1)) + 1, li0 + (lij * (i - 1)) + lij_half + 1):  # 9,10
                            points[(xc + m, yc + i)].c = 0.1
                            points[(xc + m, yc - i)].c = 0.1
                        for m in range(Lli - lij - lijk * (i - 1),
                                       (Lli - 1 - lijk * (i - 1)) + 1):  # 15, 16, 17, 18
                            points[(xc + m, yc + i)].c = 0.1
                            points[(xc + m, yc - i)].c = 0.1
                    if i == 4:
                        for m in range(li0 + (lij * (i - 1)) + 1, li0 + (i * lij) + 1):  # от 13 до 16
                            points[(xc + m, yc + i)].c = 0.1
                            points[(xc + m, yc - i)].c = 0.1

        return points

    def _plume_gen_dir_west_exp(self):
        xc = yc = int ((self.world_size - 1) / 2)
        lij = 4 # гиперпараметр
        lij_half = int(lij / 2)
        lijk = int(lij / 2)  # гиперпараметр lijk = 2
        lijk_half = int(lijk / 2)
        li0 = lij + lijk # гиперпараметр li0 = 6, уменьшается на 2 каждый раз
        Lli = 11 # гиперпараметр для изначального лепестка Ll1 = 11, увеличивается на 4 каждый раз
        for leaf_id in range(0, 5):
            if leaf_id == 0:
                self.points[(xc, yc)].c = 1  # точка с источником
            else:
                for kl in range(0, leaf_id + 1):
                    # Начальная стадия - отрост середины
                    if kl == 0:
                        if leaf_id == 1:
                            for m in range(1, Lli + 1):  # середина для первого лепестка от 1 до 11
                                self.points[(xc + m, yc)].c = (1 - (0.1 * leaf_id))
                        else:
                            for m in range(Lli - lij + 1, Lli + 1):  # середина для остальных
                                self.points[(xc + m, yc)].c = (1 - 0.1 * leaf_id)
                    # Серединная стадия
                    if leaf_id - kl > 0:
                        for m in range(li0 + lijk_half, li0 + lij_half + 1):
                            self.points[(xc + m, yc + kl)].c = (1 - 0.1 * leaf_id)
                            self.points[(xc + m, yc - kl)].c = (1 - 0.1 * leaf_id)
                        for m in range(Lli - lij, (Lli - lijk_half) + 1):
                            self.points[(xc + m, yc + kl)].c = (1 - 0.1 * leaf_id)
                            self.points[(xc + m, yc - kl)].c = (1 - 0.1 * leaf_id)
                    # Конечная стадия - края лепестка
                    if kl == leaf_id:
                        for m in range(li0 + (lij * (kl - 1)) + lijk_half, li0 + (kl * lij) + 1):
                            self.points[(xc + m, yc + kl)].c = (1 - 0.1 * leaf_id)
                            self.points[(xc + m, yc - kl)].c = (1 - 0.1 * leaf_id)
            # Обновление гиперпараметров
            if leaf_id != 0:
                Lli += 4  # Изменение в соответствии с моделью
                li0 -= 2  # Изменение в соответствии с моделью
            else:
                pass

    def _plume_gen_dir_north(self):
        """
        Направление ветра - NORTH (Север), загрязнение направлено вниз
        1) генерируем направленное направо WEST
        2) поворачиваем трижды против часовой стрелки
        """
        self._plume_gen_directed()
        self._plume_rotate()
        self._plume_rotate()
        self._plume_rotate()

    def _plume_gen_dir_east(self) -> None:
        """
        Направление ветра - EAST (Восток), загрязнение направлено налево
        1) генерируем направленное направо WEST
        2) поворачиваем дважды против часовой стрелки
        """
        self._plume_gen_directed()
        self._plume_rotate()
        self._plume_rotate()

    def _plume_gen_dir_south(self):
        """
                Направление ветра - SOUTH (Юг), загрязнение направлено вверх
                1) генерируем направленное направо WEST
                2) поворачиваем против часовой стрелки
                """
        self._plume_gen_directed()
        self._plume_rotate()

    def _plume_gen_loc_custom(self):
        pass

    def _plume_gen_loc_central(self):
        self._plume_gen_directed()

    def _plume_gen_loc_west(self):
        pass

    def _plume_gen_loc_east(self):
        pass

    def _plume_gen_loc_south(self):
        pass

    def _plume_gen_loc_north(self):
        pass

    def _plume_rotate(self):
        points_temp = self._set_temp_coords()
        xc = yc = int ((self.world_size - 1) / 2)
        for i in range(self.world_size - 1, 0, -1):
            for j in range(self.world_size):
                points_temp[(xc - (i - yc), j)].c = self.points[(j, i)].c
        for i in range(self.world_size - 1, 0, -1):
            for j in range(self.world_size):
                self.points[(j, i)].c = points_temp[(j, i)].c

    def _plume_gen_directed_(self):
        if WIND_DIRECTION == 'WEST':
            self._plume_gen_directed()
        elif WIND_DIRECTION == 'EAST':
            self._plume_gen_dir_east()
        elif WIND_DIRECTION == 'NORTH':
            self._plume_gen_dir_north()
        elif WIND_DIRECTION == 'SOUTH':
            self._plume_gen_dir_south()

    def get_point(self, _x: int, _y: int):
        print(f"the coordinates for point with id {self.points[(_x, _y)].id} are:\nx = {self.points[(_x, _y)].x}"
              f"\ny = {self.points[(_x, _y)].y}")

    def world_paint_old(self):
        for i in range(self.world_size-1, 0, -1):
            for j in range(self.world_size):
                print(f"{self.points[(j, i)].c}    ", end='')
                if j == self.world_size - 1:
                    print("\n")

    def world_paint(self) -> None:
        print(f"C's map for world")
        for i in range(self.world_size - 1, -1, -1):
            for j in range(self.world_size):
                if self.points[(j, i)].c == 1:
                    print(f"{self.points[(j, i)].c}", end='   ')
                elif self.points[(j, i)].c * 100 % 10 == 0:
                    print(f"{self.points[(j, i)].c}", end=' ')
                elif self.points[(j, i)].c * 100 % 10 != 0:
                    print(f"{self.points[(j, i)].c}", end='')
                print("  ", end='')
                if j == self.world_size - 1:
                    print("\n")
# world1 = World(world_size=21, plume_size=4)
# world1.world_create()
# world1.plume_gen()
# world1.get_point(0, 5)
# print(world1.points)
# world1.world_paint()
