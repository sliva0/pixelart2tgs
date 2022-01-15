from dataclasses import dataclass
from collections import defaultdict
import gzip
import json
from typing import Optional

import numpy as np
from scipy import ndimage

from contour_generator import generate_contours
import templates

SourceAnimationType = list[tuple[float, np.ndarray]]
PosType = tuple[int, int]
ColorType = tuple[int, int, int, int]
ShapeType = frozenset[PosType]


def get_image_sizes(source: SourceAnimationType) -> tuple[int, int]:
    return source[0][1].shape[:2]


def point_square_dist(a: PosType, b: PosType):
    return sum((i - j)**2 for i, j in zip(a, b))


def count_changes(elements: list) -> int:
    counter = 0
    prev, *elements = elements

    for element in elements:
        if prev != element:
            counter += 1
        prev = element
    return counter


def lottify_color(color: ColorType) -> tuple[float, float, float]:
    return tuple(round(int(i) / 255, 3) for i in color[:3])


def lottify_pos(position: PosType) -> tuple[int, int]:
    return tuple(int(i) for i in position)[::-1]


def lottify_value(value_frames: list, time_shift: float, durations: list[float]):
    last_value = None
    keyframes = []
    current_time = time_shift

    for (current_value, frame_duration) in zip(value_frames, durations):
        if current_value is not None and current_value != last_value:
            keyframes.append((current_time, current_value))
            last_value = current_value

        current_time += frame_duration

    if len(keyframes) == 1:
        return templates.static_value(keyframes[0][1])
    else:
        return templates.animated_value([templates.keyframe(*data) for data in keyframes])


@dataclass(eq=True, frozen=True)
class FormPosColor:
    pos: PosType
    color: ColorType

    def check_diff(self, other: "FormPosColor"):
        dist = point_square_dist(self.pos, other.pos)

        return (
            dist > 0,  # if positions are equal, difference is less
            dist if self.color == other.color else float("inf"),
            dist,
        )


FrameShapesType = defaultdict[ShapeType, set[FormPosColor]]
FramesType = list[set[FormPosColor]]
AnimationShapesType = dict[ShapeType, FramesType]
ChainFramesType = list[Optional[FormPosColor]]


class Chain:
    def __init__(self, keyframe_shift: int, first_visible_frame: FormPosColor):
        self.keyframe_shift = keyframe_shift
        self.frames: ChainFramesType = [first_visible_frame]
        self.last_visible_frame = first_visible_frame

    def add_closest_element(self, elements: list[FormPosColor]) -> Optional[FormPosColor]:
        if elements:
            new_element = min(elements, key=self.last_visible_frame.check_diff)
            self.last_visible_frame = new_element
        else:
            new_element = None

        self.frames.append(new_element)

    def count_frames(self):
        frames: list[FormPosColor] = list(filter(bool, self.frames))

        opacity_frames = count_changes(map(bool, self.frames))
        position_frames = count_changes(i.pos for i in frames)
        color_frames = count_changes(i.color for i in frames)

        return opacity_frames * 2 + position_frames * 3 + color_frames * 4

    def clean_variants(self, frames: FramesType):
        for element, frame in zip(self.frames, frames[self.keyframe_shift:]):
            if element:
                frame.remove(element)

    def generate_group(self, contours: list[list[PosType]], durations: list[float], scale: float):
        time_shift = sum(durations[:self.keyframe_shift])
        shifted_durations = durations[self.keyframe_shift:]

        opacity_values = [0] * self.keyframe_shift + [bool(frame) * 100 for frame in self.frames]
        pos_values = [frame and lottify_pos(frame.pos) for frame in self.frames]
        color_values = [frame and lottify_color(frame.color) for frame in self.frames]

        opacity = lottify_value(opacity_values, 0, durations)
        position = lottify_value(pos_values, time_shift, shifted_durations)
        color = lottify_value(color_values, time_shift, shifted_durations)

        contours = [templates.contour([lottify_pos(i) for i in points]) for points in contours]

        return templates.group(contours, scale, color, opacity, position)


def add_zeros_frame(image: np.ndarray) -> np.ndarray:
    xi, yi = image.shape
    image = np.concatenate([image, np.zeros([xi, 1])], axis=1)
    return np.concatenate([image, np.zeros([1, yi + 1])])


def get_frame_colors(pixels: np.ndarray):
    colors = np.unique(pixels, axis=0)
    return colors[colors[:, -1] != 0]


def normalize_shape(shape: np.ndarray) -> tuple[frozenset[PosType], PosType]:
    coords = shape.nonzero()
    upper_left_corner = tuple(np.min(coords, axis=1))
    pixels = np.transpose(coords) - upper_left_corner
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


def extract_animation_shapes(source: SourceAnimationType):
    durations: tuple[float]
    shape_dict: AnimationShapesType = defaultdict(list)

    durations, frames = zip(*source)
    frames_shapes = list(map(extract_frame_shapes, frames))

    for shape in set().union(*frames_shapes):
        shape_frames = shape_dict[shape]
        for frame_shapes in frames_shapes:
            shape_frames.append(frame_shapes[shape])

    return durations, shape_dict


def make_frame_chains(frames: FramesType) -> list[Chain]:
    final_chains: list[Chain] = []

    for start_i, start_frames in enumerate(frames):
        while start_frames:
            chain_variants = [Chain(start_i, start_frame) for start_frame in start_frames]

            for current_frames in frames[start_i + 1:]:
                for chain in chain_variants:
                    chain.add_closest_element(current_frames)

            optimal_chain = min(chain_variants, key=lambda i: i.count_frames())
            final_chains.append(optimal_chain)
            optimal_chain.clean_variants(frames)

    return final_chains


def generate_shift_scale(x: int, y: int):
    scale = 512 / max(x, y)
    if x > y:
        shift = [(1 - y / x) * 256, 0.0]
    else:
        shift = [0.0, (1 - x / y) * 256]
    return shift, scale


def generate_lottie(source: SourceAnimationType):
    durations, shape_dict = extract_animation_shapes(source)

    x, y = get_image_sizes(source)
    shift, scale = generate_shift_scale(x, y)
    length = round(sum(durations), 1)

    groups = []

    for shape, frames in shape_dict.items():
        chains = make_frame_chains(frames)

        contours = generate_contours(shape)

        groups += [chain.generate_group(contours, durations, scale) for chain in chains]

    return templates.lottie(length, LABEL, shift, scale, groups)


from PIL import Image


def open_gif_file(path: str) -> SourceAnimationType:
    image = Image.open(path)
    source_animation = []

    for i in range(image.n_frames):  #type: ignore
        image.seek(i)
        duration = image.info["duration"] * 60 / 1000
        frame = image.convert("RGBA")
        #x, y = frame.size  #.resize((x // 2, y // 2), Image.NEAREST))
        source_animation.append((duration, np.array(frame)))

    return source_animation


def save_tgs(lottie, filepath):
    with gzip.open(filepath, 'wb', compresslevel=9) as out:
        out.write(json.dumps(lottie, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))

LABEL = "Made by t.me/sliva0 script"

source = open_gif_file("./Deltarune/Other/spamton_fortnite_cutted.gif")
lottie = generate_lottie(source)

#with open("test.json", "w") as f: f.write(repr(lottie))

save_tgs(lottie, "./spamton_fortnite_cutted.tgs")