def colors_256(color_, s):
    return f"\033[38;5;{str(color_)}m {s} \033[0;0m"


def red(s):
    return colors_256(160, s)


def purple(s):
    return colors_256(21, s)
