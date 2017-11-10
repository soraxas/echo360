import dateutil.parser
import datetime
import operator
import sys
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class EchoVideos(object):

    def __init__(self, videos_json, driver):
        assert(videos_json is not None)
        self._driver = driver
        self._videos = []
        for video_json in videos_json:
            video_date = EchoVideo.get_date(video_json)
            self._videos.append(EchoVideo(video_json, self._driver))

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
            video_url = str(video_url) # cast back to string

            self._driver.get(video_url)

            # wait for maximum 30 second before timeout
            waitsecond = 30
            try:
                WebDriverWait(self._driver, waitsecond).until(
                EC.presence_of_element_located((By.ID, "content-player"))
                )
            except selenium.common.exceptions.TimeoutException:
                print('ERROR: Connection timeouted after {} second... Possibly internet problem?'.format(waitsecond))
                exit(1)
            #
            # finally:
            #     self._driver.quit()

            m3u8_url = self._driver.find_element_by_id('content-player').find_element_by_tag_name('video').get_attribute('src')

            self._url = m3u8_url

            date = dateutil.parser.parse(video_json["startTime"]).date()
            self._date = date.strftime("%Y-%m-%d")
        except KeyError as e:
            self._blow_up("Unable to parse video data from JSON (course_data)", e)

    @property
    def date(self):
        return self._date

    @property
    def url(self):
        return self._url

    @staticmethod
    def get_date(video_json):
        try:
            return dateutil.parser.parse(video_json["startTime"]).date()
        except KeyError as e:
            self._blow_up("Unable to parse video date from JSON (video data)", e)

    def _blow_up(self, str, e):
        print(str)
        print("Exception: {}".format(str(e)))
        sys.exit(1)
