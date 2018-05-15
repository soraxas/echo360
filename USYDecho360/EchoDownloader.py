import dateutil.parser
import os
import sys

from USYDecho360.hls_downloader import Downloader

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class EchoDownloader(object):

    def __init__(self, course, output_dir, date_range, username, password, use_local_binary=False, use_chrome=False):
        self._course = course
        root_path = os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__))
        if output_dir == '':
            output_dir = root_path
        self._output_dir = output_dir
        self._date_range = date_range
        self._username = username
        self._password = password

        # define a log path for phantomjs to output, to prevent hanging due to PIPE being full
        log_path = os.path.join(root_path, 'webdriver_service.log')

        # self._useragent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36"

        self._useragent = "Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25"
        # self._driver = webdriver.PhantomJS()

        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 "
            "(KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25"
        )
        if use_local_binary:
            if use_chrome:
                from USYDecho360.binary_downloader.chromedriver import get_bin
            else:
                from USYDecho360.binary_downloader.phantomjs import get_bin
            kwargs = {'executable_path' : get_bin(),
                      'desired_capabilities':dcap,
                      'service_log_path':log_path}
        else:
            kwargs = {}
        if use_chrome:
            from selenium.webdriver.chrome.options import Options
            opts = Options()
            opts.add_argument("user-agent={}".format(self._useragent))
            kwargs['chrome_options'] = opts
            self._driver = webdriver.Chrome(**kwargs)
        else:
            self._driver = webdriver.PhantomJS(**kwargs)

        # Monkey Patch, set the course's driver to the one from downloader
        self._course.set_driver(self._driver)
        self._videos = []

    def login(self):
        # Initialize to establish the 'anon' cookie that Echo360 sends.
        self._driver.get(self._course.url)
        # First see if we have successfully access course page without the need to login
        # for example: https://view.streaming.sydney.edu.au:8443/ess/portal/section/ed9b26eb-a785-4f4e-bd51-69f3faab388a
        if self._driver.find_elements_by_id('j_username'):
            self.loginWithCredentials()
        else:
            # check if it is network error
            if '<html><head></head><body></body></html>' in self._driver.page_source:
                print('Failed!')
                print('  > Failed to connect to server, is your internet working...?')
                exit(1)
            elif 'check your URL' in self._driver.page_source:
                print('Failed!')
                print('  > Failed to connet to course page, is the uuid correct...?')
                exit(1)
            else:
                # Should be only for the case where login details is not required left
                print('INFO: No need to login :)')
        print('Done!')

    def loginWithCredentials(self):
        # retrieve username / password if not given before
        if self._username is None or self._password is None:
            print('Credentials needed...')
            if self._username is None:
                if sys.version_info < (3,0): # special handling for python2
                    input = raw_input
                else:
                    from builtins import input
                self._username = input('Unikey: ')
            if self._password is None:
                import getpass
                self._password = getpass.getpass('Passowrd for {0}: '.format(self._username))
        # Input username and password:
        user_name = self._driver.find_element_by_id('j_username')
        print(user_name)
#        user_name.clear()
        user_name.send_keys(self._username)

        user_passwd = self._driver.find_element_by_id('j_password')
#        user_passwd.clear()
        user_passwd.send_keys(self._password)

        login_btn = self._driver.find_element_by_id('login-btn')
        login_btn.submit()

        # test if the login is success
        if self._driver.find_elements_by_id('j_username'):
            print('Failed!')
            print('  > Failed to login, is your username/password correct...?')
            exit(1)

        # hot patch for cavas (canvas.sydney.edu.au) where uuid is hidden in page source
        # we detect it by trying to retrieve the real uuid
        import re
        uuid = re.search('/ess/client/section/([0-9a-zA-Z]{8}-[0-9a-zA-Z]{4}-[0-9a-zA-Z]{4}-[0-9a-zA-Z]{4}-[0-9a-zA-Z]{12})',
                         self._driver.page_source)
        if uuid is not None:
            uuid = uuid.groups()[0]
            self._course._uuid = uuid

    def download_all(self):
        sys.stdout.write('>> Logging into "{0}"... '.format(self._course.url))
        sys.stdout.flush()
        self.login()
        sys.stdout.write('>> Retrieving echo360 Course Info... ')
        sys.stdout.flush()
        videos = self._course.get_videos().videos
        print('Done!')
        # change the output directory to be inside a folder named after the course
        self._output_dir = os.path.join(self._output_dir, '{0} - {1}'.format(
            self._course.course_id, self._course.course_name).strip())
        #
        filtered_videos = [video for video in videos if self._in_date_range(video.date)]
        print('=' * 60)
        print('    Course: {0} - {1}'.format(self._course.course_id, self._course.course_name))
        print('      Total videos to download: {0} out of {1}'.format(len(filtered_videos), len(videos)))
        print('=' * 60)

        downloaded_videos = []
        for video in reversed(list(filtered_videos)):
            lecture_number = self._find_pos(videos, video)
            title = "Lecture {}".format(lecture_number+1)
            filename = self._get_filename(self._course.course_id, video.date, title)
            self._download_as(video.url, filename)
            downloaded_videos.insert(0, filename)
        print(self.success_msg(self._course.course_name, downloaded_videos))
        self._driver.close()

    @property
    def useragent(self):
        return self._useragent

    @useragent.setter
    def useragent(self, useragent):
        self._useragent = useragent

    def _download_as(self, video, filename):
        print('')
        print('-'*60)
        print('Downloading "{}"'.format(filename))
        echo360_downloader = Downloader(50)
        echo360_downloader.run(video, self._output_dir)

        # rename file
        ext = echo360_downloader.result_file_name
        ext = ext[ext.rfind('.')+1:]
        os.rename(os.path.join(echo360_downloader.result_file_name), os.path.join(self._output_dir, '{0}.{1}'.format(filename, ext)))
        print('-'*60)

    def _initialize(self, echo_course):
        self._driver.get(self._course.url)

    def _get_filename(self, course, date, title):
        return "{} - {} - {}".format(course, date, title)

    def _in_date_range(self, date_string):
        the_date = dateutil.parser.parse(date_string).date()
        return self._date_range[0] <= the_date and the_date <= self._date_range[1]

    def _find_pos(self, videos, the_video):
        for i, video in enumerate(videos):
            if video == the_video: # compare by object id, because date could possibly be the same in some case.
                return i

    def success_msg(self, course_name, videos):
        bar = '=' * 65
        msg = '\n{0}\n'.format(bar)
        msg += '    Course: {0} - {1}'.format(self._course.course_id, self._course.course_name)
        msg += '\n{0}\n'.format(bar)
        msg += '    Successfully downloaded:\n'
        for i in videos:
            msg += '        {}\n'.format(i)
        msg += '{0}\n'.format(bar)
        return msg
