# Echo360 Videos Downloader #

echo360 is a command-line Python tool that allows you to download lecture videos from any university's Echo360 lecture portal. All that's required is the particular course's url. See the FAQ for tips on how to find it.

The way this script works _should_ support all university's echo360 system in theory, see FAQ for details.


# Getting Started #

### Automated Installation ###

**Linux / MacOS**
```shell
./run.sh COURSE_URL  # where COURSE_URL is your course url
```
**Windows**
```shell
run.bat COURSE_URL  # where COURSE_URL is your course url
```
The scripts will boostrap all installation and download all needed files on the fly.
### Optional ###
- ffmpeg (for transcoding ts file to mp4 file) See [here](https://github.com/adaptlearning/adapt_authoring/wiki/Installing-FFmpeg) for a brief instructions of installing it in different OS.

## Manual ##
The provided script automated every operations, and install all dependency in a local python virtual environment. You can also use the system-wise python installation by manual installation. Get started by first install all requirements:
```shell
pip install -r requirements.txt  # or with: python -m pip install -r requirements.txt
```
Then run with:
```shell
python echo360.py
```

### Operating System ###
- Linux
- OS X
- Windows



# Usage #
**NOTE THAT** all the below command you can substitute `python echo360.py` with `./run.sh` (or `run.bat` if you are in windows)

### Quick Start ###
```shell
>>> python echo360.py                       \
    https://view.streaming.sydney.edu.au:8443/ess/portal/section/2018_S1C_INFO1001_ND
```
### Script args ###
```
>>> usage: echo360.py [-h] [--output OUTPUT_PATH]
                  [--after-date AFTER_DATEYYYY-MM-DD)]
                  [--before-date BEFORE_DATE(YYYY-MM-DD] [--unikey UNIKEY]
                  [--password PASSWORD] [--download-phantomjs-binary]
                  [--chrome] [--debug]
                  ECHO360_URL

Download lectures from Echo360 portal.

positional arguments:
  ECHO360_URL           Full URL of the echo360 course page, or only the UUID
                        (which defaults to USYD). The URL of the course's
                        video lecture page, for example: http://recordings.eng
                        ineering.illinois.edu/ess/portal/section/115f3def-7371
                        -4e98-b72f-6efe53771b2a)

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT_PATH, -o OUTPUT_PATH
                        Path to the desired output directory. The output
                        directory must exist. Otherwise the current directory
                        is used.
  --after-date AFTER_DATE(YYYY-MM-DD), -a AFTER_DATE(YYYY-MM-DD)
                        Only download lectures newer than AFTER_DATE
                        (inclusive). Note: this may be combined with --before-
                        date.
  --before-date BEFORE_DATE(YYYY-MM-DD), -b BEFORE_DATE(YYYY-MM-DD)
                        Only download lectures older than BEFORE_DATE
                        (inclusive). Note: this may be combined with --after-
                        date
  --unikey UNIKEY, -u UNIKEY
                        Your unikey for your University of Sydney elearning
                        account
  --password PASSWORD, -p PASSWORD
                        Your password for your University of Sydney elearning
                        account
  --download-phantomjs-binary
                        Force the echo360.py script to download a local binary
                        file for phantomjs (will override system bin)
  --chrome              Use Chrome Driver instead of phantomjs webdriver. You
                        must have chromedriver installed in your PATH.
  --debug               Enable extensive logging.

```
# Examples #
```shell
>>> python echo360.py                  \
    "041698d6-f43a-4b09-a39a-b90475a63530" \  # Note this default to USYD's echo360
    --output "~/Lectures"                     # Use full URL for other University
```

### Download all available lectures ###
```shell
>>> python echo360.py                  \
    "041698d6-f43a-4b09-a39a-b90475a63530" \
    --output "~/Lectures"
```

### Download all lectures on or before a date ###
```shell
>>> python echo360.py                  \
    "041698d6-f43a-4b09-a39a-b90475a63530" \
    --output "~/Lectures"                  \
    --before-date "2014-10-14"
```

### Download all lectures on or after a date ###
```shell
>>> python echo360.py                  \
    "041698d6-f43a-4b09-a39a-b90475a63530" \
    --output "~/Lectures"                  \
    --after-date "2014-10-14"
```

### Download all lectures in a given date range (inclusive) ###
```shell
>>> python echo360.py                  \
    "041698d6-f43a-4b09-a39a-b90475a63530" \
    --output "~/Lectures"                  \
    --after-date "2014-08-26"              \
    --before-date "2014-10-14"
```

### Use chrome driver (instead of phantomjs) ###
Note: sometime it works better than phantomjs in some system
```shell
>>> python echo360.py                  \
    "041698d6-f43a-4b09-a39a-b90475a63530" \
    --chrome
```

# FAQ #

### Is my university supported? ###
This is first built for the echo system in the University of Sydney, and then validated in several other universities' echo system. In theory, as long as the url are in the format of:
```shell
https://$(hostname)/ess/portal/section/$(UUID)
```
... then it should be supported.

The variables `$(hostname)` and `$(UUID)` are what differentiate different University's echo360 system. If there is no credentials needed (ie no need to login before accessing the page), then 90% of the time it should works. If login is needed, some extra work might need to be put in before it works for your university. If that is the case, create an issue to let me know.

### How do I retrieve the Course URL for a course? ###
You should go to the main Echo360 Lecture page, which usually composed of all the lecturer recordings in a list format as shown below. It's the main page that lists all the recorded lectures and gives you the option to stream them or download them individually. This is important for downloading all the available videos from within the course.

![CIVL4093 Main Echo360 Lecture Page](https://i.imgur.com/jy8a99D.png)


You can usually find this link on your course's main webpage. If your course webpage only links directly to videos, then you should be able to navigate back **by clicking the title of your course name (top of page)**.

The URL for the University of Sydney - 2017 semester 2 of CIVL4903 looks like

```
https://view.streaming.sydney.edu.au:8443/ess/portal/section/041698d6-f43a-4b09-a39a-b90475a63530
```

which you can verify is correct in the above screenshot. **This should be the full URL you enter into the script, for all other universities' echo system.**

The UUID (Unified Unique IDentifier) is the last element of the URL. So in the above example it's,
```
041698d6-f43a-4b09-a39a-b90475a63530
```

### Technical details ###

The current script uses a web-driver to emulate as a web-browser in order to retrieve the original streaming link. There are current two options for the web-driver: PhantomJS and Chrome. It then uses a hls downloader to simultaneously download all the smaller parts of the videos, and combined into one. Transcoding into mp4 will be performed if ffmpeg is present in your system, and all files will be renamed into a nice format.

# Credits #
Credits to [jhalstead85](https://github.com/jhalstead85/lecho360) for which this script is based upon.
This script has then been adopted to be usable for USYD echo360. It was then extended to work in canvas (which uses a human-readable name instead of UUID); and later automated the entire process and become usable for all other universities.
