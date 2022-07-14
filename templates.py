def lottie(length: float, label: str, shift: tuple[float, float], scale: float,
           shapes: list[dict]):
    return {
        "v": "5.7.2",  # hardcoded version of format
        "fr": 60,  # frames per second
        "ip": 0,  # start frame index
        "op": length,  # end frame index
        "w": 512,  # resolution
        "h": 512,
        "nm": label,  # name
        "layers": (layer(shift, scale, shapes, length), )  # one layer 
    }


def layer(shift: tuple[float, float], scale: float, groups: list[dict],
          length: float):
    return {
        "ty": 4,  # layer type, 4 is common 
        "ks": {  # layers specs
            "p": static_value(shift),  # position
            "s": static_value((100 * scale, ) * 2)  # scale
            # a (anchor), o (opacity) and r (rotation) skipped
        },
        "shapes": groups,  # elements of the layer
        "ip": 0,  # start frame
        "op": length  # end frame
    }


def group(contours: list[dict], scale: float, color, opacity, position):
    return {
        "ty":
        "gr",  # shape type - group
        "it": [  # list of group subshapes
            *contours,  # all contours
            {
                "ty": "mm",  # thing that combines all contours
                "mm": 1  # in the right way
            },
            {
                "ty": "st",  # type - stroke
                "c": color,
                "o": static_value(50),  # opacity
                "w": static_value(0.5 / scale)  # stroke width
            },
            {
                "ty": "fl",  # type - fill
                "c": color
            },
            {
                "ty": "tr",  # type - transform (required in groups)
                "p": position,  # group position
                "o": opacity  # group opacity
            },
        ]
    }


def contour(points: list[tuple[int, int]]):
    curves = blank_curves(len(points))
    return {
        "ty":
        "sh",  # type - shape (contour)
        "ks":
        static_value({  # shape specs
            "i": curves,  # parameters that define the curvature of the line
            "o": curves,  # filled with empty lists to straight line
            "v": points,  # contour vertices
            "c": True  # cycled (first vertice connected to last)
        }),
    }


def blank_curves(length: int):
    return ((), ) * length


def static_value(value):
    return {"k": value}


def animated_value(keyframes: list[dict]):
    return {
        "a": 1,  # animated: true
        "k": keyframes,  # keyframe list
    }


def keyframe(time: float, value):
    return {
        "t": round(time, 1),  # time (frame index)
        "s": value,
        "h": 1,  # sets the animation to a rapid jump
    }
