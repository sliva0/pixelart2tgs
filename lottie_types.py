from collections import defaultdict
from dataclasses import dataclass
from typing import Optional
import numpy as np

SourceAnimationType = list[tuple[float, np.ndarray]]

PosType = tuple[int, int]
ColorType = tuple[int, int, int, int]

LottiePosType = tuple[int, int]
LottieColorType = tuple[float, float, float]

ShapeType = frozenset[PosType]


def squared_point_distance(a: PosType, b: PosType) -> int:
    return sum((i - j)**2 for i, j in zip(a, b))


@dataclass(eq=True, frozen=True)
class FormPosColor:
    pos: PosType
    color: ColorType

    def check_diff(self, other: "FormPosColor"):
        dist = squared_point_distance(self.pos, other.pos)

        return (
            dist > 0,  # if positions are equal, difference is less
            dist if self.color == other.color else float("inf"),
            dist,
        )


FrameShapesType = defaultdict[ShapeType, set[FormPosColor]]
FramesType = list[set[FormPosColor]]
AnimationShapesType = dict[ShapeType, FramesType]
ChainFramesType = list[Optional[FormPosColor]]