"""
Defining objects used in package:
- Graph World {World}, which contains vertexes Point's {Point}
- Vertex, which have coordinates Point{x,y}, plume concentration C{x,y}
- UAV - agent class, defining the methods UAV can perform

"""
import math
from dataclasses import dataclass, field
from math import sqrt
from src.utils.setup_loggers import logger as _logger
from src.utils import ros_commands
from src.world.territory import Point, World
from typing import Any, Dict, List, Tuple

@dataclass
class UAV:
    """Object representing single UAV and his behaviour"""
    id: int  # UAV's id
    uav_world: World
    cur_point: Point
    logs_file: Any
    cur_mode: str  # Текущий режим: 'search' - обход территории, 'localize' - локализация источника загрязнения
    localize_stage: str = "UNKNOWN"
    return_stage: str = "UNKNOWN"
    temp_moving_direction: str = "UNKNOWN"
    anemometer_data: str = "UNKNOWN"
    to_plume_direction: str = "UNKNOWN"
    target_point: Point = None
    reach_point: Point = None
    publisher_obj: Any = None
    time_iterations: Dict[int, int] = field(default_factory=dict)


    uav_compass = {
        'opposite': {
            'WEST': 'EAST',
            'EAST': 'WEST',
            'NORTH': 'SOUTH',
            'SOUTH': 'NORTH'
        },
        'perpendicular': {
            'WEST': ('NORTH', 'SOUTH'),
            'EAST': ('NORTH', 'SOUTH'),
            'NORTH': ('EAST', 'WEST'),
            'SOUTH': ('EAST', 'WEST'),
        }
    }

    def move_to(self, target_point: Point) -> None:
        """Moving to target_point"""
        print(f'UAV with id {self.id} moving to {target_point} from {self.cur_point}')
        self.logs_file.write(f'UAV with id {self.id} moving to {target_point} from {self.cur_point}\n')
        # ros_commands.move_uav(self.id,
        #                       self.cur_point.x,
        #                       self.cur_point.y,
        #                       target_point.x,
        #                       target_point.y)
        self.cur_point = target_point
        print(f"UAV with id {self.id} completed moving to {target_point}")
        self.logs_file.write(f"UAV with id {self.id} completed moving to {target_point}\n")

    def get_target_point_reaching(self):
        """
        логика выбора следующей точки в режиме достижения какой-то из координат
        :return:
        """
        self.move_to_reach_point()

    def move_to_reach_point(self, reach_point: Point = None) -> None:
        """
        Функция для осуществления движения к точке с определенными координатами
        """
        # Проверка на нахождение в режиме движения к точке достижения
        if self.cur_mode != 'REACH':
            # Установка режима и точки, к которой необходимо добраться
            self.reach_point = reach_point
            self.cur_mode = 'REACH'
        else:
            coord_diff = (abs(self.reach_point.x - self.cur_point.x), abs(self.reach_point.y-self.cur_point.y))
            if coord_diff[0] != 0 and coord_diff[1] != 0:
                # moving diagonally first
                self.target_point = self.uav_world.points[self._to_reach_point_direction()]
            else:
                self.target_point = self.uav_world.points[self._to_reach_point_direction()]
            if self.target_point == self.reach_point:
                self.cur_mode = 'SEARCH'

    def _to_reach_point_direction(self) -> Tuple[int, int]:
        """
        Вспомогательная функция для того чтобы получить координаты, в какую сторону необходимо двигаться чтобы
        достичь reach_point
        """
        diff_x = self.reach_point.x - self.cur_point.x
        diff_y = self.reach_point.y - self.cur_point.y

        if diff_x > 0:
            if diff_y == 0:
                return self._get_direction_point('EAST')
            elif diff_y > 0:
                return self._get_direction_point('NORTH_EAST')
            else:
                return self._get_direction_point('SOUTH_EAST')
        elif diff_x < 0:
            if diff_y == 0:
                return self._get_direction_point('WEST')
            elif diff_y > 0:
                return self._get_direction_point('NORTH_WEST')
            else:
                return self._get_direction_point('SOUTH_WEST')
        else:
            return self._get_direction_point('NORTH') if diff_y > 0 else self._get_direction_point('SOUTH')




    def measure_plume(self, sensor_plume: Point) -> None:
        """
        "measuring" plume from cur_point Point and getting concentration "point.c"
        """
        print(f'UAV with id {self.id} scanning Point x = {self.cur_point.x} y = {self.cur_point.y}')
    #   self.logs_file.write(f'UAV with id {self.id} scanning Point x = {self.cur_point.x} y = {self.cur_point.y}\n')
        self.cur_point.c = sensor_plume.c
        print(f"the plume value is c = {self.cur_point.c}")
    #   self.logs_file.write(f"the plume value is c = {self.cur_point.c}\n")

    def measure_wind_direction(self, sensor_wind_direction: Point) -> None:
        """modeling anemometer measurements at cur_point Point and getting wind direction"""
        print(f'UAV with id {self.id} measures wind at Point x = {self.cur_point.x} y = {self.cur_point.y}')
        self.logs_file.write(f'UAV with id {self.id} measures wind at Point '
                             f'x = {self.cur_point.x} y = {self.cur_point.y}\n')
        self.cur_point.wind = sensor_wind_direction.wind
        self.anemometer_data = sensor_wind_direction.wind
        print(f"the wind direction is: {self.cur_point.wind}")
        self.logs_file.write(f"the wind direction is: {self.cur_point.wind}\n")

    def mark_point(self) -> None:
        """function is not used"""
        print(f'Point x = {self.cur_point.x} y = {self.cur_point.y} marked as "checked" by UAV with id {self.id}')
        self.cur_point.is_checked = True

    def calculate_weights(self) -> None:
        """Функция для просчёта карты интересов для каждой точки в момент времени t0 в зависимости от расстояния"""
        for i in range(self.uav_world.world_size):
            for j in range(self.uav_world.world_size):
                if self.uav_world.points[(j, i)].x == self.cur_point.x and self.uav_world.points[(j, i)].y == self.cur_point.y:
                    self.uav_world.points[(j, i)].weight = 0
                else:
                    diff_min = min(abs(self.uav_world.points[(j, i)].x - self.cur_point.x),
                                   abs(self.uav_world.points[(j, i)].y - self.cur_point.y))
                    diff_max = max(abs(self.uav_world.points[(j, i)].x - self.cur_point.x),
                                   abs(self.uav_world.points[(j, i)].y - self.cur_point.y))
                    # Старая модель подсчёта весов без учёта движения по диагонали
                    # self.uav_world.points[(j, i)].weight = max(abs(self.uav_world.points[(j, i)].x -self.cur_point.x),
                    #                                            abs(self.uav_world.points[(j, i)].y -self.cur_point.y))
                    # Новая модель подсчёта весов в зависимости от расстояния
                    self.uav_world.points[(j, i)].weight = (diff_max - diff_min) + (diff_min * sqrt(2))
                    # self.uav_world.points[(j, i)].weight = math.sqrt(
                    #     (self.uav_world.points[(j, i)].x - self.cur_point.x) ** 2
                    #     + (self.uav_world.points[(j, i)].y - self.cur_point.y) ** 2
                    # )
    def merge_weights(self, another_worlds: List[World]):
        """Функция для последовательного перемножения карт весов всех дронов"""
        for n in range(len(another_worlds)):
            for i in range(self.uav_world.world_size):
                for j in range(self.uav_world.world_size):
                    self.uav_world.points[(j, i)].weight = self.uav_world.points[(j, i)].weight * \
                                                           another_worlds[n].points[
                                                               (j, i)].weight

    def get_target_point_searching(self, shift: int = 0):
        """"Головная функция по выбору точки, в которую будет направляться дрон в следующий момент времени"""
        # Получение всех существующих соседних точек и их координат в виде списка
        nearby_points_coords: list = self._get_nearby_points_coords()
        print(f"uav{self.id} at ({self.cur_point.x},{self.cur_point.y}) and nearby points are\n{nearby_points_coords}")
        self.logs_file.write(f"uav{self.id} at ({self.cur_point.x},{self.cur_point.y}) and "
                             f"nearby points are\n{nearby_points_coords}\n")
        # Выбор из всех соседних точек нужной с наибольшим весом
        target_point_coords: Tuple = self._get_target_point(nearby_points_coords, shift)
        print(f'uav{self.id} chosen {target_point_coords} as target point')
        self.logs_file.write(f'uav{self.id} chosen {target_point_coords} as target point\n')
        # Присвоение координат целевой точке в соответствии с расчётами выше
        self.target_point = self.uav_world.points[target_point_coords]

    def _get_target_point(self, nearby_points_coords: list, shift: int = 0) -> Tuple:
        weights_list: List[(int, float)] = []
        for n in range(len(nearby_points_coords)):
            weights_list.append((self.uav_world.points[nearby_points_coords[n]].weight, n))
        weights_list.sort(reverse=True)
        if shift > 0:
            for n in range(shift):
                weights_list.pop(0)
        return nearby_points_coords[weights_list[0][1]]

    def _get_nearby_points_coords(self) -> list:
        existing_points: list = []
        xc, yc = self.cur_point.x, self.cur_point.y
        neighbour_points = [(xc + 1, yc + 1), (xc + 1, yc), (xc + 1, yc - 1), (xc, yc - 1), (xc - 1, yc - 1),
                            (xc - 1, yc), (xc - 1, yc + 1), (xc, yc + 1)]
        for i in range(8):
            if (0 <= neighbour_points[i][0] < self.uav_world.world_size
                    and 0 <= neighbour_points[i][1] < self.uav_world.world_size):
                existing_points.append(neighbour_points[i])
        return existing_points

    def paint_weights_map(self) -> None:
        print(f"weights map for uav with id {self.id}")
        for i in range(self.uav_world.world_size - 1, -1, -1):
            for j in range(self.uav_world.world_size):
                if self.uav_world.points[(j, i)].id == ((self.uav_world.world_size ** 2) - 1) / 2:
                    print("[", end='')
                if self.uav_world.points[(j, i)].weight < 10:
                    print(f"   {self.uav_world.points[(j, i)].weight:.2f}", end='')
                elif self.uav_world.points[(j, i)].weight < 100:
                    print(f"  {self.uav_world.points[(j, i)].weight:.2f}", end='')
                elif self.uav_world.points[(j, i)].weight < 1000:
                    print(f" {self.uav_world.points[(j, i)].weight:.2f}", end='')
                elif self.uav_world.points[(j, i)].weight >= 1000:
                    print(f"{self.uav_world.points[(j, i)].weight:.2f}", end='')
                if self.uav_world.points[(j, i)].id == ((self.uav_world.world_size ** 2) - 1) / 2:
                    print("]", end='')
                print("   ", end='')
                if j == self.uav_world.world_size - 1:
                    print("\n")

    def get_target_point_localization(self):
        """функция для выбора следующей точки движения по алгоритму локализации в соответствующем режиме"""

        # Если стадия локализации - движение против ветра:
        if self.localize_stage == 'MOVE_AGAINST_WIND':
            # Определение направления, в котором осуществляется движение
            if self.anemometer_data == "UNKNOWN":
                moving_direction: str = self._get_moving_direction()
            else:
                moving_direction: str = self.anemometer_data
            # Выбор точки, которая соответствует выбранному направлению движения
            self.target_point = self.uav_world.points[self._get_direction_point(moving_direction)]
            print(f'uav{self.id} found plume and in LOCALIZE mode\nchosen {self.target_point} as target point')
            self.logs_file.write(f'uav{self.id} found plume and in LOCALIZE mode\nchosen {self.target_point}'
                                 f' as target point\n')

        # Если стадия локализации - возвращение к загрязнению:
        if self.localize_stage == 'RETURN_TO_PLUME':
            # Если это первый раз - необходимо определить с какой из сторон находится загрязнение
            if self.to_plume_direction == "UNKNOWN":
                self._get_to_plume_direction()
                print(f"debug 1")
            else:  # если же эта информация уже есть - движение в её сторону
                self.target_point = self.uav_world.points[self._get_direction_point(self.to_plume_direction)]


    def _get_to_plume_direction(self):
        """
        Функция для определения, в какую сторону смещаться дрону если он выйдет за пределы загрязнения
        """
        if self.return_stage == "UNKNOWN":
            # Установка флага для перехода в режим поиска возвращения в загрязнение
            self.return_stage = "STEP_1"  # шаг 1 - выбор одной из точек, либо правильной либо противоположной (избыток)
            self.temp_moving_direction = self._get_to_plume_direction_step_1() # Получение одного из 2 направлений
            self.target_point = self.uav_world.points[self._get_direction_point(self.temp_moving_direction)] # выбор точки

            # Установка флага для перехода к следующему шагу STEP_2
            self.return_stage = "STEP_2"  # шаг 2 - перемещение в одну из точек

        elif self.return_stage == "STEP_2":
            # Если первый выбор был неправильным - значит правильный второй, получаем направление движения
            self.temp_moving_direction = self._get_to_plume_direction_step_2()
            # Здесь придётся делать это через два шага, необходимо разработать функцию перемещающу дрон к точке
            # с определенными координатами, пока этого нет - костыли и заглушки
            self.target_point = self.uav_world.points[self._get_direction_point(self.temp_moving_direction)] # выбор точки
            # Установка флага для перехода к следующему шагу STEP_3
            self.return_stage = "STEP_3"  # шаг 3 - возвращение к загрязнению
            # Теперь известно, что направление - противоположное
            self.to_plume_direction = self._get_to_plume_direction_step_2()

        elif self.return_stage == "STEP_3":
            # Окончательное возвращение к загрязнению. Нам известно и направление и всё что нужно
            self.target_point = self.uav_world.points[self._get_direction_point(self.temp_moving_direction)]

    def _get_to_plume_direction_step_1(self) -> str:
        """
        ВНИМАНИЕ! ЗАГЛУШКА! ТРЕБУЕТСЯ РАЗРАБОТКА
        Функция для определения одного из двух перпенидкулярных направлений, в которых можно продолжить движение
        """
        print(f"debug 3")
        return self.uav_compass['perpendicular'][self.anemometer_data][0]

    def _get_to_plume_direction_step_2(self) -> str:
        """
        ВНИМАНИЕ! ЗАГЛУШКА! ТРЕБУЕТСЯ РАЗРАБОТКА
        Функция для определения одного из двух перпенидкулярных направлений, в которых можно продолжить движение
        """
        return self.uav_compass['perpendicular'][self.anemometer_data][1]

    def _get_moving_direction(self) -> str:
        """
        Функция для определения направления движения.
        В данный момент необходимо выбрать направление противоположное направлению ветра
        Т.к направление ветра "west" - означает, что ветер "дует с запада", значит направление движения
        дрона должно быть именно на запад. Отсюда направление задается и равно направлению ветра из датчика
        анемометра, что уже известно - но данная функция может быть изменена
        """
        return self.cur_point.wind

    def _get_direction_point(self, direction: str) -> tuple[int, int]:
        """
        :param direction: принимает на вход необходимое направление движения
        :return: возвращает координаты точки по заданному направлению
        """
        if direction == 'EAST':
            return self.cur_point.x + 1, self.cur_point.y
        elif direction == 'WEST':
            return self.cur_point.x - 1, self.cur_point.y
        elif direction == 'NORTH':
            return self.cur_point.x, self.cur_point.y + 1
        elif direction == 'SOUTH':
            return self.cur_point.x, self.cur_point.y - 1
        elif direction == 'NORTH_EAST':
            return self.cur_point.x + 1, self.cur_point.y + 1
        elif direction == 'NORTH_WEST':
            return self.cur_point.x - 1, self.cur_point.y + 1
        elif direction == 'SOUTH_WEST':
            return self.cur_point.x - 1, self.cur_point.y - 1
        elif direction == 'SOUTH_EAST':
            return self.cur_point.x + 1, self.cur_point.y - 1