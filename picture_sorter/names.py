"""
File for names manipulation.
"""

import math


def generate_names(
    name: str, ext: str, size: int, suffix: str = "_#"
) -> tuple[str, ...]:
    """
    Generate a sequence of systematically numbered names.

    Each generated name consts of:
        base name + suffix + zero-padded index + extension.

    :param name: Base name to use.
    :param ext: File extension (e.g., ".txt").
    :param size: Number of names to generate.
    :param suffix: String appended before the index (default: "_#").
    :return: Tuple of generated names as strings.
    """
    # Number of digits needed for zero-padding (e.g., size=100 -> 3 digits)
    zero_pad = math.ceil(math.log10(size + 1))

    return tuple(
        f"{name}{suffix}{i:0{zero_pad}d}{ext}" for i in range(1, size + 1)
    )
