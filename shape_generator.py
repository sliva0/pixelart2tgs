from scipy import ndimage

from converter_types import *


def get_frame_colors(pixels: np.ndarray):
    colors = np.unique(pixels, axis=0)
    return colors[colors[:, -1] != 0]


def add_zeros_frame(image: np.ndarray) -> np.ndarray:
    xi, yi = image.shape
    image = np.concatenate([image, np.zeros([xi, 1])], axis=1)
    return np.concatenate([image, np.zeros([1, yi + 1])])


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
        labels, amount = ndimage.label(color_mask)
        color = tuple(color)
        for label_number in range(1, amount + 1):
            shape, shape_shift = normalize_shape(labels == label_number)
            shapes[shape].add(FormPosColor(shape_shift, color))

    return shapes


def generate_shapes(source: SourceAnimationType) -> tuple[DurationsType, AnimationShapesType]:
    durations, frames = source

    shape_dict: AnimationShapesType = defaultdict(list)
    frames_shapes = list(map(extract_frame_shapes, frames))

    for shape in set().union(*frames_shapes):
        shape_frames = shape_dict[shape]
        for frame_shapes in frames_shapes:
            shape_frames.append(frame_shapes[shape])

    return durations, shape_dict
