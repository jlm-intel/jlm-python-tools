# jlm-python-tools
Python-based utility scripts I've written to perform a number of mostly file-related tasks. These are all tools I've written to perform day-to-day
tasks on Windows and Linux systems.

Here's a quick run-down of what's available here:

## batchrename.py
Recursively search for files of a given filename and rename them to a target filename, overwriting existing files with the target name.

## batchtypechange.py
Recursively searches a given directory for files of a certain file type and replaces their filename extension.

## collectfiles.py
Locate a list of files (by full or partial filename) in a nested directory structure and copy them to a target directory. Optional support to parse the output from the cubase-project-plugins tool as a filename list.

## comparefiles.py
Compares two text files and provides a report on which lines are different or unique between the two.

## file_utilities.py
File utility methods used by the other scripts.

## findorphanedfiles.py
Locates files in a remote directory that do not exist in a local directory (for identifying obsolete/extra files).

## folderclean.py
Organizes messy folders by moving files of different types into category-specific subdirectories.

## foldersync.py
Synchronizes directories by copying new or updated files from a source directory to a target location. Optionally removes orphaned files from the target.

## multisync.py
Bidirectional sync tool for updating files that are shared by multiple computers.

## networkstatus.py
Repeatedly tests your internet connection and keeps a log of when the connection drops and comes back online.

## nostamps.py
Removes timestamps of a variety of different formats from log files to enable more precise comparison between different files.
