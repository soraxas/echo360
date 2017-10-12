import argparse
import json
import os
import sys

from datetime import datetime
from EchoCourse import EchoCourse
from EchoDownloader import EchoDownloader


_DEFAULT_BEFORE_DATE = datetime(2900, 1, 1).date()
_DEFAULT_AFTER_DATE = datetime(1100, 1, 1).date()

def try_parse_date(date_string, fmt):
    try:
        return datetime.strptime(date_string, fmt).date()
    except:
        print("Error parsing date input:", sys.exc_info())
        sys.exit(1)

def handle_args():
    parser = argparse.ArgumentParser(description="Download lectures from UIUC's Echo360 portal.")
    parser.add_argument("--uuid", "-u",
                        required=True,
                        help="Echo360 UUID for the course, which is found in \
                              the URL of the course's video lecture page (e.g. \
                              '115f3def-7371-4e98-b72f-6efe53771b2a' in \
                              http://recordings.engineering.illinois.edu/ess/portal/section/115f3def-7371-4e98-b72f-6efe53771b2a)",
                        metavar="COURSE_UUID")
    parser.add_argument("--titles", "-f",
                        help="Path to JSON file containing date to title \
                              mapping. See Readme.md for info on the \
                              required format",
                        metavar="TITLES_PATH")
    parser.add_argument("--output", "-o",
                        help="Path to the desired output directory The output \
                             directory must exist. Otherwise the current \
                             directory is used.",
                        metavar="OUTPUT_PATH")
    parser.add_argument("--after-date", "-a",
                        dest="after_date",
                        help="Only download lectures newer than AFTER_DATE \
                             (inclusive). Note: this may be combined with \
                             --before-date.",
                        metavar="AFTER_DATE(YYYY-MM-DD)")
    parser.add_argument("--before-date", "-b",
                        dest="before_date",
                        help="Only download lectures older than BEFORE_DATE \
                              (inclusive). Note: this may be combined with \
                              --after-date",
                        metavar="BEFORE_DATE(YYYY-MM-DD)")
    parser.add_argument("--unikey", "-k",
                        dest="unikey",
                        help="Your unikey for your University of \
                              Sydney elearning account",
                        metavar="UNIKEY")
    parser.add_argument("--password", "-p",
                        dest="password",
                        help="Your password for your University of \
                              Sydney elearning account",
                        metavar="PASSWORD")

    args = vars(parser.parse_args())
    course_uuid = args["uuid"]

    titles_path = os.path.expanduser(args["titles"]) if args["titles"] is not None else ""
    titles_path = titles_path if os.path.isfile(titles_path) else ""

    output_path = os.path.expanduser(args["output"]) if args["output"] is not None else ""
    output_path = output_path if os.path.isdir(output_path) else ""

    after_date = try_parse_date(args["after_date"], "%Y-%m-%d") if args["after_date"] else _DEFAULT_AFTER_DATE
    before_date = try_parse_date(args["before_date"], "%Y-%m-%d") if args["before_date"] else _DEFAULT_BEFORE_DATE

    username = args["unikey"]
    password = args["password"]

    if username is None:
        username = input('Unikey: ')
    if password is None:
        import getpass
        password = getpass.getpass('Passowrd for {0} : '.format(username))

    return (course_uuid, titles_path, output_path, after_date, before_date, username, password)

def main():
    course_uuid, titles_path, output_path, after_date, before_date, username, password = handle_args()

    titles = None
    if titles_path != "":
        with open(titles_path, "r") as titles_json:
            data = json.load(titles_json)
            titles = data["titles"] if "titles" in data else None

    course = EchoCourse(course_uuid, titles)
    downloader = EchoDownloader(course, output_path, date_range=(after_date, before_date), username=username, password=password)
    downloader.download_all()

def _blow_up(self, str, e):
    print(str)
    print("Exception: {}".format(str(e)))
    sys.exit(1)


if __name__ == '__main__':
    main()
