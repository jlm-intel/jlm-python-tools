"""
Cleans up messy folders (like Downloads) by moving files of certain types to separate directories. The script starts out with a default
set of directories and related file types, but you can configure your own by editing the generated JSON settings file.
"""

__author__ = "Josh Mayfield"
__copyright__ = "Copyright 2026, jlm-python-tools"
__license__ = "GPL-3.0"
__maintainer__ = "Josh Mayfield"
__email__ = "joshmayfield@outlook.com"

import argparse  # for argument parsing
import glob  # for filename expansion
import os  # for path commands

from file_utilities import FileUtilitiesConstants, copy_newer_file, load_json_file, save_json_file, verify_directory  # for my file methods

# configuration file:
# - categories section
# - each section is named after the directory where you want categories to go (images, videos, music, etc)
# - each section contains an array of file types or filespecs to include (see if glob will work for this)
# {
#    "categories": {
#      "images": [
#        "*.jpg",
#        "*.png",
#        "*.gif"
#      ],
#      "videos": [
#        "*.mkv",
#        "*.mp4"
#      ]
#    }
# }


def parse_args():
    # set up default settings filename
    program_dir = os.path.dirname(__file__)
    settings_default = os.path.join(program_dir, "folderclean.json")

    parser = argparse.ArgumentParser(description="Cleans up a directory by placing different types of files into sensible folders.")
    parser.add_argument("clean_dir", type=str, help="Directory you wish to clean up.")
    parser.add_argument("--archive_dir", type=str, required=False, help="Directory where you want to place cleaned-up files.")
    parser.add_argument("--settings_file", type=str, required=False, default=settings_default, help="Path of configuration file to use for settings.")
    parser.add_argument("--setup", action="store_true", help="Creates a template settings file which you must populate with your desired settings.")

    args = parser.parse_args()
    return args


def create_settings(settings_path):
    # check for existing file?
    blob = {
        "categories": {
            "Archives": ["*.zip", "*.rar"],
            "AudioFiles": ["*.aif", "*.m4a", "*.m4r", "*.mp3", "*.wav"],
            "Documents": ["*.pdf", "*.csv", "*.xlsx", "*.docx", "*.rtf", "*.txt"],
            "Images": ["*.gif", "*.jfif", "*.jpg", "*.jpeg", "*.pdn", "*.png", "*.psd", "*.webp"],
            "Programs": ["*.exe", "*.msi"],
            "Scripts": ["*.bat", "*.cmd", "*.py", "*.vbs"],
            "Videos": ["*.mov", "*.mp4", "*.webm"],
        }
    }

    success = save_json_file(settings_path, blob)
    if success:
        print(f"INFO: Created settings file {settings_path}")
    else:
        print(f"ERROR: Unable to create settings file {settings_path}")

    return success


def clean_directory(clean_dir, archive_dir, settings_path):
    success = False
    errors = 0
    moved = 0
    skipped = 0

    settings = load_json_file(settings_path)
    if settings is None:
        print(f"ERROR: Unable to load settings file {settings_path}")
        return success

    if not verify_directory(clean_dir, False):
        print(f"ERROR: {clean_dir} is missing or is not a directory")
        return success

    if not verify_directory(archive_dir, True):
        print(f"ERROR: Unable to find or create {archive_dir}")
        return success

    for cur_cat in settings["categories"]:
        print(f"INFO: Processing category {cur_cat}...")
        category_directory = os.path.join(archive_dir, cur_cat)
        for cur_spec in settings["categories"][cur_cat]:
            # print(f'INFO: Current filespec {cur_spec}')
            filelist = glob.glob(os.path.join(clean_dir, cur_spec))
            # don't have to verify target directory; copy_newer_file does that implicitly
            for cur_file in filelist:
                # make target filepath
                target = os.path.join(category_directory, os.path.basename(cur_file))
                copy_result = copy_newer_file(cur_file, target, True, False)
                if copy_result == FileUtilitiesConstants.RESULT_ERROR:
                    errors += 1
                elif copy_result == FileUtilitiesConstants.RESULT_SKIPPED:
                    skipped += 1
                else:
                    moved += 1

    print(f"INFO: Moved {moved} files to {archive_dir} with {skipped} skipped files and {errors} errors.")

    return success


if __name__ == "__main__":
    args = parse_args()

    # if archive_dir is set, use that, otherwise, default to clean_dir
    clean_dir = args.clean_dir
    archive_dir = clean_dir
    if args.archive_dir is not None:
        archive_dir = args.archive_dir

    # does this work for default settings path?
    settings_path = args.settings_file

    # DEBUG
    print(f"clean_dir: {clean_dir}")
    print(f"archive_dir: {archive_dir}")
    print(f"settings_path: {settings_path}")

    # if setup requested, create settings
    if args.setup:
        create_settings(settings_path)
        exit()

    clean_directory(clean_dir, archive_dir, settings_path)
