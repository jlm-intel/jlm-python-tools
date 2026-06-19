"""
This script scans a specified local and remote directory for contents and prints the names of files only found in the remote directory.
The script takes two arguments: the local directory to scan for filenames, and the remote directory to compare against. The script will recursively search through
the remote directory and print any files that are not found in the local directory.

An application for this is to determine if there are any obsolete files in a backup location that might be taking up extra space, or to find files
that were deleted locally but still exist in the remote location. This can be used as a cleanup tool to identify files that can be safely deleted
from the remote location.
"""

__author__ = "Josh Mayfield"
__copyright__ = "Copyright 2026, jlm-python-tools"
__license__ = "GPL-3.0"
__maintainer__ = "Josh Mayfield"
__email__ = "joshmayfield@outlook.com"

import argparse  # for argument parsing
import glob  # for recursive file finding
import os  # for path commands


def parse_args():
    parser = argparse.ArgumentParser(description="Scans a specified directory for contents and prints the filenames.")
    parser.add_argument("local_dir", type=str, help="Local directory to scan for filenames.")
    parser.add_argument("remote_dir", type=str, help="Remote directory to compare against.")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()

    local_dir = args.local_dir
    remote_dir = args.remote_dir
    verbose = True

    print(f"Searching for potentially orphaned files in {remote_dir}. This might take a while...")
    searchspec = os.path.join(remote_dir, "**", "*")
    filelist = glob.iglob(searchspec, recursive=True)
    remote_len = len(remote_dir)
    remote_len += 1
    print(f"Processing orphaned files in {remote_dir}. This might take a while...")
    DEBUG_LIMITER = 0
    for cur_file in filelist:
        if os.path.isdir(cur_file):
            continue
        target_path = os.path.join(local_dir, cur_file[remote_len:])
        if not os.path.exists(target_path):
            # file not found in local directory, cur_file is orphaned
            if verbose:
                # below converts the string to a bytes array and strips out any non-ascii characters.
                # this is only required for cases when you are redirecting output to a file in windows.
                # the default console supports printing utf-8
                print(f"Orphaned file: {bytes(cur_file, 'utf-8').decode('ascii', 'ignore')}")
