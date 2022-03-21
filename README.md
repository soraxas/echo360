# Echo360 Videos Downloader

[![Package Application with Pyinstaller](https://github.com/soraxas/echo360/workflows/Package%20Application%20with%20Pyinstaller/badge.svg)](https://github.com/soraxas/echo360/actions/)
[![linux-downloads](https://img.shields.io/badge/Download%20Executable-Linux%20&%20Mac-blueviolet)](https://github.com/soraxas/echo360/releases/latest/download/echo360-linux)
[![windows-downloads](https://img.shields.io/badge/Download%20Executable-Windows-blue)](https://github.com/soraxas/echo360/releases/latest/download/echo360-windows.exe)


echo360 is a command-line Python tool that allows you to download lecture videos from any university's Echo360 system and echo360 Cloud platform. All that's required is the particular course's url. See the FAQ for tips on how to find it.

The way this script works _should_ support all university's echo360 system in theory, see FAQ for details.

See it in action:

<p align="center">
    <img width="700" height="auto" src="docs/images/demo.gif" alt="echo360 demo" />
</p>

**NEWS:** It now works with `echo360.org` platform as well. Special thanks to [*@cloudrac3r*](https://github.com/cloudrac3r) and *Emma* for their kind offering of providing sources and helped debugging it. Read [FAQ](#echo360-cloud) for details.

# Getting Started

### Automated Installation

**Linux / MacOS**

```shell
./run.sh COURSE_URL  # where COURSE_URL is your course url
```

**Windows**

```shell
run.bat COURSE_URL  # where COURSE_URL is your course url
```

The scripts will boostrap all installation and download all needed files on the fly.

**pip**

```shell
pip install echo360
echo360-downloader COURSE_URL  # where COURSE_URL is your course url
```

### Optional

-   ffmpeg (for transcoding ts file to mp4 file) See [here (windows)](https://www.easytechguides.com/install-ffmpeg/) or [here](https://github.com/adaptlearning/adapt_authoring/wiki/Installing-FFmpeg) for a brief instructions of installing it in different OS.

## Manual

The provided script automated every operations, and install all dependency in a local python virtual environment. You can also use the system-wise python installation by manual installation. Get started by first install all requirements:

```shell
pip install -r requirements.txt  # or with: python -m pip install -r requirements.txt
```

Then run with:

```shell
python echo360.py
```

### Operating System

-   Linux
-   OS X
-   Windows

# Usage

**NOTE THAT** all the below command you can substitute `python echo360.py` with `./run.sh` (or `run.bat` if you are in windows)

### Quick Start

```shell
>>> python echo360.py                       \
    https://view.streaming.sydney.edu.au:8443/ess/portal/section/2018_S1C_INFO1001_ND
```

### Script args
```
>>> usage: echo360.py [-h] [--output OUTPUT_PATH]
                  [--after-date AFTER_DATEYYYY-MM-DD)]
                  [--before-date BEFORE_DATE(YYYY-MM-DD] [--unikey UNIKEY]
                  [--password PASSWORD] [--setup-credentials]
                  [--download-phantomjs-binary] [--chrome] [--firefox]
                  [--echo360cloud] [--interactive] [--alternative_feeds]
                  [--debug] [--auto | --manual]
                  ECHO360_URL

Download lectures from portal.

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
  --after-date AFTER_DATE(YYYY-MM-DD)
                        Only download lectures newer than AFTER_DATE
                        (inclusive). Note: this may be combined with --before-
                        date.
  --before-date BEFORE_DATE(YYYY-MM-DD)
                        Only download lectures older than BEFORE_DATE
                        (inclusive). Note: this may be combined with --after-
                        date
  --unikey UNIKEY, -u UNIKEY
                        Your unikey for your University of Sydney elearning
                        account
  --password PASSWORD, -p PASSWORD
                        Your password for your University of Sydney elearning
                        account
  --setup-credentials   Open a chrome instance to expose an ability for user
                        to log into any website to obtain credentials needed
                        before proceeding. (implies using chrome-driver)
  --download-phantomjs-binary
                        Force the echo360.py script to download a local binary
                        file for phantomjs (will override system bin)
  --chrome              Use Chrome Driver instead of phantomjs webdriver. You
                        must have chromedriver installed in your PATH.
  --firefox             Use Firefox Driver instead of phantomjs webdriver. You
                        must have geckodriver installed in your PATH.
  --interactive, -i     Interactively pick the lectures you want, instead of
                        download all (default) or based on dates .
  --alternative_feeds, -a
                        Download first two video feeds. Since some university
                        have multiple video feeds, with this option on the
                        downloader will also try to download the second
                        video, which could be the alternative feed. Might
                        only work on some 'echo360.org' hosts.
  --debug               Enable extensive logging.
  --auto                Only effective for 'echo360.org' host. When set, this
                        script will attempts to automatically redirects after
                        you had logged into your institution's SSO.
  --manual, -m          [Deprecated] Only effective for 'echo360.org' host.
                        When set, the script requires user to manually
                        continue the script within the terminal. This is the
                        default behaviour and exists only for backward
                        compatibility reason.
```
# Examples

```shell
>>> python echo360.py                  \
    "041698d6-f43a-4b09-a39a-b90475a63530" \  # Note this default to USYD's echo360
    --output "~/Lectures"                     # Use full URL for other University
```

### Download all available lectures

```shell
>>> python echo360.py                  \
    "041698d6-f43a-4b09-a39a-b90475a63530" \
    --output "~/Lectures"
```

### Download all lectures on or before a date

```shell
>>> python echo360.py                  \
    "041698d6-f43a-4b09-a39a-b90475a63530" \
    --output "~/Lectures"                  \
    --before-date "2014-10-14"
```

### Download all lectures on or after a date

```shell
>>> python echo360.py                  \
    "041698d6-f43a-4b09-a39a-b90475a63530" \
    --output "~/Lectures"                  \
    --after-date "2014-10-14"
```

### Download all lectures in a given date range (inclusive)

```shell
>>> python echo360.py                  \
    "041698d6-f43a-4b09-a39a-b90475a63530" \
    --output "~/Lectures"                  \
    --after-date "2014-08-26"              \
    --before-date "2014-10-14"
```

### Use chrome driver (instead of phantomjs)

Note: sometime it works better than phantomjs in some system

```shell
>>> python echo360.py                  \
    "041698d6-f43a-4b09-a39a-b90475a63530" \
    --chrome
```

# FAQ

### Is my university supported?

This is first built for the echo system in the University of Sydney, and then validated in several other universities' echo system. In theory, as long as the url are in the format of:

```shell
https://$(hostname)/ess/portal/section/$(UUID)
```
or
```shell
https://echo360.org[.xx]/
```
or with a dot net variant
```shell
https://echo360.net[.xx]/
```

... then it should be supported.

The variables `$(hostname)` and `$(UUID)` are what differentiate different University's echo360 system. If there is no credentials needed (ie no need to login before accessing the page), then 90% of the time it should works. If login is needed, some extra work might need to be put in before it works for your university. If that is the case, create an issue to let me know.

As for `echo360.org`, see [this](#echo360-cloud).

### How do I retrieve the Course URL for a course?

You should go to the main Echo360 Lecture page, which usually composed of all the lecturer recordings in a list format as shown below. It's the main page that lists all the recorded lectures and gives you the option to stream them or download them individually. This is important for downloading all the available videos from within the course.

<img height="auto" src="docs/images/course_page.png" alt="echo360 course main page" />

You can usually find this link on your course's main webpage. If your course webpage only links directly to videos, then you should be able to navigate back **by clicking the title of your course name (top of page)**.

The URL for the University of Sydney - 2017 semester 2 of CIVL4903 looks like

    https://view.streaming.sydney.edu.au:8443/ess/portal/section/041698d6-f43a-4b09-a39a-b90475a63530

which you can verify is correct in the above screenshot. **This should be the full URL you enter into the script, for all other universities' echo system.**

The UUID (Unified Unique IDentifier) is the last element of the URL. So in the above example it's,

    041698d6-f43a-4b09-a39a-b90475a63530

### echo360 cloud

Echo360 cloud refers to websites in the format of `https://echo360.org[.xx]`. This module now officially support this platform.

<p align="center">
<img height="auto" width="700" src="docs/images/echo360cloud_home.png" alt="echo360 cloud course main page" />
</p>

This method requires you to setup SSO credentials, therefore, it needs to open up a browser for you to setup your own university's SSO credentials.

To download videos, run:
```shell
./run.sh https://echo360.<org|net>[.xx]/section/$(UUID)/home
```
where `[.xx]` is an optional country flag specific to your echo360 platform and `$(UUID)` is the unique identifier for your course. This should the url that you can retrieve from your course's *main page* like the following.

<img height="auto" src="docs/images/echo360cloud_course-page.png" alt="echo360 cloud course main page" />

Note that this implies `setup-credential` option and will use chrome-webdriver by default. If you don't have chrome or prefer to use firefox, run it with the ` --firefox` flag like so:
```shell
./run.sh https://echo360.<org|net>[.xx]/section/$(UUID)/home --firefox
```

After running the command, it will opens up a browser instance, most likely with a login page. You should then login with your student's credentials like what you would normally do. After you have successfully logged in, the module should automatically redirects you and continues. If the script hangs (e.g. failed to recognises that you have logged in), feel free to let me know.


### I'm not sure of how to run it?

First, you'd need to install [Python](https://www.python.org/downloads/) in your system. Then, you can follow the youtube tutorial videos to get an idea of how to use the module.

- For [Windows users](https://www.youtube.com/watch?v=Lv1wtjnCcwI) (and showcased how to retrieve actual echo360 course url)
[![](docs/images/youtube_win_tutorial.jpg)](https://www.youtube.com/watch?v=Lv1wtjnCcwI)

### My credentials does not work?

You can setup any credentials need with manually logging into websites, by running the script with:
```sh
./run.sh ECHO360_URL --setup-credential
```
This will open up a chrome instance that allows you to log into your website as you normally do. Afterwards, simply type 'continue' into your shell and press enter to continue to proceeds with the rest of the script.

### My credentials does not work (echo360.org)?

For echo360.org, the default behaviour is it will always require you to setup-credentials, and the module will automatically detect login token and proceed the download process. For some institutions, this seems to be not sufficient (#29).

You can disable such behaviour with
```sh
./run.sh ECHO360_ORG_URL --manual
```
for manual setup; and once you had logged in, type
```sh
continue
```
in your terminal to continue.

### How do I download only individual video(s)?

You are in luck! It is now possible to pick a subset of videos to download from (instead of needing to download everything like before). Just pass the interactive argument like this:
```sh
./run.sh ECHO360_URL --interactive  # or ./run.sh ECHO360_URL -i
```
...and it shall presents an interactive screen for you to pick each individual video(s) that you want to download, like the screenshot as shown below.

<img src="/docs/images/pick_individual_videos_screenshot.png" width="650" height="auto" >

### My lecture has two video feeds, how can I download both of them?

You can add argument `--alternative_feeds` or simply `-a` to download both video feeds.

### Technical details

The current script uses a web-driver to emulate as a web-browser in order to retrieve the original streaming link. There are current two options for the web-driver: PhantomJS and Chrome. It then uses a hls downloader to simultaneously download all the smaller parts of the videos, and combined into one. Transcoding into mp4 will be performed if ffmpeg is present in your system, and all files will be renamed into a nice format.

# Credits

Credits to [jhalstead85](https://github.com/jhalstead85/lecho360) for which this script is based upon.
This script has then been adopted to be usable for USYD echo360. It was then extended to work in canvas (which uses a human-readable name instead of UUID); and later automated the entire process and become usable for all other universities.
