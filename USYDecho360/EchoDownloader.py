import dateutil.parser
import os
import sys

from selenium import webdriver
import selenium
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from USYDecho360.hls_downloader import Downloader

class EchoDownloader(object):

    def __init__(self, course, output_dir, date_range, username, password, use_local_binary=False):
        self._course = course
        if output_dir == '':
            output_dir = os.path.dirname(os.path.realpath(__file__))
        self._output_dir = output_dir
        self._date_range = date_range

        # define a log path for phantomjs to output, to prevent hanging due to PIPE being full
        log_path = '{0}/phantomjs_service.log'.format(os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__)))

        # self._useragent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36"

        self._useragent = "Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25"
        # self._driver = webdriver.PhantomJS()

        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 "
            "(KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25"
        )
        if use_local_binary:
            from USYDecho360.phantomjs_binary_downloader import get_phantomjs_bin
            self._driver = webdriver.PhantomJS(executable_path=get_phantomjs_bin(), desired_capabilities=dcap, service_log_path=log_path)
        else:
            self._driver = webdriver.PhantomJS(desired_capabilities=dcap, service_log_path=log_path)


        # Monkey Patch, set the course's driver to the one from downloader
        self._course.set_driver(self._driver)

        # Initialize to establish the 'anon' cookie that Echo360 sends.
        sys.stdout.write('>> Logging into "{0}"... '.format(self._course.url))
        sys.stdout.flush()
        self._driver.get(self._course.url)

        # first try if we can access content without login
        # for example: https://view.streaming.sydney.edu.au:8443/ess/portal/section/ed9b26eb-a785-4f4e-bd51-69f3faab388a
        try:
            self._driver.find_element_by_id('j_username')
            # should show raise exception here if it does not need to login...

            # retrieve username / password if not given before
            if username is None or password is None:
                print('Credentials needed...')
                if username is None:
                    if sys.version_info < (3,0): # special handling for python2
                        input = raw_input
                    else:
                        from builtins import input
                    username = input('Unikey: ')
                if password is None:
                    import getpass
                    password = getpass.getpass('Passowrd for {0}: '.format(username))
            # Input username and password:
            user_name = self._driver.find_element_by_id('j_username')
            user_name.clear()
            user_name.send_keys(username)

            user_passwd = self._driver.find_element_by_id('j_password')
            user_passwd.clear()
            user_passwd.send_keys(password)

            login_btn = self._driver.find_element_by_id('login-btn')
            login_btn.submit()

            # test if the login is success
            try:
                self._driver.find_element_by_id('j_username')
            except selenium.common.exceptions.NoSuchElementException:
                print('Done!')
            else:
                print('Failed!')
                print('  > Failed to login, is your username/password correct...?')
                exit(1)

        except selenium.common.exceptions.NoSuchElementException:
            if self._driver.page_source.strip() == '<html><head></head><body></body></html>':
                print('Failed!')
                print('  > Failed to connect to server, is your internet working...?')
                exit(1)
            print('Done!')
            print('INFO: No need to login :)')

        # print(self._driver.page_source)
        self._videos = []

    def download_all(self):
        sys.stdout.write('>> Retrieving echo360 Course Info... ')
        sys.stdout.flush()
        videos = self._course.get_videos().videos
        print('Done!')
        # change the output directory to be inside a folder named after the course
        self._output_dir += '/{0} - {1}'.format(self._course.course_id, self._course.course_name)
        #
        filtered_videos = [video for video in videos if self._in_date_range(video.date)]
        print('=' * 60)
        print('    Course: {0} - {1}'.format(self._course.course_id, self._course.course_name))
        print('      Total videos to download: {0} out of {1}'.format(len(videos), len(filtered_videos)))
        print('=' * 60)

        downloaded_videos = []
        for video in reversed(list(filtered_videos)):
            lecture_number = self._find_pos(videos, video)
            title = "Lecture {}".format(lecture_number+1)
            filename = self._get_filename(self._course.course_id, video.date, title)
            self._download_as(video.url, filename)
            downloaded_videos.insert(0, filename)
        print(self.success_msg(self._course.course_name, downloaded_videos))

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
