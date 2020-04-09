import dateutil.parser
import operator
import sys
import selenium
import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

_LOGGER = logging.getLogger(__name__)


def update_course_retrieval_progress(current, total):
    prefix = '>> Retrieving echo360 Course Info... '
    status = "{}/{} videos".format(current, total)
    text = "\r{0} {1} ".format(prefix, status)
    sys.stdout.write(text)
    sys.stdout.flush()


class EchoVideos(object):
    def __init__(self, videos_json, driver):
        assert (videos_json is not None)
        self._driver = driver
        self._videos = []
        total_videos_num = len(videos_json)
        update_course_retrieval_progress(0, total_videos_num)

        for i, video_json in enumerate(videos_json):
            video_date = EchoVideo.get_date(video_json)
            self._videos.append(EchoVideo(video_json, self._driver))
            update_course_retrieval_progress(i + 1, total_videos_num)

        self._videos.sort(key=operator.attrgetter("date"))

    @property
    def videos(self):
        return self._videos

    def _blow_up(self, str, e):
        print(str)
        print("Exception: {}".format(str(e)))
        sys.exit(1)


class EchoVideo(object):
    def __init__(self, video_json, driver):
        self._driver = driver

        try:
            video_url = "{0}".format(video_json["richMedia"])
            video_url = str(video_url)  # cast back to string

            self._driver.get(video_url)
            _LOGGER.debug("Dumping video page at %s: %s",
                          video_url,
                          self._driver.page_source)

            m3u8_url = self._loop_find_m3u8_url(video_url, waitsecond=30)
            self._url = m3u8_url

            date = dateutil.parser.parse(video_json["startTime"]).date()
            self._date = date.strftime("%Y-%m-%d")
            self._title = video_json['title']

        except KeyError as e:
            self._blow_up("Unable to parse video data from JSON (course_data)",
                          e)

    def _loop_find_m3u8_url(self, video_url, waitsecond=15, max_attempts=5):
        stale_attempt = 1
        refresh_attempt = 1
        while True:
            self._driver.get(video_url)
            try:
                # wait for maximum second before timeout
                WebDriverWait(self._driver, waitsecond).until(
                    EC.presence_of_element_located((By.ID, "content-player")))
                return self._driver.find_element_by_id(
                    'content-player').find_element_by_tag_name(
                        'video').get_attribute('src')
            except selenium.common.exceptions.TimeoutException:
                if refresh_attempt >= max_attempts:
                    print(
                        '\r\nERROR: Connection timeouted after {} second for {} attempts... \
                          Possibly internet problem?'.format(
                            waitsecond, max_attempts))
                    raise
                refresh_attempt += 1
            except StaleElementReferenceException:
                if stale_attempt >= max_attempts:
                    print(
                        '\r\nERROR: Elements are not stable to retrieve after {} attempts... \
                        Possibly internet problem?'.format(max_attempts))
                    raise
                stale_attempt += 1

    @property
    def date(self):
        return self._date

    @property
    def url(self):
        return self._url

    @property
    def title(self):
        return self._title.decode('utf-8').encode('utf-8')

    @staticmethod
    def get_date(video_json):
        try:
            return dateutil.parser.parse(video_json["startTime"]).date()
        except KeyError as e:
            self._blow_up("Unable to parse video date from JSON (video data)",
                          e)

    def _blow_up(self, str, e):
        print(str)
        print("Exception: {}".format(str(e)))
        sys.exit(1)
