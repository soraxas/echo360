import argparse
import os
import sys
import re
import logging
import time
from datetime import datetime
try:
    import pick
except ImportError as e:
    # check if this is windows, if so install windows curse on the fly
    if 'win32' not in sys.platform:
        raise e
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'windows-curses'])

from .echo_exceptions import EchoLoginError
from .downloader import EchoDownloader
from .course import EchoCourse, EchoCloudCourse

_DEFAULT_BEFORE_DATE = datetime(2900, 1, 1).date()
_DEFAULT_AFTER_DATE = datetime(1100, 1, 1).date()

_LOGGER = logging.getLogger(__name__)


def try_parse_date(date_string, fmt):
    try:
        return datetime.strptime(date_string, fmt).date()
    except ValueError:
        print("Error parsing date input:", sys.exc_info())
        sys.exit(1)


def handle_args():
    parser = argparse.ArgumentParser(
        description="Download lectures from  portal.")
    parser.add_argument(
        "url",
        help="Full URL of the echo360 course page, \
              or only the UUID (which defaults to USYD). \
              The URL of the course's video lecture page, \
              for example: http://recordings.engineering.illinois.edu/ess/portal/section/115f3def-7371-4e98-b72f-6efe53771b2a)",  # noqa
        metavar="ECHO360_URL")
    parser.add_argument(
        "--output",
        "-o",
        help="Path to the desired output directory. The output \
                             directory must exist. Otherwise the current \
                             directory is used.",
        metavar="OUTPUT_PATH")
    parser.add_argument(
        "--after-date",
        "-a",
        dest="after_date",
        help="Only download lectures newer than AFTER_DATE \
                             (inclusive). Note: this may be combined with \
                             --before-date.",
        metavar="AFTER_DATE(YYYY-MM-DD)")
    parser.add_argument(
        "--before-date",
        "-b",
        dest="before_date",
        help="Only download lectures older than BEFORE_DATE \
                              (inclusive). Note: this may be combined with \
                              --after-date",
        metavar="BEFORE_DATE(YYYY-MM-DD)")
    parser.add_argument(
        "--unikey",
        "-u",
        dest="unikey",
        help="Your unikey for your University of \
                              Sydney elearning account",
        metavar="UNIKEY")
    parser.add_argument(
        "--password",
        "-p",
        dest="password",
        help="Your password for your University of \
                              Sydney elearning account",
        metavar="PASSWORD")
    parser.add_argument(
        "--setup-credentials",
        action='store_true',
        default=False,
        dest="setup_credential",
        help="Open a chrome instance to expose an ability for user to log into \
                                any website to obtain credentials needed before proceeding. \
                                (implies using chrome-driver)"
    )
    parser.add_argument(
        "--download-phantomjs-binary",
        action='store_true',
        default=False,
        dest="download_binary",
        help="Force the echo360.py script to download a local \
                              binary file for phantomjs (will override system bin)"
    )
    parser.add_argument(
        "--chrome",
        action='store_true',
        default=False,
        dest="use_chrome",
        help="Use Chrome Driver instead of phantomjs webdriver. You \
                              must have chromedriver installed in your PATH.")
    parser.add_argument(
        "--firefox",
        action='store_true',
        default=False,
        dest="use_firefox",
        help="Use Firefox Driver instead of phantomjs webdriver. You \
                              must have geckodriver installed in your PATH.")
    parser.add_argument(
        "--interactive",
        '-i',
        action='store_true',
        default=False,
        help="Interactively pick the lectures you want, instead of download all \
                              (default) or based on dates .")
    parser.add_argument(
        "--debug",
        action='store_true',
        default=False,
        dest="enable_degbug",
        help="Enable extensive logging.")

    args = vars(parser.parse_args())
    course_url = args["url"]

    output_path = os.path.expanduser(
        args["output"]) if args["output"] is not None else "default_out_path"
    output_path = output_path if os.path.isdir(
        output_path) else "default_out_path"

    after_date = try_parse_date(
        args["after_date"],
        "%Y-%m-%d") if args["after_date"] else _DEFAULT_AFTER_DATE
    before_date = try_parse_date(
        args["before_date"],
        "%Y-%m-%d") if args["before_date"] else _DEFAULT_BEFORE_DATE

    username = args["unikey"]
    password = args["password"]
    # check if the given uuid is actually a full URL
    course_hostname = re.search(
        'https?:[/]{2}[^/]*',
        course_url)  # would be none if it does not exists
    if course_hostname is not None:
        course_hostname = course_hostname.group()
    else:
        _LOGGER.info(
            "Non-URL value is given, defaults to University of Sydney's echo system"
        )
        _LOGGER.info(
            "Use the full URL if you want to use this in other University")

    args_without_sensitive_info = dict(args)
    args_without_sensitive_info.pop('unikey', None)
    args_without_sensitive_info.pop('password', None)
    _LOGGER.debug("Input args: %s", args_without_sensitive_info)
    _LOGGER.debug("Hostname: %s, UUID: %s", course_hostname, course_url)

    webdriver_to_use = "phantomjs"
    if args['use_chrome']:
        webdriver_to_use = "chrome"
    elif args['use_firefox']:
        webdriver_to_use = "firefox"

    return (course_url, course_hostname, output_path, after_date, before_date,
            username, password, args['setup_credential'], args['download_binary'],
            webdriver_to_use, args['interactive'], args['enable_degbug'])


