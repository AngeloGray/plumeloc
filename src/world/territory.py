"""
This file specifies the world as territory where UAV's and plume are
placed. It has shape of square with size of N. Separated into similar
subsquares with coordinates {x,y} and plume concentration values V{x.y}
"""
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from src.config import TERRITORY_SIZE, PLUME_SIZE, WIND_DIRECTION


@dataclass
class Point:
    """Defines point object which is included in world dictionary"""
    # coords: Coords
    id: int
    x: float
    y: float
    wind: str
    c: float = 0.0
    is_checked: bool = False
    weight: float = 0


@dataclass
class World:
    points: Dict[Tuple[int, int], Point] = field(default_factory=dict)
    world_size: int = TERRITORY_SIZE
    plume_size: int = PLUME_SIZE
    plume_location: str = "CENTRAL"
    wind_direction: str = WIND_DIRECTION

    def _set_coords(self) -> None:
        point_id = 0
        for i in range(self.world_size):
            for j in range(self.world_size):
                cur_point = Point(id=point_id, x=j, y=i, wind=self.wind_direction)
                self.points[(j, i)] = cur_point
                point_id += 1

    def _set_coords_uav(self) -> None:
        point_id = 0
        for i in range(self.world_size):
            for j in range(self.world_size):
                cur_point = Point(id=point_id, x=j, y=i, wind="UNKNOWN")
                self.points[(j, i)] = cur_point
                point_id += 1

    def plume_gen(self):
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

    def _plume_gen_dir_central(self):
        pass

    def _plume_gen_dir_north(self):
        pass

    def _plume_gen_dir_west(self):
        xc = yc = int ((self.world_size - 1) / 2)
        lij = 4 # гиперпараметр
        lij_half = int(lij / 2)
        lijk = int(lij / 2)  # гиперпараметр lijk = 2
        lijk_half = int(lijk / 2)
        li0 = lij + lijk # гиперпараметр li0 = 6, уменьшается на 2 каждый раз
        Lli = 11 # гиперпараметр для изначального лепестка Ll1 = 11, увеличивается на 4 каждый раз

        for leaf_id in range(0, 5):
            if leaf_id == 0:
                self.points[(xc, yc)].c = 1 # точка с источником

            if leaf_id == 1:
                for i in range(0, leaf_id + 1):
                    if i == 0:
                        for m in range(1, Lli + 1): # от 1 до 11
                            self.points[(xc + m, yc)].c = (1 - 0.25 * leaf_id)
                    if i == 1:
                        for m in range(li0 + (lij * (i - 1)) + lijk_half, li0 + (i * lij) + 1):  # от 7 до 10 сверху и снизу
                            self.points[(xc + m, yc + i)].c = (1 - 0.25 * leaf_id)
                            self.points[(xc + m, yc - i)].c = (1 - 0.25 * leaf_id)

            if leaf_id == 2:
                Lli += 4 # Изменение в соответствии с моделью
                li0 -= 2  # Изменение в соответствии с моделью
                for i in range(0, leaf_id + 1):
                    if i == 0:
                        for m in range(Lli - lij + 1, Lli + 1): # от 12 до 15 - середина
                            self.points[(xc + m, yc)].c = (1 - 0.25 * leaf_id)
                    if i == 1:
                        # от 5,6 & 11,12,13,14 для верхней и нижней части лепестка
                        for m in range(li0 + lijk_half, li0 + lij_half + 1):  # 5, 6
                            self.points[(xc + m, yc + i)].c = (1 - 0.25 * leaf_id)
                            self.points[(xc + m, yc - i)].c = (1 - 0.25 * leaf_id)
                        for m in range(Lli - lij, (Lli - lijk_half) + 1):  # 11, 12, 13, 14
                            self.points[(xc + m, yc + i)].c = (1 - 0.25 * leaf_id)
                            self.points[(xc + m, yc - i)].c = (1 - 0.25 * leaf_id)
                    if i == 2:
                        for m in range(li0 + (lij * (i - 1)) + lijk_half, li0 + (i * lij) + 1):  # от 9 до 12
                            self.points[(xc + m, yc + i)].c = (1 - 0.25 * leaf_id)
                            self.points[(xc + m, yc - i)].c = (1 - 0.25 * leaf_id)

            if leaf_id == 3:
                Lli += 4  # Изменение в соответствии с моделью
                li0 -= 2  # Изменение в соответствии с моделью
                for i in range(0, leaf_id + 1):
                    if i == 0:
                        for m in range(Lli - lij + 1, Lli + 1):  # от 16 до 19 - середина
                            self.points[(xc + m, yc)].c = (1 - 0.25 * leaf_id)
                    if i == 1:
                        # от 3,4 & 15,16,17,18 для верхней и нижней части лепестка
                        for m in range(li0 + (lij * (i - 1)) + lijk_half, li0 + (lij * (i - 1)) + lij_half + 1):  # 3, 4
                            self.points[(xc + m, yc + i)].c = (1 - 0.25 * leaf_id)
                            self.points[(xc + m, yc - i)].c = (1 - 0.25 * leaf_id)
                        for m in range(Lli - lij - lijk * (i - 1), (Lli - lijk_half - lijk * (i - 1)) + 1):  #15, 16, 17, 18
                            self.points[(xc + m, yc + i)].c = (1 - 0.25 * leaf_id)
                            self.points[(xc + m, yc - i)].c = (1 - 0.25 * leaf_id)
                    if i == 2:
                        # от 7, 8 & 13, 14, 15 ,16 для верхней и нижней части лепестка
                        for m in range(li0 + (lij * (i - 1)) + lijk_half, li0 + (lij * (i - 1)) + lij_half + 1):  # 7, 8
                            self.points[(xc + m, yc + i)].c = (1 - 0.25 * leaf_id)
                            self.points[(xc + m, yc - i)].c = (1 - 0.25 * leaf_id)
                        for m in range(Lli - lij - lijk * (i - 1), (Lli - lijk_half - lijk * (i - 1)) + 1):  # 13, 14, 15, 16
                            self.points[(xc + m, yc + i)].c = (1 - 0.25 * leaf_id)
                            self.points[(xc + m, yc - i)].c = (1 - 0.25 * leaf_id)
                    if i == 3:
                        for m in range(li0 + (lij * (i - 1)) + lijk_half, li0 + (i * lij) + 1):  # от 11 до 14
                            self.points[(xc + m, yc + i)].c = (1 - 0.25 * leaf_id)
                            self.points[(xc + m, yc - i)].c = (1 - 0.25 * leaf_id)








                





    def _plume_gen_dir_east(self):
        pass

    def _plume_gen_dir_south(self):
        pass

    def _plume_gen_dir_custom(self):
        pass

    def plume_gen_directed(self):
        if self.plume_location == "CENTRAL":
            self._plume_gen_dir_central()
        elif self.plume_location == "NORTH":
            self._plume_gen_dir_north()
        elif self.plume_location == "WEST":
            self._plume_gen_dir_west()
        elif self.plume_location == "EAST":
            self._plume_gen_dir_east()
        elif self.plume_location == "SOUTH":
            self._plume_gen_dir_south()
        elif self.plume_location == "CUSTOM":
            self._plume_gen_dir_custom()

    def world_create(self):
        self._set_coords()
        self.plume_gen()

    def test_world_create(self):
        self._set_coords()
        self._plume_gen_dir_west()
        self.world_paint()

    def uav_world_create(self):
        self._set_coords_uav()

    def get_point(self, _x: int, _y: int):
        print(f"the coordinates for point with id {self.points[(_x, _y)].id} are:\nx = {self.points[(_x, _y)].x}"
              f"\ny = {self.points[(_x, _y)].y}")

    def world_paint(self):
        for i in range(self.world_size-1, 0, -1):
            for j in range(self.world_size):
                print(f"{self.points[(j, i)].c}   ", end='')
                if j == self.world_size - 1:
                    print("\n")

# world1 = World(world_size=21, plume_size=4)
# world1.world_create()
# world1.plume_gen()
# world1.get_point(0, 5)
# print(world1.points)
# world1.world_paint()
