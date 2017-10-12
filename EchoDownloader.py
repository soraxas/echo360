import dateutil.parser
import os
import sys
import urllib.request, urllib.error, urllib.parse

from selenium import webdriver


class EchoDownloader(object):

    def __init__(self, course, output_dir, date_range, username, password):
        self._course = course
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


        # Input username and password:
        user_name = self._driver.find_element_by_id('j_username')
        user_name.clear()
        user_name.send_keys(username)

        user_passwd = self._driver.find_element_by_id('j_password')
        user_passwd.clear()
        user_passwd.send_keys(password)


        login_btn = self._driver.find_element_by_id('login-btn')
        login_btn.submit()

        self._videos = []

    def download_all(self):
        videos = self._course.get_videos().videos
        filtered_videos = [video for video in videos if self._in_date_range(video.date)]
        total_videos = len(filtered_videos)

        # Download the newest video first but maintain it's original index
        # in case a JSON file isn't passed (and we need to label them as
        # Lecture 1, 2, ...)
        for i, video in reversed(list(enumerate(filtered_videos))):
            # TODO Check if the lecture number is included in the JSON object.
            lecture_number = self._find_pos(videos, video)
            title = video.title if (video.title != "") else "Lecture {}".format(lecture_number+1)
            filename = self._get_filename(self._course.course_id, video.date, title)

            print(("Downloading {} of {}: {}".format(total_videos - i, total_videos, video.url)))
            print(("  to {}\n".format(filename)))
            self._download_as(video.url, filename)

    @property
    def useragent(self):
        return self._useragent

    @useragent.setter
    def useragent(self, useragent):
        self._useragent = useragent

    def _download_as(self, video, filename):
        print(video)
        print(filename)
        exit()
        try:
            request = urllib.request.Request(video)
            request.add_header('User-Agent', self._useragent)
            opener = urllib.request.build_opener()

            with open(os.path.join(self._output_dir, filename), "wb") as local_file:
                local_file.write(opener.open(request).read())

        except urllib.error.HTTPError as e:
            print(("HTTP Error:", e.code, video))
        except urllib.error.URLError as e:
            print(("URL Error:", e.reason, video))

    def _initialize(self, echo_course):
        self._driver.get(self._course.url)

    def _get_filename(self, course, date, title):
        return "{} - {} - {}.m4v".format(course, date, title)

    def _in_date_range(self, date_string):
        the_date = dateutil.parser.parse(date_string).date()
        return self._date_range[0] <= the_date and the_date <= self._date_range[1]


    def _find_pos(self, videos, the_video):
        for i, video in enumerate(videos):
            if video.date == the_video.date:
                return i

        return -1
