import templates
from converter_types import *


def lottify_pos(position: PosType) -> LottiePosType:
    """
    Converts position from converter format to lottie format.
    """
    return tuple(map(int, position))[::-1]


def lottify_color(color: ColorType) -> LottieColorType:
    """
    Converts color from converter format to lottie format.
    """
    return tuple(round(int(i) / 255, 3) for i in color[:3])


def lottify_value(value_frames: list, time_shift: float,
                  durations: DurationsType):
    """
    Converts animated value (color, position, opacity) to lottie format.
    """

    last_value = None
    keyframes = []
    current_time = time_shift

    # iterates over all frames
    for current_value, frame_duration in zip(value_frames, durations):

        # adds new keyframe only if value present and changed
        if current_value is not None and current_value != last_value:
            keyframes.append((current_time, current_value))
            last_value = current_value

        current_time += frame_duration

    # use basic static value template, if value didn't change
    if len(keyframes) == 1:
        return templates.static_value(last_value)
    else:
        kfs = [templates.keyframe(*data) for data in keyframes]
        return templates.animated_value(kfs)


class Chain:
    """
    Class that stores the positions and colors
    of a particular shape in a sequence of frames.

    In the final animation, each chain is assembled into a group,
    which allows not to duplicate information about the contours
    of the shape for each frame, but only to change its position
    and color using keyframes.
    """

    def __init__(self, keyframe_shift: int, start_frame: FormPosColor):
        self.keyframe_shift = keyframe_shift
        self.frames: ChainFramesType = [start_frame]
        self.last_visible_frame = start_frame

    def take_closest_element(self, next_frame: set[FormPosColor]):
        """
        Greedily selects a specific position and color
        of the same shape from the next frame.
        """

        if next_frame:
            closest = self.last_visible_frame.take_closest(next_frame)
            self.last_visible_frame = closest
        else:
            # if there is no same shape in the next frame,
            # None is written to the list and last_visible_frame is not updated
            closest = None

        self.frames.append(closest)

    def generate_group(self, contours: list[ContourType],
                       durations: DurationsType, scale: float):
        """
        Generates lottie group from chain.
        """
        time_shift = sum(durations[:self.keyframe_shift])
        shifted_durations = durations[self.keyframe_shift:]

        opacity_values = [(100 if frame else 0) for frame in self.frames]
        opacity_values = [0] * self.keyframe_shift + opacity_values

        pos_values = [
            frame and lottify_pos(frame.pos) for frame in self.frames
        ]
        color_values = [
            frame and lottify_color(frame.color) for frame in self.frames
        ]

        opacity = lottify_value(opacity_values, 0, durations)
        position = lottify_value(pos_values, time_shift, shifted_durations)
        color = lottify_value(color_values, time_shift, shifted_durations)

        lottie_contours = [
            templates.contour(list(map(lottify_pos, contour)))
            for contour in contours
        ]

        return templates.group(
            lottie_contours,
            scale,
            color,
            opacity,
            position,
        )


def generate_chains(frames: FramesType) -> list[Chain]:
    """
    Creates chains from all `FormPosColor` in every frame of one shape.
    """
    chains: list[Chain] = []

    # iterate through start frames
    for start_frame_index, start_frame in enumerate(frames):
        # for every start position (+color) in start frame
        for start_pos in start_frame:
            # creates new chain
            chain = Chain(start_frame_index, start_pos)

            # fill up chain with FormPosColor from next frames
            for current_frames in frames[start_frame_index + 1:]:
                # closest element taken from the sets is removed
                # so as not to go in several chains
                chain.take_closest_element(current_frames)

            chains.append(chain)

    return chains