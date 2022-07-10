from collections import defaultdict
import gzip
import json

import numpy as np
from scipy import ndimage

from contour_generator import generate_contours
from chain_generator import generate_chains
from lottie_types import *
import templates


def get_image_sizes(source: SourceAnimationType) -> tuple[int, int]:
    return source[0][1].shape[:2]


def add_zeros_frame(image: np.ndarray) -> np.ndarray:
    xi, yi = image.shape
    image = np.concatenate([image, np.zeros([xi, 1])], axis=1)
    return np.concatenate([image, np.zeros([1, yi + 1])])


def get_frame_colors(pixels: np.ndarray):
    colors = np.unique(pixels, axis=0)
    return colors[colors[:, -1] != 0]


def normalize_shape(shape: np.ndarray) -> tuple[ShapeType, PosType]:
    coords = shape.nonzero()
    upper_left_corner = tuple(np.min(coords, axis=1))
    pixels = np.transpose(coords) - upper_left_corner  # type: ignore
    return frozenset(map(tuple, pixels)), upper_left_corner


def extract_frame_shapes(frame: np.ndarray) -> FrameShapesType:
    x, y, z = frame.shape
    colors = get_frame_colors(frame.reshape(x * y, z))

    shapes: FrameShapesType = defaultdict(set)

    for color in colors:
        color_mask = add_zeros_frame(~np.any(frame - color, axis=2))
        labels, amount = ndimage.label(color_mask)  #type: ignore
        color = tuple(color)
        for label_number in range(1, amount + 1):
            shape, shape_shift = normalize_shape(labels == label_number)
            shapes[shape].add(FormPosColor(shape_shift, color))

    return shapes


def extract_animation_shapes(
        source: SourceAnimationType) -> tuple[tuple[float], AnimationShapesType]:
    durations: tuple[float]
    frames: tuple[np.ndarray]
    durations, frames = zip(*source)  # type: ignore

    shape_dict: AnimationShapesType = defaultdict(list)
    frames_shapes = list(map(extract_frame_shapes, frames))

    for shape in set().union(*frames_shapes):
        shape_frames = shape_dict[shape]
        for frame_shapes in frames_shapes:
            shape_frames.append(frame_shapes[shape])

    return durations, shape_dict


def generate_shift_scale(x: int, y: int) -> tuple[list[float], float]:
    scale = 512 / max(x, y)
    if x > y:
        shift = [(1 - y / x) * 256, 0.0]
    else:
        shift = [0.0, (1 - x / y) * 256]
    return shift, scale


def generate_lottie(source: SourceAnimationType):
    durations, shape_dict = extract_animation_shapes(source)

    shift, scale = generate_shift_scale(*get_image_sizes(source))
    length = round(sum(durations), 1)

    groups = []

    for shape, frames in shape_dict.items():
        contours = generate_contours(shape)
        chains = generate_chains(frames)

        groups += [chain.generate_group(contours, durations, scale) for chain in chains]

    return templates.lottie(length, LABEL, shift, scale, groups)


from PIL import Image


def open_gif_file(str) -> SourceAnimationType:
    image = Image.open(path)
    source_animation = []

    for frame_index in range(image.n_frames):  #type: ignore
        image.seek(frame_index)
        duration = image.info["duration"] * 60 / 1000
        frame = image.convert("RGBA")
        #x, y = frame.size  #.resize((x // 2, y // 2), Image.NEAREST))
        source_animation.append((duration, np.array(frame)))

    return source_animation


def save_tgs(lottie, filepath):
    with gzip.open(filepath, 'wb', compresslevel=9) as out:
        out.write(json.dumps(lottie, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))


from pathlib import Path

LABEL = "Made by t.me/sliva0 script"

paths = [r"Deltarune\durgbow.gif"]

for path in map(Path, paths):
    out_path = path.parent.parent / path.with_suffix(".tgs")
    source = open_gif_file(path)

    print(f"generating {path.name}")
    lottie = generate_lottie(source)

    #with open("test.json", "w") as f: f.write(repr(lottie))
    print(f"saving {path.name}")
    save_tgs(lottie, out_path)
