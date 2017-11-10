import dateutil.parser
import os
import sys

from selenium import webdriver
import selenium


class EchoDownloader(object):

    def __init__(self, course, output_dir, date_range, username, password):
        self._course = course
        if output_dir == '':
            output_dir = dir_path = os.path.dirname(os.path.realpath(__file__))
        self._output_dir = output_dir
        self._date_range = date_range

        # self._useragent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36"

        self._useragent = "Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25"
        # self._driver = webdriver.PhantomJS()

        from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 "
            "(KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25"
        )
        self._driver = webdriver.PhantomJS(desired_capabilities=dcap)


        # Monkey Patch, set the course's driver to the one from downloader
        self._course.set_driver(self._driver)

        # Initialize to establish the 'anon' cookie that Echo360 sends.
        print('Accessing {0}'.format(self._course.url))
        self._driver.get(self._course.url)

        try:
            # if error that means no need to enter username or password
            # for example: https://view.streaming.sydney.edu.au:8443/ess/portal/section/ed9b26eb-a785-4f4e-bd51-69f3faab388a
            # Input username and password:
            user_name = self._driver.find_element_by_id('j_username')
            user_name.clear()
            user_name.send_keys(username)

            user_passwd = self._driver.find_element_by_id('j_password')
            user_passwd.clear()
            user_passwd.send_keys(password)


            login_btn = self._driver.find_element_by_id('login-btn')
            login_btn.submit()
        except selenium.common.exceptions.NoSuchElementException:
            print('INFO: No need to login')
            pass
        self._videos = []

    def download_all(self):
        videos = self._course.get_videos().videos
        filtered_videos = [video for video in videos if self._in_date_range(video.date)]
        total_videos = len(filtered_videos)

        downloaded_videos = []
        for i, video in reversed(list(enumerate(filtered_videos))):
            lecture_number = self._find_pos(videos, video)
            title = "Lecture {}".format(lecture_number+1)
            filename = self._get_filename(self._course.course_id, video.date, title)

            print(("Downloading {} of {}: {}".format(total_videos - i, total_videos, video.url)))
            print(("  to {}\n".format(filename)))
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
        print(video)
        print(filename)
        print(self._output_dir)

        from hls_downloader import Downloader
        echo360_downloader = Downloader(50)
        echo360_downloader.run(video, self._output_dir)

        # rename file
        os.rename(os.path.join(echo360_downloader.result_file_name), os.path.join(self._output_dir, filename))

    def _initialize(self, echo_course):
        self._driver.get(self._course.url)

    def _get_filename(self, course, date, title):
        return "{} - {} - {}.mp4".format(course, date, title)

    def _in_date_range(self, date_string):
        the_date = dateutil.parser.parse(date_string).date()
        return self._date_range[0] <= the_date and the_date <= self._date_range[1]

    def _find_pos(self, videos, the_video):
        for i, video in enumerate(videos):
            if video.date == the_video.date:
                return i

    def success_msg(self, course_name, videos):
        bar = '================================================================='
        msg = '\n{0}\n'.format(bar)
        msg += '    Course: {0} - {1}'.format(self._course.course_id, self._course.course_name)
        msg += '\n{0}\n'.format(bar)
        msg += '    Successfully downloaded:\n'
        for i in videos:
            msg += '        {}\n'.format(i)
        msg += '{0}\n'.format(bar)
        return msg
