lottie = lambda time, layers: {
    "v": "5.7.2",
    "fr": 60,
    "ip": 0,
    "op": time,
    "w": 512,
    "h": 512,
    "nm": "Made by @sliva0 script",
    "layers": layers
}

layer = lambda time_i, time_o, shapes, shift, scale: {
    "ty": 4,
    "ks": {
        "p": {
            "k": shift
        },
        "s": {
            "k": [100 * scale, 100 * scale]
        }
    },
    "shapes": shapes,
    "ip": time_i,
    "op": time_o
}

group = lambda contours, color, scale, opacity: {
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
            "c": {
                "k": color
            },
            "o": {
                "k": 100 * opacity,
            },
            "w": {
                "k": 1 / scale
            }
        },
        {
            "ty": "fl",
            "c": {
                "k": color
            },
            "o": {
                "k": 100 * opacity
            }
        },
        {
            "ty": "tr"
        },
    ]
}

contour = lambda points: {
    "ty": "sh",
    "ks": {
        "k": {
            "i": [[]] * len(points),
            "o": [[]] * len(points),
            "v": points
        }
    }
}