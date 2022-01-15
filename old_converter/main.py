import sys
import json
import gzip

from PIL import Image

import old_converter.converter as converter


def save_tgs(lottie, filepath):
    with gzip.open(filepath, 'wb', compresslevel=9) as out:
        out.write(json.dumps(lottie, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))


paths = ["./Deltarune/Other/spamton_fortnite_cutted.gif"] #sys.argv[1:]
print(paths)

for path in paths:
    out_path = path.split("/")[-1].split(".")[0] + ".tgs"
    img = Image.open(path)
    frames, durations = [], []

    for i in range(img.n_frames):  #type: ignore
        img.seek(i)
        duration = img.info["duration"]
        durations.append(duration * 60 / 1000)
        frame = img.convert("RGBA")
        x, y = frame.size
        frames.append(frame) #.resize((x // 2, y // 2), Image.NEAREST))

    print(out_path, durations, end="\n\n", sep="\n")

    lottie = converter.generate_lottie(frames, durations)
    save_tgs(lottie, out_path)