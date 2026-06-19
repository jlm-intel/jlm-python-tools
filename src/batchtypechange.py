"""
Recursively searches a given directory for files of a certain file type and replaces their filename extension.

For example, to replace all ".doc" files with ".txt" files under "C:\MyDocs", you would run:
python batchtypechange.py "C:\MyDocs" --source "*.doc" --target "txt"
"""

__author__ = "Josh Mayfield"
__copyright__ = "Copyright 2026, jlm-python-tools"
__license__ = "GPL-3.0"
__maintainer__ = "Josh Mayfield"
__email__ = "joshmayfield@outlook.com"

import argparse  # for argument parsing
import glob  # filename expansion
import os  # for environ and scandir


def parse_args():
    parser = argparse.ArgumentParser(
        description="Recursively searches a directory for files matching a certain file type and replaces their extensions with a new filename extension."
    )
    parser.add_argument("dir", type=str, help="Directory to search for source files.")
    parser.add_argument(
        "--source", type=str, required=True, help='Filespec to search for ("*.doc").'
    )
    parser.add_argument(
        "--target",
        type=str,
        required=True,
        help='New filename extension to use, without wildcards or separators ("txt").',
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()

    source_filespec = args.source
    target_extention = args.target
    search_dir = args.dir
    successes = 0
    errors = 0

    print("Files to search for: " + source_filespec)
    print("Filename extension to use for renaming: " + target_extention)
    print("Directory to search for source files: " + search_dir)

    # locate source files
    searchspec = os.path.join(search_dir, "**")
    searchspec = os.path.join(searchspec, source_filespec)
    filelist = glob.glob(searchspec, recursive=True)

    # if none found, end
    if len(filelist) == 0:
        print(
            "ERROR: No files found matching " + source_filespec + " under " + search_dir
        )
        quit()

    for curfile in filelist:
        # debug - print found files
        # print(curfile)

        # if found, build new path to target file
        # new_target = os.path.join(
        #     os.path.dirname(curfile),
        #     os.path.basename(curfile))
        (filename_only, ext_only) = os.path.splitext(curfile)
        while len(ext_only) > 0:
            # keep removing extensions, if more found. (example: ".wma.mp3")
            (filename_only, ext_only) = os.path.splitext(filename_only)
        new_target = f"{filename_only}.{target_extention}"
        print(f"{curfile} -> {new_target}...")

        # rename/move source to target
        try:
            os.replace(curfile, new_target)
            successes += 1
        except IsADirectoryError:
            print("Source is a file but destination is a directory: " + new_target)
            errors += 1
        except NotADirectoryError:
            print("Source is a directory but destination is a file: " + new_target)
            errors += 1
        except PermissionError:
            print("Operation not permitted: " + new_target)
            errors += 1
        except OSError:
            print("OS error occurred: " + new_target)
            errors += 1

    # count successful replacements and errors
    print("Number of source files successfully moved: " + str(successes))
    print("Number of errors encountered: " + str(errors))
