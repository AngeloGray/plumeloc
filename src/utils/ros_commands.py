import rospy
from std_msgs.msg import String


def move_uav(id_ : int, x_cur: float, y_cur: float, x_tar: float, y_tar: float) -> None:
    """"
    Logic for uav moving from cur_vertex{x_cur, y_cur} to -> target_vertex{x_tar, y_tar}
    """
    pass


def initialize_publisher(publisher_id):
    """Initialize publisher"""
    return rospy.Publisher(f"message_topic_{publisher_id}", String, queue_size=10)


def send_message(publisher, data):
    """Send message"""
    rate = rospy.Rate(1)
    for _ in range(10):
        publisher.publish(data)
        rate.sleep()


rospy.init_node('command_node', anonymous=True)
