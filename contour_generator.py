from collections import defaultdict
from enum import Enum

import numpy as np

from converter_types import *

BordersType = dict[PosType, set["Direction"]]


class Direction(Enum):
    """
    Enumeration of all 4 possible directions.
    """
    UP = (-1, 0)
    RT = (0, 1)  # RighT
    DN = (1, 0)  # DowN
    LT = (0, -1)  # LefT

    def __radd__(self, other: PosType) -> PosType:
        """
        Moves position on 1 pixel in direction.
        """
        x, y = self.value
        return (other[0] + x, other[1] + y)

    def turn_right(self) -> "Direction":
        return {
            self.UP: self.RT,
            self.RT: self.DN,
            self.DN: self.LT,
            self.LT: self.UP,
        }[self]

    def turn_left(self) -> "Direction":
        return {
            self.UP: self.LT,
            self.RT: self.UP,
            self.DN: self.RT,
            self.LT: self.DN,
        }[self]

    def get_next_right(self, dirs: set["Direction"]) -> "Direction":
        """
        Get the rightmost direction from set.
        """
        bdir = self.turn_right()  # starts from trying to rotate right
        while bdir not in dirs:  # while direction is not present
            bdir = bdir.turn_left()  # tries to take less right directions
        return bdir

    def take_closest(self, dirs: set["Direction"]) -> "Direction":
        """
        Takes (gets and removes) optimal direction from set.
        """
        next_dir = self.get_next_right(dirs)
        dirs.remove(next_dir)
        return next_dir

    def get_next(self, borders: BordersType, point: PosType):
        """
        Selects a new direction of movement along the borders
        and shifts the point in it.
        """
        dirs = borders[point]
        dir_now = self.take_closest(dirs)
        if not dirs:
            del borders[point]
        return point + dir_now, dir_now


def generate_borders(shape: ShapeType) -> BordersType:
    """
    Collects sets of shape arrow borders.
    ``` plain
                                    0    1    2       {
    {                             +-------------        (0, 1): {>, },
      (0, 1),      [_ # _]      0 |      + -> +         (0, 2): {v, },
      (1, 0),  ->  [# # _]  ->    |      ^    v   ->    (1, 2): {v, },
      (1, 1),      [_ _ _]      1 | + -> +    +         (2, 2): {<, },
    }                             | ^         v         ...
                                2 | + <- + <- +       } 
    ```
    Second and third steps are drawn for clarity, function converts
    positions set directly to a dict with keys - positions
    and values - sets of `Direction`s of arrow borders from that positions.

    """
    shift = (0.5, 0.5)
    borders: BordersType = defaultdict(set)

    # iterates over all shape pixels
    for pixel in shape:
        # iterates over all neighbour pixels
        # by iterating over all directions and adding them to the pixel
        for adj_dir in Direction:
            adjacent = pixel + adj_dir
            if adjacent in shape: # if neighbour is present
                continue # skip drawing border beetween them

            # direction of border arrow beetween current pixel
            # and empty neighbour pixel
            border_dir = adj_dir.turn_right()

            # calculates start point of arrow 
            start = (np.array(pixel) + adjacent - border_dir.value) / 2 + shift

            start: PosType = tuple(map(int, start))
            borders[start].add(border_dir)

    return borders


def generate_cycle(borders: BordersType) -> ContourType:
    """
    Assembles the cycle by going through the arrow borders.
    """
    # gets any start position
    start = point_now = next(iter(borders))

    # moves one step on border to get first direction
    point_now, dir_now = last_dir = Direction.RT.get_next(borders, start)

    # creates cycle without start point
    # because it will be last element of the cycle
    cycle = [point_now]

    while start != point_now:
        point_now, dir_now = dir_now.get_next(borders, point_now)

        # if direction didn't change
        if last_dir == dir_now:
            # replaces last point in cycle
            # to delete useless point on straight line
            cycle[-1] = point_now
        else:
            cycle.append(point_now)

        last_dir = dir_now

    return cycle


def generate_contours(shape: ShapeType) -> list[ContourType]:
    """
    Generates all shape contours.
    """
    borders = generate_borders(shape)
    cycles: list[ContourType] = []

    while borders:
        cycles.append(generate_cycle(borders))
        
    return cycles
