import os
import re

import dateutil.parser
import operator
import sys

import ffmpy
import requests
import selenium
import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

from echo360.hls_downloader import Downloader

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

            self._date = self.get_date(video_json["startTime"])
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
        if type(self._title) != str:
            # it's type unicode for python2
            return self._title.encode('utf-8')
        return self._title

    def get_date(self, video_json):
        try:
            # date is not important so we will just ignore it if something went wrong
            date = dateutil.parser.parse(self._extract_date(video_json)).date()
            return date.strftime("%Y-%m-%d")
        except Exception:
            return "0000-00-00"
    
    def _extract_date(self, video_json):
        return video_json["startTime"]

    def _blow_up(self, str, e):
        print(str)
        print("Exception: {}".format(str(e)))
        sys.exit(1)

    def download(self, output_dir, filename, pool_size=50):
        print('')
        print('-' * 60)
        print('Downloading "{}"'.format(filename))
        self._download_url_to_dir(self.url, output_dir, filename, pool_size)
        print('-' * 60)

    def _download_url_to_dir(self, url, output_dir, filename, pool_size,
                             convert_to_mp4=True):
        echo360_downloader = Downloader(pool_size,
                                        selenium_cookies=self._driver.get_cookies())
        echo360_downloader.run(url, output_dir, convert_to_mp4=convert_to_mp4)

        # rename file
        ext = echo360_downloader.result_file_name.split('.')[-1]
        result_full_path = os.path.join(output_dir, '{0}.{1}'.format(filename, ext))
        os.rename(
            os.path.join(echo360_downloader.result_file_name),
            result_full_path)
        return result_full_path


class EchoCloudVideos(EchoVideos):
    def __init__(self, videos_json, driver, hostname):
        assert (videos_json is not None)
        self._driver = driver
        self._videos = []
        total_videos_num = len(videos_json)
        update_course_retrieval_progress(0, total_videos_num)

        for i, video_json in enumerate(videos_json):
            self._videos.append(EchoCloudVideo(video_json, self._driver, hostname))
            update_course_retrieval_progress(i + 1, total_videos_num)

        self._videos.sort(key=operator.attrgetter("date"))

    @property
    def videos(self):
        return self._videos


class EchoCloudVideo(EchoVideo):

    @property
    def video_url(self):
        return "{}/lesson/{}/classroom".format(self.hostname, self.video_id)

    def __init__(self, video_json, driver, hostname):
        self.hostname = hostname
        self._driver = driver

        try:
            video_id = "{0}".format(video_json["lesson"]["lesson"]["id"])
            self.video_id = str(video_id)  # cast back to string

            self._driver.get(self.video_url)
            _LOGGER.debug("Dumping video page at %s: %s",
                          self.video_url,
                          self._driver.page_source)

            m3u8_url = self._loop_find_m3u8_url(self.video_url, waitsecond=30)
            self._url = m3u8_url

            self._date = self.get_date(video_json)
            self._title = video_json['lesson']['lesson']['name']

        except KeyError as e:
            raise KeyError("Unable to parse video data from JSON (course_data)", e)

    def download(self, output_dir, filename, pool_size=50):
        print('')
        print('-' * 60)
        print('Downloading "{}"'.format(filename))

        session = requests.Session()
            # load cookies
        for cookie in self._driver.get_cookies():
            session.cookies.set(cookie["name"], cookie["value"])

        r = session.get(self.url)
        if not r.ok:
            print("Error: Failed to get m3u8 info. Skipping this video")
            return

        lines = [n for n in r.content.decode().split('\n')]
        m3u8_video = None
        m3u8_audio = None
        for i in range(1, len(lines)):
            if lines[i].strip() == "":
                continue
            if not lines[i].startswith('#'):
                # check what content is this for by previous' line
                # ALL THESE CHECKS ARE HAND-CRAFTED AND MIGHT BREAKS EASILY
                if "RESOLUTION" in lines[i-1]:
                    # there probably will be multiple video stream but the last one is
                    # most likely the highest quality :) ..... assumption assumption
                    m3u8_video = lines[i]
                else:
                    m3u8_audio = lines[i]
        if m3u8_video is None or m3u8_audio is None:
            print("ERROR: Failed to find audio/video m3u8... skipping this one")
            return
        # NOW we can finally start downloading!
        from hls_downloader import urljoin

        print("  > Downloading audio:")
        audio_file = self._download_url_to_dir(urljoin(
            self.url, m3u8_audio), output_dir, filename + "_audio",
            pool_size, convert_to_mp4=False)
        print("  > Downloading video:")
        video_file = self._download_url_to_dir(urljoin(
            self.url, m3u8_video), output_dir, filename + "_video",
            pool_size, convert_to_mp4=False)
        sys.stdout.write('  > Converting to mp4... ')
        sys.stdout.flush()
        self.combine_audio_video(audio_file, video_file,
                                 os.path.join(output_dir, filename + ".mp4"))
        print('Done!')
        print('-' * 60)

    @staticmethod
    def combine_audio_video(audio_file, video_file, final_file):
        if os.path.exists(final_file):
            os.remove(final_file)
        ff = ffmpy.FFmpeg(
            global_options='-loglevel panic',
            inputs={video_file: None, audio_file: None},
            outputs={final_file: ['-c:v', 'copy', '-c:a', 'ac3']}
        )
        ff.run()


    def _loop_find_m3u8_url(self, video_url, waitsecond=15, max_attempts=5):
        stale_attempt = 1
        refresh_attempt = 1
        while True:
            self._driver.get(video_url)
            try:
                # find all m3u8 files
                # the replace is for reversing the escape by the escapped js in the page source
                m3u8urls = set(re.findall(
                    "https://[^,]*?m3u8",
                    self._driver.page_source.replace("\/", "/"))
                )
                # find one that has audio + video
                m3u8urls = [url for url in m3u8urls if url.endswith("av.m3u8")]
                if len(m3u8urls) == 0:
                    raise Exception(
                        "No audio+video m3u8 files found! Exiting...\n"
                        "This script is hard-coded to download audio+video. "
                        "If this is an intended behaviour, please contact the author.")
                # There could exists multiple m3u8 files
                # (e.g. .../s1_av.m3u8, .../s2_av.m3u8, etc.) Probably to refer to
                # different quality?? We will set it to always prefer higher number.
                # Since (from my experiment) the prefixes are always the same, we will
                # just use text sorting to get the higher number.
                m3u8urls = reversed(m3u8urls)
                return next(m3u8urls)

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

    def _extract_date(self, video_json):
        return video_json["lesson"]["startTimeUTC"]
