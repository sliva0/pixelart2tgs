from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

import numpy as np

PosType = tuple[int, int]
ColorType = tuple[int, int, int, int]

LottiePosType = tuple[int, int]
LottieColorType = tuple[float, float, float]

ShapeType = frozenset[PosType]
ContourType = list[PosType]
DurationsType = list[float]

SourceAnimationType = tuple[DurationsType, list[np.ndarray]]


@dataclass(eq=True, frozen=True)
class FormPosColor:
    """
    Dataclass with information about the position and color
    of a specific shape in a specific frame.
    """
    pos: PosType
    color: ColorType

    def squared_distance(self, other: "FormPosColor") -> int:
        """
        Pythagorean distance between points without calculating the square
        root, since results are only needed to compare with each other
        """
        return sum((i - j)**2 for i, j in zip(self.pos, other.pos))

    def check_diff(self, other: "FormPosColor"):
        """
        Calculates the tuple needed to compare the "closest" element of
        the same class from the next frame to implement the greedy algorithm.
        
        The smaller the value returned by this function, the less
        information about the transition will need to be written to
        the final file, thereby optimizing its size.
        """
        dist = self.squared_distance(other)

        return (
            # elements with same position are closest
            dist > 0,  # if positions are same, diff is False (< True)

            # elements with the same color are closer
            # than those with different colors
            dist if self.color == other.color else float("inf"),

            # all other elements are compared by distance beetween them
            dist,
        )

    def take_closest(self, next_frame: set["FormPosColor"]):
        """
        Takes (gets and removes) closest `FormPosColor`from set of next frame.
        """
        closest = min(next_frame, key=self.check_diff)
        next_frame.remove(closest)
        return closest


FrameShapesType = defaultdict[ShapeType, set[FormPosColor]]
FramesType = list[set[FormPosColor]]
AnimationShapesType = dict[ShapeType, FramesType]
ChainFramesType = list[Optional[FormPosColor]]