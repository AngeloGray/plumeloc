from src.world.territory import Point, World
from src.objects import UAV


UAV_INITIAL_POSITIONS ={
    0: (0, 0)
}

world_uav = World()
world_uav.world_create()

cur_uav_id = 0
cur_uav = UAV(
    id_=cur_uav_id,
    cur_point=world_uav.world_points[UAV_INITIAL_POSITIONS[cur_uav_id]]
)
print(f"uav with id {cur_uav.id_} is at position: x = {cur_uav.cur_point.x}, y = {cur_uav.cur_point.y} ")

world_plume = World()
world_plume.world_create()
world_plume.plume_gen()

# world_plume.world_paint()
print("meow")
# world_uav.world_paint()
cur_uav.move_to(world_uav.world_points[(4, 4)])
print("meow")
cur_uav.plume_measure(world_plume.world_points[(cur_uav.cur_point.x, cur_uav.cur_point.y)])
print("meow")