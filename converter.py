DEBUG = False

from enum import Enum
from collections import defaultdict

import numpy as np

if DEBUG:
    import matplotlib.pyplot as plt  #used for contour debug

import templates


class Direction(Enum):
    UP = (-1, 0)
    RT = (0, 1)
    DN = (1, 0)
    LT = (0, -1)

    def __radd__(self, other: tuple[int, int]) -> tuple[int, int]:
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

    def get_next_left(self, dirs: set):
        bdir = self.turn_left()
        while bdir not in dirs:
            bdir = bdir.turn_right()
        return bdir

    def get_next_right(self, dirs: set):
        bdir = self.turn_right()
        while bdir not in dirs:
            bdir = bdir.turn_left()
        return bdir

    def get_closest_dir(self, dirs: set, priority: str = "left"):
        if not dirs:
            raise ValueError("Something went terribly wrong in borders generation")
        if priority == "left":
            bdir = self.get_next_left(dirs)
        else:
            bdir = self.get_next_right(dirs)
        dirs.remove(bdir)
        return bdir
    
    def get_next_dir(self, borders, point, priority: str = "left"):
        dirs = borders[point]
        dir_now = self.get_closest_dir(dirs, priority)
        if not dirs:
            del borders[point]
        return dir_now


def add_zeros_frame(claster: np.ndarray) -> np.ndarray:
    xi, yi = claster.shape
    claster = np.concatenate([claster, np.zeros([xi, 1])], axis=1)
    return np.concatenate([claster, np.zeros([1, yi + 1])])


def draw_debug_borders(borders: dict[tuple[int, int], set[Direction]]):
    for i, j in borders.items():
        for d in j:
            plt.arrow(*i[::-1], *np.array(d.value[::-1]) * 0.5, width=0.05)
    plt.gca().invert_yaxis()
    plt.axis('equal')
    plt.grid()


def generate_borders(claster: np.ndarray):
    shift = (0.5, 0.5)
    borders: dict[tuple[int, int], set[Direction]] = defaultdict(set)
    pixels = np.transpose(claster.nonzero())

    for pixel in pixels:
        for idir in Direction:
            ax, ay = adjacent = pixel + idir.value
            if claster[ax, ay]:
                continue
            bdir = idir.turn_right()
            corner = ((pixel + adjacent) - np.array(bdir.value)) / 2
            start = tuple(map(int, corner + shift))
            borders[start].add(bdir)  #type: ignore

    if DEBUG:
        draw_debug_borders(borders)
    return borders


def generate_cycle(borders: dict[tuple[int, int], set[Direction]]):
    try:
        start = point_now = next(iter(borders))
    except StopIteration:
        return None

    dir_now = last_dir = Direction.RT.get_next_dir(borders, start)
    point_now += dir_now
    cycle = [start, point_now]

    while start != point_now:
        dir_now = dir_now.get_next_dir(borders, point_now)
        point_now += dir_now

        if last_dir == dir_now:
            cycle[-1] = point_now
        else:
            cycle.append(point_now)

        last_dir = dir_now

    return cycle


def generate_contours(claster: np.ndarray):
    borders = generate_borders(claster)
    cycles: list[list[tuple[int, int]]] = []

    while True:
        cycle = generate_cycle(borders)
        if not cycle:
            break
        if DEBUG:
            plt.plot(*tuple(zip(*cycle))[::-1], marker="o")
        cycles.append(cycle)

    if DEBUG:
        plt.show()

    return cycles


def get_colors(pixels: np.ndarray):
    colors = np.unique(pixels, axis=0)
    return colors[colors[:, -1] != 0]


def generate_shift_scale(x: int, y: int):
    scale = 512 / max(x, y)
    if x > y:
        shift = [(1 - y / x) * 256, 0.0]
    else:
        shift = [0.0, (1 - x / y) * 256]
    return shift, scale


def convert_color_format(color: np.ndarray):
    return (color[:3] / 255).tolist()


def get_opacity(color: np.ndarray):
    return color[-1] / 255


def generate_layer(img, time_i: float, time_o: float):
    x, y, z = img.shape
    colors = get_colors(img.reshape(x * y, z))

    shift, scale = generate_shift_scale(x, y)
    shapes = []

    for color in colors:
        color_mask = add_zeros_frame((img - color).sum(axis=2) == 0)
        cycles = generate_contours(color_mask)

        contours = []
        for cycle in cycles:
            contour = templates.contour(np.array(cycle, dtype=np.int64)[:, ::-1].tolist())
            contours.append(contour)

        lottie_color = convert_color_format(color)
        opacity = get_opacity(color)

        group = templates.group(contours, lottie_color, scale, opacity)
        shapes.append(group)

    return templates.layer(time_i, time_o, shapes, shift, scale)


def generate_lottie(frames: list, frames_duration: list[float]):
    layers = []
    time_offset = 0
    for frame, duration in zip(frames, frames_duration):
        img = np.array(frame)

        layer = generate_layer(img, time_offset, time_offset + duration)
        layers.append(layer)
        time_offset += duration

    return templates.lottie(time_offset, layers)