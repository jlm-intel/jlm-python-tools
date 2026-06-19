"""
This script attempts to pull a given url at a given interval of seconds in order to determine if there is an active internet connection.
Changes in connection status are written to a log file and printed to the console.
"""

__author__ = "Josh Mayfield"
__copyright__ = "Copyright 2026, jlm-python-tools"
__license__ = "GPL-3.0"
__maintainer__ = "Josh Mayfield"
__email__ = "joshmayfield@outlook.com"


import argparse  # for argument parsing
import os  # for path commands
import sys  # for exit
import time  # for sleep
import urllib.error
import urllib.request  # for url opening
from datetime import datetime

# connection status values
CONNECTION_UNKNOWN = 0
CONNECTION_FAILED = 1
CONNECTION_SUCCESSFUL = 2


def parse_args():
    parser = argparse.ArgumentParser(description="Keeps a log of disruptions in internet connectivity.")
    parser.add_argument("-i", "--interval_secs", type=int, required=False, default=30, help="Number of seconds between connectivity checks.")
    parser.add_argument("-u", "--url", type=str, required=False, default="https://www.google.com/", help="URL to check for connection availability.")
    parser.add_argument("-l", "--log_path", type=str, required=True, help="Log file for recording connection status.")
    parser.add_argument("-o", "--overwrite_existing", action="store_true", help="Overwrites pre-existing log file rather than appending it.")
    parser.add_argument(
        "-t", "--timeout", type=int, required=False, default=10, help="Connection timeout value in seconds (assuming failed connection on timeout)."
    )
    args = parser.parse_args()
    return args


def append_logfile(filename, output):
    print(output)
    try:
        file = open(filename, "a+")
        file.write(output + "\n")
        file.close()
    except Exception as e:
        print(f"ERROR: Error encountered writing to file {filename}: {e}")


def check_connection(url, timeout):
    success = True
    try:
        urllib.request.urlopen(url, timeout=timeout)
    except urllib.error.URLError:
        success = False
    except urllib.error.HTTPError:
        success = False
    return success


def format_output(connection_successful, current_time, last_time):
    formatted_line = ""
    conn_status = "succeeded"
    if connection_successful != CONNECTION_SUCCESSFUL:
        conn_status = "failed"
    time_diff = current_time - last_time
    datestring = current_time.strftime("%I:%M%p on %B %d, %Y")
    formatted_line = f"Connection {conn_status} at {datestring}, after {round(time_diff.total_seconds() / 60, 1)} minutes."
    return formatted_line


if __name__ == "__main__":
    args = parse_args()

    # print settings
    print(f"URL to check: {args.url}")
    print(f"Log file: {args.log_path}")
    print(f"Check interval (in seconds): {args.interval_secs}")
    if args.overwrite_existing:
        print(f"Will overwrite {args.log_path} if it exists.")
    else:
        print(f"Will append {args.log_path} if it exists.")

    # look for pre-existing file and remove if overwrite_existing set.
    if os.path.exists(args.log_path):
        if args.overwrite_existing:
            try:
                os.remove(args.log_path)
            except Exception as e:
                print(f"ERROR: Unable to delete file {args.log_path}: {e}")
                sys.exit(1)

    append_logfile(args.log_path, "Starting to monitor internet connection (press CTRL+C to stop)...")

    last_time = datetime.now()
    conn_status = CONNECTION_UNKNOWN
    while True:
        last_status = conn_status
        if not check_connection(args.url, args.timeout):
            conn_status = CONNECTION_FAILED
        else:
            conn_status = CONNECTION_SUCCESSFUL

        if conn_status != last_status:
            cur_time = datetime.now()
            formatted_line = format_output(conn_status, cur_time, last_time)
            append_logfile(args.log_path, formatted_line)
            last_time = cur_time

        time.sleep(args.interval_secs)
