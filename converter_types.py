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
    pos: PosType
    color: ColorType

    def squared_distance(self, other: "FormPosColor") -> int:
        return sum((i - j)**2 for i, j in zip(self.pos, other.pos))

    def check_diff(self, other: "FormPosColor"):
        dist = self.squared_distance(other)

        return (
            dist > 0,  # if positions are equal, difference is less
            dist if self.color == other.color else float("inf"),
            dist,
        )


FrameShapesType = defaultdict[ShapeType, set[FormPosColor]]
FramesType = list[set[FormPosColor]]
AnimationShapesType = dict[ShapeType, FramesType]
ChainFramesType = list[Optional[FormPosColor]]