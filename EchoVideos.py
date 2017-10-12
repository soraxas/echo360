import dateutil.parser
import datetime
import operator
import sys

class EchoVideos(object):

    def __init__(self, videos_json, titles, driver):
        assert(videos_json is not None)

        self._driver = driver
        self._videos = []
        for video_json in videos_json:
            video_date = EchoVideo.get_date(video_json)
            video_title = self._get_title(titles, video_date)
            self._videos.append(EchoVideo(video_json, video_title, self._driver))

        self._videos.sort(key=operator.attrgetter("date"))

    @property
    def videos(self):
        return self._videos

    def _get_title(self, titles, date):
        if titles is None:
            return ""
        try:
            for title in titles:
                title_date = dateutil.parser.parse(title["date"]).date()
                if date == title_date:
                    return title["title"].encode("ascii")
            return ""

        except KeyError as e:
            blow_up("Unable to parse either titles or course_data JSON", e)

    def _blow_up(self, str, e):
        print(str)
        print("Exception: {}".format(str(e)))
        sys.exit(1)



class EchoVideo(object):

    def __init__(self, video_json, title, driver):
        self._title = title
        self._driver = driver

        try:
            video_url = "{0}".format(video_json["richMedia"])
            video_url = str(video_url) # cast back to string
            # a = 'https://view.streaming.sydney.edu.au:8443/ess/echo/presentation/1a700a60-d42f-4e24-bd5d-d23d2d8dd134'
            # print(video_url)
            # print(a)
            self._driver.get(video_url)
            # self._driver.get_screenshot_as_file('./211.png')
            # self._driver.get(a)
            # self._driver.get_screenshot_as_file('./212.png')
            # import time
            # time.sleep(1)
            # # self._driver.get_screenshot_as_file('./211.png')
            # self._driver.get('http://getright.com/useragent.html')
            # self._driver.get_screenshot_as_file('./2.png')
            m3u8_url = self._driver.find_element_by_id('content-player').find_element_by_tag_name('video').get_attribute('src')

            self._url = m3u8_url

            date = dateutil.parser.parse(video_json["startTime"]).date()
            self._date = date.strftime("%Y-%m-%d")
        except KeyError as e:
            self._blow_up("Unable to parse video data from JSON (course_data)", e)

    @property
    def title(self):
        return self._title

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
