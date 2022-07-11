import gzip
import json
from pathlib import Path

import numpy as np
from PIL import Image

from converter_types import *
from lottie_generator import generate_lottie


import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-i", nargs="+", action="append")

def open_gif_file(path) -> SourceAnimationType:
    image = Image.open(path)
    source_animation = []

    for frame_index in range(image.n_frames):  #type: ignore
        image.seek(frame_index)
        duration = image.info["duration"] * 60 / 1000
        frame = image.convert("RGBA")
        source_animation.append((duration, np.array(frame)))

    return source_animation


def save_tgs(lottie, path):
    with gzip.open(path, 'wb', compresslevel=9) as file:
        compressed_json = json.dumps(lottie, ensure_ascii=False, separators=(',', ':'))
        file.write(compressed_json.encode('utf-8'))


LABEL = "Made by t.me/sliva0 script"

paths = [r"Deltarune\durgbow.gif"]

for path in map(Path, paths):
    out_path = path.parent.parent / path.with_suffix(".tgs")
    source = open_gif_file(path)

    print(f"generating {path.name}")
    lottie = generate_lottie(source, LABEL)

    print(f"saving {path.name}")
    save_tgs(lottie, out_path)