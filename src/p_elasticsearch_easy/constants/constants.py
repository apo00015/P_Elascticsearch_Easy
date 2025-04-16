from enum import Enum

MAX_SIZE: int = 10000


class TIMEOUT(int, Enum):
    ELASTIC = 300
