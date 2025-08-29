"""
File for path manipulation.
"""

import logging
import pathlib

from .names import generate_names


def find_duplicate_names(
    files: list[pathlib.Path],
) -> tuple[list[pathlib.Path], list[tuple[pathlib.Path, ...]]]:
    """
    Identify unique and duplicate filenames within a list of files.

    :param files: List of file paths.
    :return: A tuple containing:
        - list of unique file paths (no duplicates found)
        - list of tuples, each containing file paths with duplicate names
    """
    name_groups: dict[str, list[pathlib.Path]] = {}
    logging.debug("Group files by name.")
    for file in files:
        filename = file.name
        logging.debug("Name: '%s' from '%s'.", filename, file)
        name_groups.setdefault(file.name, []).append(file)

    unique_names, duplicate_names = [], []
    for name_group in name_groups.values():
        if len(name_group) == 1:
            unique_names.append(name_group[0])
        else:
            duplicate_names.append(tuple(name_group))

    logging.debug(
        "From %d files, found %d files with unique name.",
        len(files),
        len(unique_names),
    )
    logging.debug(
        "From %d files, found %d groups of same name files.",
        len(files),
        len(duplicate_names),
    )

    return unique_names, duplicate_names


def generate_destination(
    files: list[pathlib.Path],
    destination: pathlib.Path | str = "",
    dup_suffix: str = "_#",
) -> list[tuple[pathlib.Path, pathlib.Path]]:
    """
    Generate destination paths for a list of files, renaming duplicates.

    :param files: List of file paths to map.
    :param destination: Base directory where destination files will be placed.
    :param dup_suffix: Suffix pattern for numbering duplicate files.
    :return: List of (source, destination) tuples.
    """
    destination = pathlib.Path(destination)
    src_and_dst: list[tuple[pathlib.Path, pathlib.Path]] = []

    logging.debug("Generating destination path.")
    unique_name, duplicate_name = find_duplicate_names(files)

    # Unique files keep their names
    logging.debug("Files with the same name.")
    for file in unique_name:
        dst = destination.joinpath(file.name)
        logging.debug("SRC: %s. DST: %s", file, dst)
        src_and_dst.append((file, dst))

    # Duplicate files get systematically numbered names
    logging.debug("Files renamed.")
    for group in duplicate_name:
        size = len(group)
        stem = group[0].stem
        ext = group[0].suffix

        names = generate_names(stem, ext, size, suffix=dup_suffix)
        for file, new_name in zip(group, names):
            dst = destination.joinpath(new_name)
            logging.debug("SRC: %s. DST: %s", file, dst)
            src_and_dst.append((file, dst))

    return src_and_dst
