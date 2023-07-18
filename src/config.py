"""
Config file for specifying various simulation parameters

"""

TERRITORY_SIZE: int = 101  # Минимальная конфигурация загрязнения занимает размер в 24 - рекомендуется как минимум 49
MASHTAB_COEF: int = 2  # Коэффициент увеличения размеров загрязнения (от 1)
PLUME_SIZE: float = 5  # Параметр регулирующий размер загрязнения имеющего нормальную форму - без ветра. ( от 3)
WIND_DIRECTION: str = 'SOUTH'  # Одна из 4 сторон света: WEST, EAST, NORTH, WEST / 'STILL' - без ветра, нормальная форма
PLUME_LOCATION: str = 'CENTRAL'  # Какой-то из краёв 'WEST', 'EAST', центр 'CENTRAL' / Кастоные координаты: 'CUSTOM'
PLUME_CUSTOM_COORDS: tuple[int, int] = (26, 26)  # Кортеж с координатами (x, y)
NUM_OF_UAVS: int = 4  # Количество дронов
UAV_INITIAL_POSITIONS = {  # Словарь с изначальными позициями и айдишниками дронов. (!) Должны начинаться с нуля
    0: (0, 0),
    1: (5, 0),
    2: (0, 5),
    3: (5, 5)
}
INIT_TIME_STAMP: int = 30  # Начальный момент времени, с которого будет осуществляться визуализация
