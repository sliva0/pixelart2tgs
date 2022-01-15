from dataclasses import dataclass
from collections import defaultdict
from typing import Optional

import numpy as np
from scipy import ndimage

from contour_generator import generate_contours

SourceAnimationType = list[tuple[float, np.ndarray]]
PosType = tuple[int, int]
ColorType = tuple[int, int, int, int]
ShapeType = frozenset[PosType]


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


def lottify_value(value_frames: list, time_shift: float, durations: list[float]):
    last_value = None
    keyframes = []
    current_time = time_shift

    for (current_value, frame_duration) in zip(value_frames, durations):
        if current_value is not None and current_value != last_value:
            keyframes.append((current_time, current_value))
        
        current_time += frame_duration
    
    if len(keyframes) == 1:
        return 


@dataclass(eq=True, frozen=True)
class FormPosColor:
    position: PosType
    color: ColorType

    def check_diff(self, other: "FormPosColor"):
        dist = point_square_dist(self.position, other.position)

        return (
            dist != 0,  # if positions are equal, difference is less
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
        position_frames = count_changes(i.position for i in frames)
        color_frames = count_changes(i.color for i in frames)

        return opacity_frames * 2 + position_frames * 3 + color_frames * 4

    def clean_variants(self, frames: FramesType):
        for element, frame in zip(self.frames, frames):
            if element:
                frame.remove(element)

    def generate_lottie_group(self, shape: ShapeType, durations: list[float]):
        ...


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


def extract_form_list(source_animation: SourceAnimationType):
    durations, shape_dict = extract_animation_shapes(source_animation)
    for shape, frames in shape_dict.items():
        chains = make_frame_chains(frames)
        generate_contours(shape)
        yield chains, shape, durations


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


from PIL import Image

source = open_gif_file("./Deltarune/Other/spamton_fortnite_cutted.gif")

import matplotlib.pyplot as plt

axes = plt.gca()

for chains, shape, durations in extract_form_list(source):
    print("shape processed")
    for chain in chains:
        s = chain.frames[1]
        if not s:
            continue
        for point in np.array(tuple(shape)) + s.position + 0.2:
            rectangle = plt.Rectangle(point[::-1], 0.6, 0.6, fc=np.array(s.color) / 255)
            axes.add_patch(rectangle)

axes.invert_yaxis()
plt.axis("equal")
plt.grid()
plt.show()