import argparse
import os
import sys
import re

from USYDecho360.exceptions import EchoLoginError
from USYDecho360.downloader import EchoDownloader
from USYDecho360.course import EchoCourse
from datetime import datetime


_DEFAULT_BEFORE_DATE = datetime(2900, 1, 1).date()
_DEFAULT_AFTER_DATE = datetime(1100, 1, 1).date()


def try_parse_date(date_string, fmt):
    try:
        return datetime.strptime(date_string, fmt).date()
    except:
        print("Error parsing date input:", sys.exc_info())
        sys.exit(1)


def handle_args():
    parser = argparse.ArgumentParser(description="Download lectures from Echo360 portal.")
    parser.add_argument("url",
                        help="Full URL of the echo360 course page, \
                              or only the UUID (which defaults to USYD). \
                              The URL of the course's video lecture page, \
                              for example: http://recordings.engineering.illinois.edu/ess/portal/section/115f3def-7371-4e98-b72f-6efe53771b2a)",
                        metavar="ECHO360_URL")
    parser.add_argument("--output", "-o",
                        help="Path to the desired output directory. The output \
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
    parser.add_argument("--unikey", "-u",
                        dest="unikey",
                        help="Your unikey for your University of \
                              Sydney elearning account",
                        metavar="UNIKEY")
    parser.add_argument("--password", "-p",
                        dest="password",
                        help="Your password for your University of \
                              Sydney elearning account",
                        metavar="PASSWORD")
    parser.add_argument("--download-phantomjs-binary",
                        action='store_true',
                        default=False,
                        dest="download_binary",
                        help="Force the echo360.py script to download a local \
                              binary file for phantomjs (will override system bin)")
    parser.add_argument("--chrome",
                        action='store_true',
                        default=False,
                        dest="use_chrome",
                        help="Use Chrome Driver instead of phantomjs webdriver. You \
                              must have chromedriver installed in your PATH.")

    args = vars(parser.parse_args())
    course_url = args["url"]

    output_path = os.path.expanduser(args["output"]) if args["output"] is not None else "default_out_path"
    output_path = output_path if os.path.isdir(output_path) else "default_out_path"

    after_date = try_parse_date(args["after_date"], "%Y-%m-%d") if args["after_date"] else _DEFAULT_AFTER_DATE
    before_date = try_parse_date(args["before_date"], "%Y-%m-%d") if args["before_date"] else _DEFAULT_BEFORE_DATE

    username = args["unikey"]
    password = args["password"]
    # check if the given uuid is actually a full URL
    course_hostname = re.search('https?:[/]{2}[^/]*', course_url)  # would be none if it does not exists
    if course_hostname is not None:
        course_hostname = course_hostname.group()
    course_uuid = re.search('[^/]+(?=/$|$)', course_url)  # retrieve the last part of the URL
    course_uuid = course_uuid.group()

    return (course_uuid, course_hostname, output_path, after_date, before_date, username, password, args['download_binary'], args['use_chrome'])


def main():
    course_uuid, course_hostname, output_path, after_date, before_date, username, password, download_binary, use_chrome = handle_args()

    cmd_exists = lambda x: any(os.access(os.path.join(path, x), os.X_OK) for path in os.environ["PATH"].split(os.pathsep))
    # NOTE: local binary will always override system PATH binary
    use_local_binary = True

    if use_chrome:
        from USYDecho360.binary_downloader.chromedriver import ChromedriverDownloader as binary_downloader
        binary_type = 'chromedriver'
    else:
        from USYDecho360.binary_downloader.phantomjs import PhantomjsDownloader as binary_downloader
        binary_type = 'phantomjs'
    binary_downloader = binary_downloader()  # initialise class
    # First test for existance of localbinary file
    if not os.path.isfile(binary_downloader.get_bin()):
        # If failed, then test for existance of global executable in PATH
        if cmd_exists('chromedriver'):
            use_local_binary = False
        else:
            # None exists, download binary file
            start_download_binary(binary_downloader, binary_type)

    if download_binary:
        start_download_binary(binary_downloader, binary, manual=True)
        exit(0)

    course = EchoCourse(course_uuid, course_hostname)
    downloader = EchoDownloader(course, output_path, date_range=(after_date, before_date),
                                username=username, password=password,
                                use_local_binary=use_local_binary,
                                use_chrome=use_chrome)
    print('>>>  Download will use "{}" webdriver from {} executable  <<<'.format(
           'ChromeDriver' if use_chrome else 'PhantomJS',
           'LOCAL' if use_local_binary else 'GLOBAL'))
    downloader.download_all()


def _blow_up(self, str, e):
    print(str)
    print("Exception: {}".format(str(e)))
    sys.exit(1)


def start_download_binary(binary_downloader, binary_type, manual=False):
    print('='*65)
    if not manual:
        print('Binary file of {0} not found, will initiate a download process now...'.format(binary_type))
    binary_downloader.download()
    print('Done!')
    print('='*65)


if __name__ == '__main__':
    try:
        main()
    except EchoLoginError:
        # raise KeyboardInterrupt
        pass
