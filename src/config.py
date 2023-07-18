"""
Config file for specifying various simulation parameters

"""

TERRITORY_SIZE: int = 53  # Минимальная конфигурация загрязнения занимает размер в 24 - рекомендуется как минимум 49
MASHTAB_COEF: int = 1  # Коэффициент увеличения размеров загрязнения (от 1)
PLUME_SIZE: float = 5  # Параметр регулирующий размер загрязнения имеющего нормальную форму - без ветра. ( от 3)
WIND_DIRECTION: str = 'EAST'  # Одна из 4 сторон света: WEST, EAST, NORTH, WEST / 'STILL' - без ветра, нормальная форма
PLUME_LOCATION: str = 'CUSTOM'  # Какой-то из краёв 'WEST', 'EAST', центр 'CENTRAL' / Кастоные координаты: 'CUSTOM'
PLUME_CUSTOM_COORDS: tuple[int, int] = (10, 10)  # Кортеж с координатами (x, y)
