import json
import re
import sys

import selenium
import logging
from selenium.webdriver.common.by import By

from .videos import EchoVideos, EchoCloudVideos

_LOGGER = logging.getLogger(__name__)


class EchoCourse(object):
    def __init__(self, uuid, hostname=None, alternative_feeds=False):
        self._course_id = None
        self._course_name = None
        self._uuid = uuid
        self._videos = None
        self._driver = None
        self._alternative_feeds = alternative_feeds
        if hostname is None:
            self._hostname = "https://view.streaming.sydney.edu.au:8443"
        else:
            self._hostname = hostname

    def get_videos(self):
        if self._driver is None:
            self._blow_up("webdriver not set yet!!!", "")
        if not self._videos:
            try:
                course_data_json = self._get_course_data()
                videos_json = course_data_json["section"]["presentations"][
                    "pageContents"
                ]
                self._videos = EchoVideos(videos_json, self._driver)
            except KeyError as e:
                self._blow_up(
                    "Unable to parse course videos from JSON (course_data)", e
                )
            except selenium.common.exceptions.NoSuchElementException as e:
                self._blow_up("selenium cannot find given elements", e)

        return self._videos

    @property
    def uuid(self):
        return self._uuid

    @property
    def hostname(self):
        return self._hostname

    @property
    def url(self):
        return "{}/ess/portal/section/{}".format(self._hostname, self._uuid)

    @property
    def video_url(self):
        return "{}/ess/client/api/sections/{}/section-data.json?pageSize=100".format(
            self._hostname, self._uuid
        )

    @property
    def course_id(self):
        if self._course_id is None:
            try:
                # driver = webdriver.PhantomJS() #TODO Redo this. Maybe use a singleton factory to request the lecho360 driver?s
                self.driver.get(
                    self.url
                )  # Initialize to establish the 'anon' cookie that Echo360 sends.
                self.driver.get(self.video_url)
                course_data_json = self._get_course_data()

                self._course_id = course_data_json["section"]["course"]["identifier"]
                self._course_name = course_data_json["section"]["course"]["name"]
            except KeyError as e:
                self._blow_up(
                    "Unable to parse course id (e.g. CS473) from JSON (course_data)", e
                )

        if type(self._course_id) != str:
            # it's type unicode for python2
            return self._course_id.encode("utf-8")
        return self._course_id

    @property
    def course_name(self):
        if self._course_name is None:
            # trigger getting course_id to get course name as well
            self.course_id
        if type(self._course_name) != str:
            # it's type unicode for python2
            return self._course_name.encode("utf-8")
        return self._course_name

    @property
    def driver(self):
        if self._driver is None:
            self._blow_up("webdriver not set yet!!!", "")
        return self._driver

    @property
    def nice_name(self):
        return "{0} - {1}".format(self.course_id, self.course_name)

    def _get_course_data(self):
        try:
            self.driver.get(self.video_url)
            _LOGGER.debug(
                "Dumping course page at %s: %s",
                self.video_url,
                self._driver.page_source,
            )
            json_str = self.driver.find_element(By.TAG_NAME, "pre").text
        except ValueError as e:
            raise Exception("Unable to retrieve JSON (course_data) from url", e)
        self.course_data = json.loads(json_str)
        return self.course_data

    def set_driver(self, driver):
        self._driver = driver

    def _blow_up(self, msg, e):
        print(msg)
        print("Exception: {}".format(str(e)))
        sys.exit(1)


