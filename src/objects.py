"""
Defining objects used in package:
- Graph {G}, which contains vertexes {V}
- Vertex, which have coordinates V{x,y}, plume concentration C{x,y}
- UAV - agent class, defining the methods UAV can perform

"""
from dataclasses import dataclass
from src.utils.setup_loggers import logger as _logger
from src.utils import ros_commands
from src.world.territory import Point, World

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
    cur_point: Point

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

    def plume_measure(self, sensor_plume: Point):
        print(f'UAV with id {self.id_} scanning Point x = {self.cur_point.x} y = {self.cur_point.y}')
        self.cur_point.c = sensor_plume.c
        print(f"the plume value is c = {self.cur_point.c}")
