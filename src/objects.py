"""
Defining objects used in package:
- Graph {G}, which contains vertexes {V}
- Vertex, which have coordinates V{x,y}, plume concentration C{x,y}
- UAV - agent class, defining the methods UAV can perform

"""
from dataclasses import dataclass, field
from math import sqrt
from src.utils.setup_loggers import logger as _logger
from src.utils import ros_commands
from src.world.territory import Point, World
from typing import Any, Dict, List, Tuple


# @dataclass
# class Vertex:
#     id_: int
#     x: float
#     y: float
#     plume_value: float


@dataclass
class UAV:
    """Defining UAV-agent methods and attributes"""
    id_: int  # UAV's id
    # cur_vertex: Vertex
    uav_world: World
    cur_point: Point
    cur_mode: str  # Текущий режим: 'search' - обход территории, 'localize' - локализация источника загрязнения
    anemometer_data: str
    spec_flag: int
    target_point: Point = None
    publisher_obj: Any = None
    time_iterations: Dict[int, int] = field(default_factory=dict)


    # def move_to(self, target_vertex: Vertex) -> None:
    #     """Moving to target_vertex"""
    #     _logger.info(f'UAV with id {self.id_} moving to {target_vertex} from {self.cur_vertex}')
    #     ros_commands.move_uav(self.id_,
    #                           self.cur_vertex.x,
    #                           self.cur_vertex.y,
    #                           target_vertex.x,
    #                           target_vertex.y)
    #     self.cur_vertex = target_vertex
    #     _logger.info(f"UAV with id {self.id_} completed moving to {target_vertex}")
    def move_to(self, target_point: Point) -> None:
        """Moving to target_vertex"""
        print(f'UAV with id {self.id_} moving to {target_point} from {self.cur_point}')
        # ros_commands.move_uav(self.id_,
        #                       self.cur_point.x,
        #                       self.cur_point.y,
        #                       target_point.x,
        #                       target_point.y)
        self.cur_point = target_point
        print(f"UAV with id {self.id_} completed moving to {target_point}")

    def measure_plume(self, sensor_plume: Point) -> None:
        print(f'UAV with id {self.id_} scanning Point x = {self.cur_point.x} y = {self.cur_point.y}')
        self.cur_point.c = sensor_plume.c
        print(f"the plume value is c = {self.cur_point.c}")

    def measure_wind_direction(self, sensor_wind_direction: Point) -> None:
        print(f'UAV with id {self.id_} measures wind at Point x = {self.cur_point.x} y = {self.cur_point.y}')
        self.cur_point.wind = sensor_wind_direction.wind
        print(f"the wind direction is c = {self.cur_point.wind}")

    def mark_point(self) -> None:
        print(f'Point x = {self.cur_point.x} y = {self.cur_point.y} marked as "checked" by UAV with id {self.id_}')
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

    def merge_weights(self, another_worlds: List[World]):
        for n in range(len(another_worlds)):
            for i in range(self.uav_world.world_size):
                for j in range(self.uav_world.world_size):
                    self.uav_world.points[(j, i)].weight = self.uav_world.points[(j, i)].weight * \
                                                           another_worlds[n].points[
                                                               (j, i)].weight

    def get_target_point(self, shift: int = 0):
        nearby_points_coords: list = self._get_nearby_points_coords()
        print(f"uav{self.id_} at ({self.cur_point.x},{self.cur_point.y}) and nearby points are\n{nearby_points_coords}")
        target_point_coords: Tuple = self._get_target_point(nearby_points_coords, shift)
        print(f'uav{self.id_} chosen {target_point_coords} as target point')
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
        print(f"weights map for uav with id {self.id_}")
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

    def move_to_direction(self, direction: str) -> tuple[int, int]:
        if


    def get_target_point_localization(self):
        if self.cur_point.c != 0 and self.spec_flag == 0:
            direction = self.anemometer_data
            self.target_point = self.uav_world.points[self.move_to_direction(direction)]
