import re


class NaiveM3U8Parser:
    """
    Sometimes ago (when I was first developing this) the format of m3u8 looks something like:
    ```
    #EXTM3U
    #EXT-X-VERSION:7
    #EXT-X-INDEPENDENT-SEGMENTS

    #EXT-X-STREAM-INF:BANDWIDTH=52232,RESOLUTION=640x378,FRAME-RATE=25.0,CODECS="avc1.640029,mp4a.40.2",AUDIO="group_audio"
    s1q0.m3u8
    #EXT-X-STREAM-INF:BANDWIDTH=102092,RESOLUTION=1280x756,FRAME-RATE=25.0,CODECS="avc1.640029,mp4a.40.2",AUDIO="group_audio"
    s1q1.m3u8
    #EXT-X-STREAM-INF:BANDWIDTH=71074,CODECS="mp4a.40.2",AUDIO="group_audio"
    s0q0.m3u8

    #EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID="group_audio",NAME="audio_0",DEFAULT=YES,URI="s0q0.m3u8"
    ```
    i.e., it is obvious that each audio/video stream will occupy one line without hash #.

    However, there had been reports that the m3u8 now looks like:
    ```
    #EXTM3U
    #EXT-X-VERSION:7
    #EXT-X-INDEPENDENT-SEGMENTS

    #EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID="q0",NAME="Default",DEFAULT=YES,AUTOSELECT=YES,URI="s0q0.m3u8"
    #EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID="q1",NAME="Default",DEFAULT=YES,AUTOSELECT=YES,URI="s0q1.m3u8"

    #EXT-X-STREAM-INF:BANDWIDTH=55528,RESOLUTION=640x360,PROGRAM-ID=1,AUDIO="q0",CODECS="avc1.640029,mp4a.40.2",FRAME-RATE=25.0
    s1q0.m3u8
    #EXT-X-STREAM-INF:BANDWIDTH=220997,RESOLUTION=1920x1080,PROGRAM-ID=1,AUDIO="q1",CODECS="avc1.640029,mp4a.40.2",FRAME-RATE=25.0
    s1q1.m3u8
    ```
    where an audio stream can be embeded into hash # line.

    we will account for that.
    """

    VIDEO_TOKENS = [
        "RESOLUTION=",
    ]
    AUDIO_TOKENS = [
        "AUDIO=",
        "TYPE=AUDIO",
    ]

    def __init__(self, line_list):
        self.line_list = line_list
        self.videos = []
        self.audios = []

    def get_video_and_audio(self):
        video_uri = None
        audio_uri = None
        # priortise the last video. Note that we won't care about safety, as the outter class
        # should catch any exception.
        video = self.videos[-1]
        video_uri = video["URI"]
        if "audio_name" in video.keys():
            # search for corresponding audio file
            for audio in self.audios:
                if audio["name"] == video["audio_name"]:
                    audio_uri = NaiveM3U8Parser._remove_quotes(audio["URI"])
                    break
        return video_uri, audio_uri

    def parse(self):
        lines = self.line_list
        for i in range(len(lines)):
            if lines[i].strip() == "":
                continue
            if lines[i].startswith("#"):
                if any(t in lines[i] for t in NaiveM3U8Parser.VIDEO_TOKENS):
                    # is a video stream
                    self.videos.append(self._extract_properties(lines, i))
                elif any(t in lines[i] for t in NaiveM3U8Parser.AUDIO_TOKENS):
                    # is a video stream
                    self.audios.append(self._extract_properties(lines, i))

    @staticmethod
    def _extract_properties(lines, idx):
        assert lines[idx].startswith("#")
        tokens = NaiveM3U8Parser._tokenise(NaiveM3U8Parser._remove_prefix(lines[idx]))
        properties = {}
        properties["type"] = "video" if "RESOLUTION" in tokens.keys() else "audio"
        if "URI" in tokens.keys():
            # this is an inlined uri format.
            properties["URI"] = tokens["URI"]
        else:
            # Look at next line to obtain URI
            properties["URI"] = lines[idx + 1].strip()
        if properties["type"] == "video":
            # is a video
            try:
                properties["audio_name"] = tokens["AUDIO"]
            except KeyError:
                pass
        elif properties["type"] == "audio":
            # is an audio
            try:
                # old style has AUDIO=audio_name
                properties["name"] = tokens["AUDIO"]
            except KeyError:
                pass
            try:
                # new style has GROUP-ID=audio_name
                properties["name"] = tokens["GROUP-ID"]
            except KeyError:
                pass
        return properties

    @staticmethod
    def _split_on_comma_unless_inside_quotes(string):
        return re.split(r",(?=(?:[^\"']*[\"'][^\"']*[\"'])*[^\"']*$)", string)

    @staticmethod
    def _tokenise(string):
        # split a string of "a=1,b=2,c='str'" into tokenised pair of string
        items = [
            item.split("=")
            for item in NaiveM3U8Parser._split_on_comma_unless_inside_quotes(string)
        ]
        return {it[0]: it[1] for it in items}

    @staticmethod
    def _remove_prefix(string):
        return re.search("(?:[#a-zA-Z-]+:)(.*)$", string).group(1)

    @staticmethod
    def _remove_quotes(string):
        if len(string) >= 2:
            if string[0] == '"' and string[-1] == '"':
                return string[1:-1]
        return string
