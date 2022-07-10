def lottie(length: float, label: str, shift: list[float], scale: float, shapes: list[dict]):
    return {
        "v": "5.7.2",
        "fr": 60,
        "ip": 0,
        "op": length,
        "w": 512,
        "h": 512,
        "nm": label,
        "layers": (layer(shift, scale, shapes, length), )
    }


def layer(shift: list[float], scale: float, groups: list[dict], length: float):
    return {
        "ty": 4,
        "ks": {
            "p": static_value(shift),
            "s": static_value((100 * scale, ) * 2)
        },
        "shapes": groups,
        "ip": 0,
        "op": length
    }


def group(contours: list[dict], scale: float, color, opacity, position):
    return {
        "ty":
        "gr",
        "it": [
            *contours,
            {
                "ty": "mm",
                "mm": 1
            },
            {
                "ty": "st",
                "c": color,
                "o": static_value(50),
                "w": static_value(0.5 / scale)
            },
            {
                "ty": "fl",
                "c": color
            },
            {
                "ty": "tr",
                "p": position,
                "o": opacity
            },
        ]
    }


def contour(points: list[tuple[int, int]]):
    curves = blank_curves(len(points))
    return {
        "ty": "sh",
        "ks": static_value({
            "i": curves,
            "o": curves,
            "v": points,
            "c": True
        }),
    }


def blank_curves(length: int):
    return ((), ) * length


def static_value(value):
    return {"k": value}


def animated_value(keyframes: list[dict]):
    return {"a": 1, "k": keyframes}


def keyframe(time: float, value):
    return {
        "t": round(time, 1),
        "s": value,
        "h": 1,
    }
