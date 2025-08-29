"""
File for file manipulation.
"""

import logging
import pathlib
import shutil
import hashlib
from collections.abc import Callable


def recursive_list(
    directory: pathlib.Path,
    filter_f: Callable[[str | pathlib.Path], bool] = lambda _: True,
) -> list[pathlib.Path]:
    """
    Recursively list all files in a directory, optionally applying a filter.

    :param directory: Directory path to search.
    :param filter_f: Optional filter function applied to each file.
                     Defaults to including all files.
    :return: List of pathlib.Path objects matching the filter.
    """
    filtered_files: list[pathlib.Path] = []

    logging.debug("Listing directory '%s'.", directory)
    for path in directory.rglob("*"):
        logging.debug("Listed '%s'.", path)
        if path.is_file() and filter_f(path):
            logging.debug("File accepted.")
            filtered_files.append(path)
    return filtered_files


def group_by_hash(
    files: list[pathlib.Path], algorithm: str = "sha256"
) -> list[tuple[pathlib.Path, ...]]:
    """
    Group files that have identical content by computing their hash digest.

    :param files: List of file paths to compare.
    :param algorithm: Hash algorithm (e.g., 'md5', 'sha1', 'sha256').
    :return: List of tuples, where each tuple contains files with identical
    hashes.
    """
    hash_groups: dict[bytes, list[pathlib.Path]] = {}
    logging.debug("Group files by hash (%s).", algorithm)
    for file in files:
        with file.open("rb") as f:
            digest = hashlib.file_digest(f, algorithm)
            logging.debug("File:'%s'. Hash:'%s'.", file, digest.hexdigest())

        hash_groups.setdefault(digest.digest(), []).append(file)

    logging.debug("Found %d unique files.", len(hash_groups.values()))
    return [tuple(group) for group in hash_groups.values()]


def copy_files(
    src_and_dst: list[tuple[pathlib.Path, pathlib.Path]],
    root_dir: pathlib.Path | str | None = None,
) -> None:
    """
    Copy a list of files to their destination paths.

    :param src_and_dst: List of (source, destination) path tuples.
                        Destination can be relative if root_dir is provided.
    :param root_dir: Optional base directory prepended to all destinations.
    """
    logging.debug("Copying %d files.", len(src_and_dst))
    for src, dst in src_and_dst:
        logging.debug("SRC: %s. DST: %s", src, dst)
        dst = (
            pathlib.Path(dst)
            if root_dir is None
            else pathlib.Path(root_dir) / dst
        )
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)


def compress_directory(
    directory: str | pathlib.Path,
    destination: str | pathlib.Path,
    file_format: str = "zip",
) -> None:
    """
    Compress a directory into an archive.

    :param directory: Directory to compress.
    :param destination: Output archive path without extension.
    :param file_format: Archive format ('zip', 'tar', etc.).
    """
    shutil.make_archive(str(destination), file_format, str(directory))


def delete_directory(
    directory: str | pathlib.Path,
) -> None:
    """
    Remove a directory.

    :param directory: Directory to delete.
    """
    shutil.rmtree(directory)
