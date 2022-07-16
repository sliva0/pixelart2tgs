import argparse
from contextlib import contextmanager
import gzip
import json
from pathlib import Path
import traceback

import numpy as np
from PIL import Image

from .converter_types import *
from .lottie_generator import generate_lottie

SIZE_64KB = 1 << 16
SIZE_1MB = 1 << 20

FPS = 60
MS_PER_S = 1000

MAX_S = 3
MAX_FRAMES = FPS * MAX_S
MAX_MS = MS_PER_S * MAX_S

DEFAULT_LABEL = "Made by t.me/sliva0 script"

SIZE_WARNING_TEMPLATE = (
    "Warning: {}, which is why it isn't a valid telegram sticker. Lower the "
    "resolution and/or number of frames of the original file and try again.")

LENGTH_WARNING_TEMPLATE = (
    f'Warning: file "{{}}" is longer than {MAX_S} seconds, '
    'so it will be sped up to fit within telegram limits.')

DESCRIPTION = """
Simple .gif to .tgs converter cli utility.

usage examples:
$ %(prog)s -i input.gif
input.gif -> input.tgs

$ %(prog)s -i first.gif -i second.gif sticker.tgs -y
first.gif -> first.tgs
second.gif -> "sticker.tgs
"""


def open_gif_file(path) -> SourceAnimationType:
    image = Image.open(path)
    durations = []
    frames = []

    for frame_index in range(image.n_frames):
        image.seek(frame_index)

        durations.append(image.info["duration"])
        frames.append(np.array(image.convert("RGBA")))

    if (total_duration := sum(durations)) > MAX_MS:
        print(LENGTH_WARNING_TEMPLATE.format(path))
        # converts milliseconds into frames amount
        # and speed up whole animation to 3 seconds
        durations = [d * MAX_FRAMES / total_duration for d in durations]
    else:
        # just converts milliseconds into frames amount
        durations = [d * FPS / MS_PER_S for d in durations]

    return durations, frames


def save_tgs(lottie, path: Path):
    compressed_json = json.dumps(
        lottie,
        ensure_ascii=False,
        separators=(',', ':'),
    )

    with gzip.open(path, 'wb', compresslevel=9) as file:
        file.write(compressed_json.encode('utf-8'))

    if len(compressed_json) > SIZE_1MB:
        msg = f'raw data of file "{path}" is larger than 1Mb'
        print(SIZE_WARNING_TEMPLATE.format(msg))

    elif path.stat().st_size > SIZE_64KB:
        msg = f'file "{path}" is larger than 64Kb'
        print(SIZE_WARNING_TEMPLATE.format(msg))


class IOFiles(argparse.Action):
    OUTPUT_FILE_DEFAULT_SUFFIX = ".tgs"
    ARGUMENT_AMOUNT_ERROR = ('each "{}" argument requires an input file and '
                             'optionally an output file, got {} arguments: {}')

    def __call__(self,
                 parser,
                 namespace,
                 values: list[str],
                 _option_string=None):

        items = getattr(namespace, self.dest, None)
        if items is None:
            items = []

        amount = len(values)
        if amount > 2:
            parser.error(
                self.ARGUMENT_AMOUNT_ERROR.format(
                    self.dest,
                    amount,
                    ", ".join(map(repr, values)),
                ))

        infile, *outfile = map(Path, values)

        if not infile.exists():
            parser.error(f'file "{infile}" does not exist')

        if outfile:
            outfile = outfile[0]
        else:
            # generating default output file path
            outfile = infile.with_suffix(self.OUTPUT_FILE_DEFAULT_SUFFIX)

        items.append((infile, outfile))
        setattr(namespace, self.dest, items)


def get_args():
    parser = argparse.ArgumentParser(
        prog="pixelart2tgs",
        description=DESCRIPTION,
        usage="%(prog)s -i infile [outfile] [-i ...] [-y] [-l LABEL]",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-i",
        dest="input",
        nargs="+",
        metavar=('in', 'out'),
        action=IOFiles,
        required=True,
        help="input .gif file and optionally an output .tgs file paths",
    )
    parser.add_argument(
        "-y",
        dest="force_overwrite",
        action="store_true",
        help="force overwrite all output files",
    )
    parser.add_argument(
        "-l",
        dest="label",
        default=DEFAULT_LABEL,
        help="name that can be read when unpacking "
        "the sticker by third-party programs",
    )
    return parser.parse_args()


@contextmanager
def error_handling(process_name: str):
    try:
        yield
    except Exception:
        exc = traceback.format_exc().strip().split("\n")[-1]
        print(f"{process_name} error: {exc}")
        exit(1)


def main():
    args = get_args()

    for infile, outfile in args.input:
        if not args.force_overwrite and outfile.exists():
            question = f'File "{outfile}" already exists. Overwrite? [y/n] '

            if input(question).strip().lower() != "y":
                print(f'"{infile}" -> "{outfile}" skipped.')
                continue

        with error_handling("File reading"):
            source = open_gif_file(infile)

        with error_handling("Data conversion"):
            lottie = generate_lottie(source, args.label)  # type: ignore

        with error_handling("File saving"):
            save_tgs(lottie, outfile)  # type: ignore

        print(f'File "{outfile}" saved.')


if __name__ == "__main__":
    main()