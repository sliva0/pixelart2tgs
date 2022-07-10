import templates
from lottie_types import *


def lottify_color(color: ColorType) -> LottieColorType:
    return tuple(round(int(i) / 255, 3) for i in color[:3])


def lottify_pos(position: PosType) -> LottiePosType:
    return tuple(map(int, position))[::-1]


def lottify_value(value_frames: list, time_shift: float, durations: tuple[float]):
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


class Chain:

    def __init__(self, keyframe_shift: int, start_frame: FormPosColor):
        self.keyframe_shift = keyframe_shift
        self.frames: ChainFramesType = [start_frame]
        self.last_visible_frame = start_frame

    def take_closest_element(self, elements: set[FormPosColor]):
        if elements:
            closest_element = min(elements, key=self.last_visible_frame.check_diff)
            elements.remove(closest_element)
            self.last_visible_frame = closest_element
        else:
            closest_element = None

        self.frames.append(closest_element)

    def generate_group(self, contours: list[ContourType], durations: tuple[float], scale: float):
        time_shift = sum(durations[:self.keyframe_shift])
        shifted_durations = durations[self.keyframe_shift:]

        opacity_values = [0] * self.keyframe_shift + [bool(frame) * 100 for frame in self.frames]
        pos_values = [frame and lottify_pos(frame.pos) for frame in self.frames]
        color_values = [frame and lottify_color(frame.color) for frame in self.frames]

        opacity = lottify_value(opacity_values, 0, durations)
        position = lottify_value(pos_values, time_shift, shifted_durations)
        color = lottify_value(color_values, time_shift, shifted_durations)

        lottie_contours = [
            templates.contour(list(map(lottify_pos, contour))) for contour in contours
        ]

        return templates.group(lottie_contours, scale, color, opacity, position)


def generate_chains(frames: FramesType) -> list[Chain]:
    chains: list[Chain] = []

    for start_frame_index, start_frames in enumerate(frames):
        for start_frame in start_frames:
            chain = Chain(start_frame_index, start_frame)

            for current_frames in frames[start_frame_index + 1:]:
                chain.take_closest_element(current_frames)

            chains.append(chain)

    return chains