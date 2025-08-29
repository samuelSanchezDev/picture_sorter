"""
Command-line interface for picture_sorter.
"""

import argparse
import logging
import os
import pathlib
from typing import Any

from picture_sorter.dates import parse_date, NoDateFound
from picture_sorter.files import (
    compress_directory,
    copy_files,
    delete_directory,
    group_by_hash,
    recursive_list,
)
from picture_sorter.paths import generate_destination


MEDIA_EXTENSIONS = [
    ".JPEG",
    ".JPG",
    ".GIF",
    ".PNG",
    ".WEBP",
    ".RAW",
    ".MP4",
    ".MKV",
]

DEPTH2STRFTIME = {
    1: "%Y",
    2: "%Y/%m - %b",
    3: "%Y/%m - %b/%d - %a",
}

DEPTH2INT = {"none": 0, "year": 1, "month": 2, "day": 3}

NO_DATE = "no-date"
TMP_FOLDER = "tmp"


def save_media(
    base_dirs: list[pathlib.Path],
    out_dir: pathlib.Path,
    depth: int,
    compress: str | None,
) -> None:

    def media_ext(filename: str | pathlib.Path) -> bool:
        _, ext = os.path.splitext(filename)
        return ext.upper() in MEDIA_EXTENSIONS

    # Get all media files
    all_media_files = []
    for base_dir in base_dirs:
        logging.info("Listing media files in the directory '%s'.", base_dir)
        files_found = recursive_list(base_dir, media_ext)
        logging.info("Found %d files", len(files_found))
        all_media_files.extend(files_found)
    logging.info("Total found: %d media files.", len(all_media_files))

    # Keep one copy from duplicate files.
    unique_media = [f[0] for f in group_by_hash(all_media_files)]
    logging.info("Unique files found: %d media files.", len(unique_media))

    # Generate destination paths using date.

    # No date classification
    if depth == 0:
        logging.info("Generating destination with-out date.")
        src_and_dst = generate_destination(unique_media)

    # Date classification
    else:
        strformat = DEPTH2STRFTIME[depth]
        destination: dict[str, list[Any]] = {}

        logging.info("Parsing date from file.")
        for file in unique_media:
            try:
                date = parse_date(file.name)
                date = date.strftime(strformat)
            except NoDateFound:
                date = NO_DATE

            destination.setdefault(date, []).append(file)

        src_and_dst = []

        logging.info("Generating destination from date.")
        for date, files in destination.items():
            src_and_dst.extend(generate_destination(files, date))

    # Copy or compress files
    if compress is None:
        logging.info("Copying files to '%s'.", out_dir)
        copy_files(src_and_dst, out_dir)
    else:
        logging.info("Copying files to temporary directory '%s'.", TMP_FOLDER)
        copy_files(src_and_dst, TMP_FOLDER)
        logging.info(
            "Compressing '%s' into '%s.%s'.",
            TMP_FOLDER,
            out_dir,
            compress,
        )
        compress_directory(TMP_FOLDER, out_dir, compress)
        logging.info("Deleting temporary directory")
        delete_directory(TMP_FOLDER)


def main() -> None:
    """
    Main function.
    """

    parser = argparse.ArgumentParser(
        prog="picture_sorter",
        description="Organize media files by date and optionally compress the "
        "result.",
    )

    parser.add_argument(
        "--input",
        "-i",
        nargs="+",
        type=pathlib.Path,
        required=True,
        help="One or more input directories containing media files.",
        metavar="DIR",
        dest="input",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=pathlib.Path,
        required=True,
        help="Directory where to save the organized media.",
        metavar="DIR",
        dest="output",
    )

    parser.add_argument(
        "--depth",
        "-d",
        default="month",
        type=str,
        choices=("none", "year", "month", "day"),
        help=(
            "Level of date-based organization: "
            "'none' -> DIR/, "
            "'year' -> DIR/YYYY/, "
            "'month' -> DIR/YYYY/MM - Mon/, "
            "'day' -> DIR/YYYY/MM - Mon/DD - Day/ "
            "(default: month)."
        ),
        metavar="LEVEL",
        dest="depth",
    )

    parser.add_argument(
        "--compress",
        nargs="?",
        const="zip",
        default=None,
        type=str,
        choices=("zip", "tar", "gztar", "bztar", "xztar"),
        help=(
            "Optional: compress the output directory into an archive. "
            "If used without value, defaults to 'zip'. "
            "Valid formats: zip, tar, gztar, bztar, xztar."
        ),
        metavar="FORMAT",
        dest="compress",
    )

    parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        default=False,
        help="Debug flag.",
    )

    args = parser.parse_args()

    if args.debug is True:
        logging.basicConfig(
            format="%(asctime)s : %(levelname)s : %(message)s",
            datefmt="%m/%d/%Y %I:%M:%S %p",
            level=logging.DEBUG,
        )
    else:
        logging.basicConfig(
            format="%(asctime)s : %(levelname)s : %(message)s",
            datefmt="%m/%d/%Y %I:%M:%S %p",
            level=logging.INFO,
        )

    # Check
    base_dirs: list[pathlib.Path] = args.input
    for directory in base_dirs:
        if not directory.is_dir():
            raise NotADirectoryError(directory)

    out_dir: pathlib.Path = args.output
    if out_dir.exists():
        if not out_dir.is_dir():
            raise NotADirectoryError(out_dir)

    depth = DEPTH2INT[args.depth]

    save_media(base_dirs, out_dir, depth, args.compress)


if __name__ == "__main__":
    main()
