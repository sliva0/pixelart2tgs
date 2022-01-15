lottie = lambda length, label, shift, scale, shapes: {
    "v": "5.7.2",
    "fr": 60,
    "ip": 0,
    "op": length,
    "w": 512,
    "h": 512,
    "nm": label,
    "layers": [layer(shift, scale, shapes, length)]
}

layer = lambda shift, scale, groups, length: {
    "ty": 4,
    "ks": {
        "p": {
            "k": shift
        },
        "s": {
            "k": [100 * scale, 100 * scale]
        }
    },
    "shapes": groups,
    "ip": 0,
    "op": length
}

group = lambda contours, scale, color, opacity, position: {
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
            "o": opacity,
            "w": {
                "k": 1 / scale
            }
        },
        {
            "ty": "fl",
            "c": color,
            "o": opacity
        },
        {
            "ty": "tr",
            "p": position
        },
    ]
}

contour = lambda points: {
    "ty": "sh",
    "ks": {
        "k": {
            "i": [()] * len(points),
            "o": [()] * len(points),
            "v": points,
            "c": True
        }
    }
}

static_value = lambda value: {
    "k": value
}

animated_value = lambda keyframes: {
    "a": 1,
    "k": keyframes,
}

keyframe = lambda time, value: {
    "t": round(time, 1),
    "s": value,
    "h": 1,
}