def main():
    (course_url, course_hostname, output_path, after_date, before_date,
     username, password, setup_credential, download_binary, webdriver_to_use,
     interactive_mode, enable_degbug) = handle_args()

    setup_logging(enable_degbug)

    usingEcho360Cloud = False
    if "echo360.org" in course_hostname:
        print("> Echo360 Cloud platform detected")
        print("> This implies setup_credential, and using web_driver")
        print(">> Please login with your SSO details and type continue when logged in.")
        print('-' * 65)
        usingEcho360Cloud = True
        setup_credential = True

    def cmd_exists(x):
        any(
            os.access(os.path.join(path, x), os.X_OK)
            for path in os.environ["PATH"].split(os.pathsep))

    # NOTE: local binary will always override system PATH binary
    use_local_binary = True

    if setup_credential and webdriver_to_use == 'phantomjs':
        # setup credentials must use web driver
        webdriver_to_use = 'chrome'
    if webdriver_to_use == 'chrome':
        from .binary_downloader.chromedriver import ChromedriverDownloader as binary_downloader
        binary_type = 'chromedriver'
    elif webdriver_to_use == 'firefox':
        from .binary_downloader.firefoxdriver import FirefoxDownloader as binary_downloader
        binary_type = 'geckodriver'
    else:
        from .binary_downloader.phantomjs import PhantomjsDownloader as binary_downloader
        binary_type = 'phantomjs'
    binary_downloader = binary_downloader()  # initialise class
    _LOGGER.debug("binary_downloader link: %s, bin path: %s",
                  binary_downloader.get_download_link(),
                  binary_downloader.get_bin())
    # First test for existance of localbinary file
    if not os.path.isfile(binary_downloader.get_bin()):
        # If failed, then test for existance of global executable in PATH
        if cmd_exists(binary_type):
            use_local_binary = False
            _LOGGER.debug("Using global binary file")
        else:
            # None exists, download binary file
            start_download_binary(binary_downloader, binary_type)
            _LOGGER.debug("Downloading binary file")

    if download_binary:
        start_download_binary(binary_downloader, binary_type, manual=True)
        exit(0)

    if usingEcho360Cloud:
        # echo360 cloud
        course_uuid = re.search('[^/]([0-9a-zA-Z]+[-])+[0-9a-zA-Z]+',
                                course_url).group()  # retrieve the last part of the URL
        course = EchoCloudCourse(course_uuid, course_hostname)
    else:
        # import it here for monkey patching gevent, to fix the followings:
        # MonkeyPatchWarning: Monkey-patching ssl after ssl has already been 
        # imported may lead to errors, including RecursionError on Python 3.6.
        from . import hls_downloader
        course_uuid = re.search('[^/]+(?=/$|$)',
                                course_url).group()  # retrieve the last part of the URL
        course = EchoCourse(course_uuid, course_hostname)
    downloader = EchoDownloader(
        course,
        output_path,
        date_range=(after_date, before_date),
        username=username,
        password=password,
        setup_credential=setup_credential,
        use_local_binary=use_local_binary,
        webdriver_to_use=webdriver_to_use,
        interactive_mode=interactive_mode)

    _LOGGER.debug('>>> Download will use "{}" webdriver from {} executable <<<'.format(
        binary_type, 'LOCAL'
        if use_local_binary else 'GLOBAL'))
    if setup_credential:
        run_setup_credential(downloader._driver, course_hostname, echo360_cloud=True)
        downloader._driver.set_window_size(0, 0)
    downloader.download_all()

def start_download_binary(binary_downloader, binary_type, manual=False):
    print('=' * 65)
    if not manual:
        print(
            'Binary file of {0} not found, will initiate a download process now...'.
            format(binary_type))
    binary_downloader.download()
    print('Done!')
    print('=' * 65)

def run_setup_credential(webdriver, url, echo360_cloud=False):
    webdriver.get(url)
    try:
        # for making it compatiable with Python 2 & 3
        input = raw_input
    except NameError:
        pass
    try:
        if echo360_cloud:
            print(" >> After you finished logging into echo360 cloud, the window "
                  "should be automatically redirected and continued. If it got stuck, "
                  "please contact the author :)")
        while True:
            if echo360_cloud:
                # automatically wait for the Auth Token from webdriver
                if any('ECHO_JWT' in c['name'] for c in webdriver.get_cookies()):
                    break
                time.sleep(2)
            else:
                user_inputs = input("> Type 'continue' and press [enter]\n")
                if user_inputs.lower() == 'continue':
                    break
    except KeyboardInterrupt:
        pass


def setup_logging(enable_degbug=False):
    # set up logging to file - see previous section for more details
    logging_level = logging.DEBUG if enable_degbug else logging.INFO
    root_path = os.path.dirname(
        os.path.abspath(sys.modules['__main__'].__file__))
    log_path = os.path.join(root_path, 'echo360Downloader.log')
    logging.basicConfig(
        level=logging_level,
        format='[%(levelname)s: %(asctime)s] %(name)-12s %(message)s',
        datefmt='%m-%d %H:%M',
        filename=log_path,
        filemode='w')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logging.getLogger('').addHandler(console)  # add handler to the root logger
