from scipy import ndimage

from converter_types import *


def get_frame_colors(frame: np.ndarray) -> np.ndarray:
    """
    Gets list of all unique colors from one frame.
    """
    x, y, z = frame.shape
    pixels = frame.reshape(x * y, z)  # pixel color list
    colors = np.unique(pixels, axis=0)  # get all unique colors

    # returns only those colors where the last value is non-zero,
    # which means they aren't completely transparent
    return colors[colors[:, -1] != 0]


def add_zeros_frame(image: np.ndarray) -> np.ndarray:
    """
    Increases the frame size on both axes by 1 by adding zeros.
    ``` plain
    [_ _]  ->  [_ _ 0]
    [_ _]      [_ _ 0]
               [0 0 0]
    ```
    """
    xi, yi = image.shape
    image = np.concatenate([image, np.zeros([xi, 1])], axis=1)
    return np.concatenate([image, np.zeros([1, yi + 1])])


def normalize_shape(shape: np.ndarray) -> tuple[ShapeType, PosType]:
    """
    Converts shape format.
    Returns converted shape and its position.

    1) Normalizes shape by shifting to the upper left corner:
    ``` plain
    [_ _ _ _]      [_ 1 _ _]
    [_ _ _ _]  ->  [1 1 1 _]    shift = (2, 1)
    [_ _ 1 _]      [_ _ _ _]
    [_ 1 1 1]      [_ _ _ _]    0 replaced by _ for ease of reading
    ```

    2) Converts a matrix of 0 and 1 into a set of coordinates for hashability:
    ``` plain
    [_ 1 _ _]
    [1 1 1 _]  ->  {(0, 1), (1, 0), (1, 1), (1, 2)}
    [_ _ _ _]
    [_ _ _ _]
    ```
    """
    coords = shape.nonzero()  # get transposed coords of ones in shape
    upper_left_corner = np.min(coords, axis=1)  # calculate min of every coord
    pixels = np.transpose(coords) - upper_left_corner  # shift by it
    return frozenset(map(tuple, pixels)), tuple(upper_left_corner)


def extract_frame_shapes(frame: np.ndarray) -> FrameShapesType:
    """
    Creates dict with keys - shapes and values - sets of `FormPosColor`
    for a specific shape in the frame.
    """
    colors = get_frame_colors(frame)

    shapes: FrameShapesType = defaultdict(set)

    for color in colors:
        # creates matrix with ones in place of pixels of current color
        color_mask = add_zeros_frame(~np.any(frame - color, axis=2))

        # selects individual shapes among all pixels
        labels, amount = ndimage.label(color_mask)

        for label_number in range(1, amount + 1):
            shape, shape_shift = normalize_shape(labels == label_number)
            # adds every mormalized shape's color and pos pair into final dict
            shapes[shape].add(FormPosColor(shape_shift, tuple(color)))

    return shapes


def generate_shapes(
        source: SourceAnimationType
) -> tuple[DurationsType, AnimationShapesType]:
    """
    Passes durations of frames and creates dict with keys - shapes
    and values - lists of sets of `FormPosColor` for every frame.
    """

    durations, frames = source

    shape_dict: AnimationShapesType = defaultdict(list)
    frames_shapes = list(map(extract_frame_shapes, frames))

    # iterates over every unique shape in animation
    for shape in set().union(*frames_shapes):
        # caches new list of every frame shapes into a variable
        shape_frames = shape_dict[shape]
        for frame_shapes in frames_shapes:
            shape_frames.append(frame_shapes[shape])

    return durations, shape_dict
