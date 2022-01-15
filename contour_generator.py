from collections import defaultdict
from enum import Enum
import numpy as np

PosType = tuple[int, int]
ShapeType = frozenset[PosType]

DEFAULT_PRIORITY_ROTATION_DIR = "right"


class Direction(Enum):
    UP = (-1, 0)
    RT = (0, 1)
    DN = (1, 0)
    LT = (0, -1)

    def __radd__(self, other: PosType) -> PosType:
        x, y = self.value
        return (other[0] + x, other[1] + y)

    def turn_right(self):
        return {
            self.UP: self.RT,
            self.RT: self.DN,
            self.DN: self.LT,
            self.LT: self.UP,
        }[self]

    def turn_left(self):
        return {
            self.UP: self.LT,
            self.RT: self.UP,
            self.DN: self.RT,
            self.LT: self.DN,
        }[self]

    def get_next_left(self, dirs: set["Direction"]):
        bdir = self.turn_left()
        while bdir not in dirs:
            bdir = bdir.turn_right()
        return bdir

    def get_next_right(self, dirs: set["Direction"]):
        bdir = self.turn_right()
        while bdir not in dirs:
            bdir = bdir.turn_left()
        return bdir

    def get_closest_dir(self, dirs: set["Direction"], priority: str):
        if not dirs:
            raise ValueError("Something went terribly wrong in borders generation")
        if priority == "left":
            bdir = self.get_next_left(dirs)
        else:
            bdir = self.get_next_right(dirs)
        dirs.remove(bdir)
        return bdir

    def get_next_dir(self, borders, point, priority: str = DEFAULT_PRIORITY_ROTATION_DIR):
        dirs = borders[point]
        dir_now = self.get_closest_dir(dirs, priority)
        if not dirs:
            del borders[point]
        return dir_now


def generate_borders(shape: ShapeType):
    shift = (0.5, 0.5)
    borders: dict[PosType, set[Direction]] = defaultdict(set)

    for pixel in shape:
        for idir in Direction:
            ax, ay = adjacent = pixel + idir
            if (ax, ay) in shape:
                continue
            bdir = idir.turn_right()
            corner = (np.array(pixel) + adjacent - bdir.value) / 2
            start = tuple(map(int, corner + shift))
            borders[start].add(bdir)  #type: ignore

    return borders


def generate_cycle(borders: dict[PosType, set[Direction]]):
    try:
        start = point_now = next(iter(borders))
    except StopIteration:
        return None

    dir_now = last_dir = Direction.RT.get_next_dir(borders, start)
    point_now += dir_now
    cycle = [point_now]  # without start point because it will be last element of the cycle

    while start != point_now:
        dir_now = dir_now.get_next_dir(borders, point_now)
        point_now += dir_now

        if last_dir == dir_now:
            cycle[-1] = point_now
        else:
            cycle.append(point_now)

        last_dir = dir_now

    return cycle


def generate_contours(shape: ShapeType):
    borders = generate_borders(shape)
    cycles: list[list[PosType]] = []

    while cycle := generate_cycle(borders):
        cycles.append(cycle)

    return cycles