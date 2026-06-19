"""
This script is intended to back up and restore files intended to be used across multiple computers. It uses a settings file to determine
which files to back up and where to back them up to. The settings file is a json file that contains a list of files to back up, and a profile
for each computer that uses the script. Each profile contains a local directory and a remote directory. The local directory is where the files
to be backed up are located, and the remote directory is where the files will be backed up to.

The "trick" to this script is that it syncs the files automatically. (If local files are newer they are backed up to the remote directory.
If the local files are older, they are copied FROM the remote directory.) You only have to run this script on each computer to keep the files in sync.
"""

__author__ = "Josh Mayfield"
__copyright__ = "Copyright 2026, jlm-python-tools"
__license__ = "GPL-3.0"
__maintainer__ = "Josh Mayfield"
__email__ = "joshmayfield@outlook.com"

import argparse  # for argument parsing
import os  # for path commands

from file_utilities import FileUtilitiesConstants, copy_file, copy_newer_file, load_json_file, save_json_file  # for my file methods


def parse_args():
    parser = argparse.ArgumentParser(
        description="Backs up and restores files intended to be used across \
                                     multiple computers."
    )
    parser.add_argument("cmd", type=str, help="Command: backup, restore, sync, or setup")
    args = parser.parse_args()
    return args


def setup(settings_path):
    """
    Sets up the settings file for the multisync script.

    Here is an example of a settings file that supports syncing two specific files across three different computers.
    The "single_files" section contains the relative paths of the files to be synced.
    The "profiles" section contains a sub-section for each computer that uses the script (the profile names are the Windows computer names).
    Each profile contains a "local_dir" and a "remote_dir". The "local_dir" is the root directory where the files to be synced are located.
    The "remote_dir" is the root directory where all synced files reside (on a cloud drive or a network share). The script will create a
    sub-directory under the "remote_dir" for each computer, and will copy the files to that sub-directory.

    {
        "single_files": [
            "Account\\ULTIMATEBLOOPER\\SavedVariables\\Rematch.lua",
            "Account\\ULTIMATEBLOOPER\\SavedVariables\\tdBattlePetScript.lua"
        ],
        "profiles": {
            "ANTEC-P280": {
                "local_dir": "F:\\programs32\\World of Warcraft\\_retail_\\WTF",
                "remote_dir": "C:\\Users\\joshm\\OneDrive\\Documents\\MultiSync"
            },
            "ASUSGU603": {
                "local_dir": "C:\\Program Files (x86)\\World of Warcraft\\_retail_\\WTF",
                "remote_dir": "C:\\Users\\joshm\\OneDrive\\Documents\\MultiSync"
            },
            "CYBERPOWERPC2": {
                "local_dir": "C:\\ExtraSpace\\World of Warcraft\\_retail_\\WTF",
                "remote_dir": "C:\\Users\\joshm\\OneDrive\\Documents\\MultiSync"
            }
        }
    }
    """
    print("INFO: Creating/updating settings file: " + settings_path)
    success = False

    # load file if it exists
    blob = load_settings(settings_path)
    computer_name = os.getenv("COMPUTERNAME")
    if blob is None:
        # file doesn't exist or no valid data
        blob = {
            "single_files": ["(relative_path_to_first_file)", "(relative_path_to_second_file)"],
            "profiles": {computer_name: {"local_dir": "local_root_directory", "remote_dir": "backup_root_directory"}},
        }
    else:
        # setup called but settings file successfully loaded. check to see if this computer already has a section.
        found_current = False
        for cur_prof in blob["profiles"]:
            if cur_prof == computer_name:
                found_current = True

        if found_current:
            print("INFO: A profile already exists for computer: " + computer_name)
        else:
            print("INFO: Creating a new profille for computer: " + computer_name)
            new_prof = {"local_dir": "local_root_directory", "remote_dir": "backup_root_directory"}
            blob["profiles"][computer_name] = new_prof

    success = save_json_file(settings_path, blob)
    if success:
        print("INFO: Settings file is: " + settings_path + ", edit this profile to complete setup: " + computer_name)
    else:
        print(f"ERROR: Unable to configure settings file {settings_path}")

    return success


def load_settings(settings_path):
    blob = load_json_file(settings_path)
    if blob is None:
        print("ERROR: Unable to load settings file: " + settings_path)

    return blob


def validate_profile(settings):
    success = False
    computer_name = os.getenv("COMPUTERNAME")

    try:
        blob = settings["profiles"]
        blob2 = blob[computer_name]

        success = os.path.exists(blob2["local_dir"]) and os.path.exists(blob2["remote_dir"])

        if not success:
            print("Can't confirm existence of local_dir or remote_dir. Check your profile for " + computer_name)
    except Exception as e:
        print("ERROR: " + str(e))

    return success


def backup(settings):
    computer_name = os.getenv("COMPUTERNAME")
    copied = 0
    errors = 0

    # get current computer's profile
    profile = settings["profiles"][computer_name]

    # enumerate through single_files
    for cur_file in settings["single_files"]:
        # build path to local_dir + cur_file
        source_path = os.path.join(profile["local_dir"], cur_file)

        # check if file exists
        # print warning if file doesn't exist and continue to next file
        if not os.path.exists(source_path):
            print(f"ERROR: Cannot find file: {source_path}")
            errors += 1
            continue

        # build path to backup path (remote_dir + computer_name + cur_file)
        target_path = os.path.join(profile["remote_dir"], computer_name, cur_file)

        print(f"Backing up {source_path}...")
        if FileUtilitiesConstants.RESULT_ERROR == copy_file(source_path, target_path):
            errors += 1
        else:
            copied += 1

    return copied, errors


def sync(settings):
    computer_name = os.getenv("COMPUTERNAME")
    copied = 0
    errors = 0
    skipped = 0

    # get current computer's profile
    profile = settings["profiles"][computer_name]

    # back up current computer's files
    backup(settings)

    # enumerate through single_files
    for cur_file in settings["single_files"]:
        # build path to local_dir + cur_file (local_path)
        local_path = os.path.join(profile["local_dir"], cur_file)

        # build path to remote_dir + "sync_directory" + cur_file (sync_path)
        sync_path = os.path.join(profile["remote_dir"], "sync_directory", cur_file)

        # don't move files, but do use sync mode (bidirectional)
        copy_result = copy_newer_file(local_path, sync_path, False, True)
        if copy_result == FileUtilitiesConstants.RESULT_ERROR:
            errors += 1
        elif copy_result == FileUtilitiesConstants.RESULT_SKIPPED:
            skipped += 1
        else:
            copied += 1

    return copied, errors, skipped


if __name__ == "__main__":
    args = parse_args()

    program_dir = os.path.dirname(__file__)
    print(program_dir)
    settings_path = os.path.join(program_dir, "multisync.json")

    if not os.path.exists(settings_path):
        print("INFO: Settings file not found. Creating: " + settings_path)
        setup(settings_path)

    settings = load_settings(settings_path)
    success = validate_profile(settings)

    match args.cmd:
        case "setup":
            setup(settings_path)
        case "backup":
            copied, errors = backup(settings)
            print(f"INFO: Backed up {copied} files with {errors} errors.")
        case "restore":
            # TODO
            print("restore TBD")
        case "sync":
            copied, errors, skipped = sync(settings)
            print(f"Copied {copied} and skipped {skipped} files, with {errors} errors.")
        case _:
            print("ERROR: Unrecognized command: " + args.cmd)