class EchoCloudCourse(EchoCourse):
    def __init__(self, *args, **kwargs):
        super(EchoCloudCourse, self).__init__(*args, **kwargs)

    def get_videos(self):
        if self._driver is None:
            raise Exception("webdriver not set yet!!!", "")
        if not self._videos:
            try:
                course_data_json = self._get_course_data()
                videos_json = course_data_json["data"]
                self._videos = EchoCloudVideos(
                    videos_json, self._driver, self.hostname, self._alternative_feeds
                )
            # except KeyError as e:
            #     print("Unable to parse course videos from JSON (course_data)")
            #     raise e
            except selenium.common.exceptions.NoSuchElementException as e:
                print("selenium cannot find given elements")
                raise e

        return self._videos

    @property
    def video_url(self):
        return "{}/section/{}/syllabus".format(self._hostname, self._uuid)

    @property
    def _section_home_url(self):
        return "{}/section/{}/home".format(self._hostname, self._uuid)

    @property
    def course_id(self):
        if self._course_id is None:
            # self.course_data['data'][0]['lesson']['lesson']['displayName']
            # should be in the format of XXXXX (ABCD1001 - 2020 - Semester 1) ???
            # canidate = self.course_data['data'][0]['lesson']['video']['published']['courseName']
            # print(self._course_name)
            # self._course_name = canidate
            # Too much variant, it's too hard to have a unique way to extract course id.
            # we will simply use course name and ignore any course id.
            self._course_id = ""
            # result = re.search('^[^(]+', canidate)
            # if result is not None:
            #     self._course_name = result.group()
            #     result = re.search('[(].+[)]', canidate)
            #     self._course_id = result.group()[1:-1]
        return self._course_id

    @property
    def course_name(self):
        if self._course_name is None:
            # trigger getting course data (via whichever method actually
            # worked) so we can look for a course name in it.
            course_data = getattr(self, "course_data", None) or self._get_course_data()
            # try each available video as some video might be special has contains
            # no information about the course.
            for v in course_data.get("data", []):
                try:
                    self._course_name = v["lesson"]["video"]["published"]["courseName"]
                    break
                except KeyError:
                    pass
            # if the JSON API wasn't available, _get_course_data() will
            # already have set self._course_name as a side effect while
            # scraping the section page's heading; nothing more to do here.
            if self._course_name is None:
                # no available course name found...?
                self._course_name = "[[UNTITLED]]"
        return self._course_name

    @property
    def nice_name(self):
        return self.course_name

    _LESSON_ROW_RE = re.compile(
        r'<div class="class-row([^"]*)"\s+data-test-lessonid="([^"]+)"'
    )
    _LESSON_START_TIME_RE = re.compile(
        r"_(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?)_\d{4}-\d{2}-\d{2}T"
    )
    _HEADING_RE = re.compile(r"<h1\b[^>]*>\s*(.*?)\s*</h1>", re.DOTALL)

    def _get_course_data(self):
        # Some echo360 cloud/self-hosted instances still serve real JSON
        # from /section/{id}/syllabus when asked for it. Try that first so
        # this keeps working wherever it already does.
        try:
            course_data = self._fetch_course_data_via_json_api()
            if isinstance(course_data, dict) and isinstance(course_data.get("data"), list):
                self.course_data = course_data
                return self.course_data
            _LOGGER.debug(
                "JSON syllabus endpoint returned no lessons; falling back to "
                "scraping the section home page"
            )
        except (selenium.common.exceptions.WebDriverException, ValueError) as e:
            _LOGGER.debug(
                "JSON syllabus endpoint unavailable (%s); falling back to "
                "scraping the section home page",
                e,
            )
        try:
            return self._scrape_course_data_from_section_page()
        except selenium.common.exceptions.TimeoutException as e:
            raise Exception(
                "Error: Failed to get lesson info for EchoCloudCourse!"
            ) from e

    def _fetch_course_data_via_json_api(self):
        self.driver.get(self.video_url)
        _LOGGER.debug(
            "Dumping course page at %s: %s",
            self.video_url,
            self._driver.page_source,
        )
        # A plain browser navigation to this URL may get the React app shell
        # (HTML) back on newer echo360 instances instead of JSON, so ask for
        # JSON explicitly via an authenticated in-page fetch() - the same
        # thing the React app itself would do internally when this endpoint
        # is the one actually backing it.
        fetch_script = """
            var callback = arguments[arguments.length - 1];
            fetch(arguments[0], {headers: {'Accept': 'application/json'}, credentials: 'same-origin'})
              .then(function(r) { return r.text().then(function(t){ return {status: r.status, body: t}; }); })
              .then(function(result) { callback(result); })
              .catch(function(e) { callback({status: -1, body: 'FETCH_ERROR: ' + String(e)}); });
        """
        result = self.driver.execute_async_script(fetch_script, self.video_url)
        if result["status"] != 200:
            raise Exception(
                "JSON syllabus endpoint returned status {}: {}".format(
                    result["status"], result["body"][:200]
                )
            )
        return json.loads(result["body"])

    def _scrape_course_data_from_section_page(self):
        # Newer echo360 cloud UIs (e.g. echo360.org.uk as of mid-2026) always
        # serve the React app shell at /section/{id}/syllabus - even an
        # authenticated in-page fetch() with Accept: application/json gets a
        # NetworkError, not JSON. There doesn't seem to be an underlying API
        # worth chasing there anymore, so scrape the rendered section home
        # page instead: each lesson is a <div class="class-row"
        # data-test-lessonid="..."> row, and the lesson id itself embeds the
        # lesson's start/end time (e.g.
        # "..._2026-07-13T10:00:00.000_2026-07-13T13:00:00.000"), so no
        # separate date field needs to be parsed out of the row's markup.
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        self.driver.get(self._section_home_url)
        # the lesson list is rendered client-side by React, so it isn't
        # present in the page source immediately after navigation.
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.class-row"))
        )
        page = self._driver.page_source
        _LOGGER.debug("Dumping section page at %s: %s", self._section_home_url, page)

        if self._course_name is None:
            heading_match = self._HEADING_RE.search(page)
            if heading_match:
                course_name = re.sub("<[^>]+>", " ", heading_match.group(1))
                self._course_name = re.sub(r"\s+", " ", course_name).strip()

        lessons = []
        for class_suffix, lesson_id in self._LESSON_ROW_RE.findall(page):
            tokens = set(token for token in re.split(r'[\s\-]+', class_suffix) if token)
            if tokens & {'live', 'future'}:
                # not recorded/available yet, nothing to download
                continue
            start_time_match = self._LESSON_START_TIME_RE.search(lesson_id)
            start_time = start_time_match.group(1) if start_time_match else None
            lessons.append(
                {
                    "lesson": {
                        "hasVideo": True,
                        "hasAvailableVideo": True,
                        "startTimeUTC": start_time,
                        "lesson": {
                            "id": lesson_id,
                            "name": start_time or lesson_id,
                            "createdAt": start_time,
                        },
                    }
                }
            )

        self.course_data = {"data": lessons}
        return self.course_data
