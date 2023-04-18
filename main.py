from time import sleep
from src.utils import ros_commands
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
    cur_point=world_uav.points[UAV_INITIAL_POSITIONS[cur_uav_id]],
    publisher_obj=ros_commands.initialize_publisher(cur_uav_id)

)
world_global = World()
world_global.world_create()
world_global.plume_gen()

print(f"uav with id {cur_uav.id_} is at position: x = {cur_uav.cur_point.x}, y = {cur_uav.cur_point.y} ")
cur_uav.measure_plume(world_global.points[(int(cur_uav.cur_point.x), int(cur_uav.cur_point.y))])
cur_uav.mark_point()


# world_global.world_paint()
print("meow")
# world_uav.world_paint()
cur_uav.move_to(world_uav.points[(4, 4)])
print("meow")
cur_uav.measure_plume(world_global.points[(int(cur_uav.cur_point.x), int(cur_uav.cur_point.y))])
cur_uav.mark_point()
print("meow")
while True:
    sleep(1)
    cur_uav.post_to_chanel("Ready")