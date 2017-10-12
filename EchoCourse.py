import json
import sys

from selenium import webdriver
from EchoVideos import EchoVideos


class EchoCourse(object):

    def __init__(self, uuid, titles):
        self._course_id = ""
        self._uuid = uuid
        self._titles = titles
        self._videos = None
        self._driver = None

        self._hostname = "https://view.streaming.sydney.edu.au:8443"
        self._url = "{}/ess/portal/section/{}".format(self._hostname, self._uuid)
        self._video_url = "{}/ess/client/api/sections/{}/section-data.json?pageSize=100".format(self._hostname, self._uuid)

    def get_videos(self):
        if self._driver is None:
            self._blow_up("webdriver not set yet!!!", "")
        if not self._videos:
            try:
                course_data_json = self._get_course_data()
                videos_json = course_data_json["section"]["presentations"]["pageContents"]
                self._videos = EchoVideos(videos_json, self._titles, self._driver)
            except KeyError as e:
                self._blow_up("Unable to parse course videos from JSON (course_data)", e)

        return self._videos

    @property
    def uuid(self):
        return self._uuid

    @property
    def hostname(self):
        return self._hostname

    @property
    def url(self):
        return self._url

    @property
    def video_url(self):
        return self._video_url

    @property
    def course_id(self):
        if self._course_id == "":
            try:
                # driver = webdriver.PhantomJS() #TODO Redo this. Maybe use a singleton factory to request the lecho360 driver?s
                self.driver.get(self._url) # Initialize to establish the 'anon' cookie that Echo360 sends.
                self.driver.get(self._video_url)
                course_data_json = self._get_course_data()

                self._course_id = course_data_json["section"]["course"]["identifier"]
            except KeyError as e:
                self._blow_up("Unable to parse course id (e.g. CS473) from JSON (course_data)", e)

        return self._course_id

    @property
    def driver(self):
        if self._driver is None:
            self._blow_up("webdriver not set yet!!!", "")
        return self._driver

    def _get_course_data(self):
            try:
                self.driver.get(self.video_url)
                # self.driver.get_screenshot_as_file('./2.png')
                # print(dir(self.driver))
                # print('ha')
                # print(self.driver.page_source)
                json_str = self.driver.find_element_by_tag_name("pre").text

                return json.loads(json_str)
            except ValueError as e:
                self._blow_up("Unable to retrieve JSON (course_data) from url", e)

    def set_driver(self, driver):
        self._driver = driver

    def _blow_up(self, msg, e):
        print(msg)
        print("Exception: {}".format(str(e)))
        sys.exit(1)
