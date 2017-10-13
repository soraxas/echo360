# USYDecho360 #

### Contents ###
1. [Main](https://github.com/soraxas/usydecho360/blob/master/Readme.md#usydecho360)
2. [Requirements](https://github.com/soraxas/usydecho360/blob/master/Readme.md#requirements)
3. [Usage](https://github.com/soraxas/usydecho360/blob/master/Readme.md#usage)
4. [Examples](https://github.com/soraxas/usydecho360/blob/master/Readme.md#examples)
5. [FAQ](https://github.com/soraxas/usydecho360/blob/master/Readme.md#faq)

USYDecho360 is a command-line Python tool that allows you to download lecture
videos from University of Sydney's Echo360 lecture portal. All that's required
is the particular course's UUID. See the FAQ for tips on how to find it.

Credits to [jhalstead85](https://github.com/jhalstead85/lecho360) for which this script is based upon, but this has been adopted to be usable for USYD echo360.

# Requirements #

### Python ###
- Dateutil >= 2.2
- Selenium >= 2.44.0
- ffmpy >= 0.2.2

```
pip install -r requirements.txt
```

### NodeJS ###
- PhantomJS >= 1.9.7

```
npm -g install phantomjs
```

### ffmpeg ###
This is required for transcoding ts file to mp4 file. See [here](https://github.com/adaptlearning/adapt_authoring/wiki/Installing-FFmpeg) for a brief instructions of installing it in different OS.

### Operating System ###
- Linux
- OS X
- Windows

# Usage #
```
>>> python usydEcho360.py

usage: usydEcho360.py [-h] --uuid COURSE_UUID [--output OUTPUT_PATH]
                      [--after-date AFTER_DATEYYYY-MM-DD)]
                      [--before-date BEFORE_DATE(YYYY-MM-DD] [--unikey UNIKEY]
                      [--password PASSWORD]

Download lectures from USYD's Echo360 portal.

optional arguments:
  -h, --help                              Show this help message and exit

  --uuid COURSE_UUID,                     Echo360 UUID for the course, which is
  -u COURSE_UUID                          found in the URL of the course's video
                                          lecture page.

  --output OUTPUT_PATH,                   Path to the desired output directory.
  -o OUTPUT_PATH                          The output directory must exist. Otherwise
                                          the current directory is used.

  --after-date AFTER_DATE(YYYY-MM-DD),    Only download lectures newer than
  -a AFTER_DATE(YYYY-MM-DD)               AFTER_DATE (inclusive). Note: This may
                                          be combined with --before-date.

  --before-date BEFORE_DATE(YYYY-MM-DD),  Only download lectures older than
  -b BEFORE_DATE(YYYY-MM-DD)              BEFORE_DATE (inclusive). Note: This may
                                          be combined with --after-date.

  --unikey UNIKEY,                        Your unikey for your University of Sydney
  -k UNIKEY                               elearning account

  --password PASSWORD,                    Your password for your University of Sydney
  -p PASSWORD                             elearning account
```
# Examples #

### Download all available lectures ###
```
>>> python usydEcho360.py                       \
  --uuid "041698d6-f43a-4b09-a39a-b90475a63530" \
  --ouput "~/Lectures"
```

### Download all lectures on or before a date ###
```
>>> python usydEcho360.py                       \
  --uuid "041698d6-f43a-4b09-a39a-b90475a63530" \
  --ouput "~/Lectures"                          \
  --before-date "2014-10-14"
```

### Download all lectures on or after a date ###
```
python usydEcho360.py                           \
  --uuid "041698d6-f43a-4b09-a39a-b90475a63530" \
  --ouput "~/Lectures"                          \
  --after-date "2014-10-14"
```

### Download all lectures in a given date range (inclusive) ###
```
>>> python usydEcho360.py                       \
  --uuid "041698d6-f43a-4b09-a39a-b90475a63530" \
  --ouput "~/Lectures"                          \
  --after-date "2014-08-26"                     \
  --before-date "2014-10-14"
```

# FAQ #

### How do I retrieve the UUID for a course? ###
This is the most involved part (unless you have access to a titles file). What you need is the URL to the course's main Echo360 lecture page. It's the main page that lists all the recorded lectures and gives you the option to stream them or download them individually.

![CIVL4093 Main Echo360 Lecture Page](https://i.imgur.com/jy8a99D.png)


You can usually find this link on your course's main webpage. If your course webpage only links directly to videos, then you should be able to navigate back to the main portale via that link.

The URL for the 2017 semester 2 of CIVL4903 looks like

```
https://view.streaming.sydney.edu.au:8443/ess/portal/section/041698d6-f43a-4b09-a39a-b90475a63530
```

which you can verify is correct in the above screenshot. The UUID is the last element of the URL. So in the above example it's,

```
041698d6-f43a-4b09-a39a-b90475a63530
```
