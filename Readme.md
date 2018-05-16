# USYDecho360 #

USYDecho360 is a command-line Python tool that allows you to download lecture videos from University of Sydney's Echo360 lecture portal. All that's required is the particular course's UUID. See the FAQ for tips on how to find it.


Updates as of 18/03/2018: It now will works on canvas echo360 as well (https://canvas.sydney.edu.au/).

# Getting Started #

### Automated Installation ###

**Linux / MacOS**
```bash
./run.sh COURSE_UUID  # where COURSE_UUID is your course id
```
**Windows**
```bash
run.bat COURSE_UUID  # where COURSE_UUID is your course id
```
The scripts will boostrap all installation and download all needed files on the fly.
### Optional ###
- ffmpeg (for transcoding ts file to mp4 file) See [here](https://github.com/adaptlearning/adapt_authoring/wiki/Installing-FFmpeg) for a brief instructions of installing it in different OS.

## Manual ##
The provided script automated every operation, and install all dependency in a local python virtual environment. You can also use the system-wise python installation by manual installation. Get started by first install all requirements:
```bash
pip install -r requirements.txt  # or with: python -m pip install -r requirements.txt
```
Then run with:
```
python usydEcho360.py
```

### Operating System ###
- Linux
- OS X
- Windows



# Usage #
**NOTE THAT** all the below command you can substitute `python usydEcho360.py` with `./run.sh` (or `run.bat` if you are in windows)

### Quick Start ###
```
>>> python usydEcho360.py                       \
    "041698d6-f43a-4b09-a39a-b90475a63530"
```
### Script args ###
```
>>> usage: usydEcho360.py [-h] [--output OUTPUT_PATH]
                      [--after-date AFTER_DATEYYYY-MM-DD)]
                      [--before-date BEFORE_DATE(YYYY-MM-DD] [--unikey UNIKEY]
                      [--password PASSWORD] [--download-phantomjs-binary]
                      [--chrome]
                      COURSE_UUID

Download lectures from USYD's Echo360 portal.

positional arguments:
  COURSE_UUID           Echo360 UUID for the course, which is found in the URL
                        of the course's video lecture page (e.g.
                        '115f3def-7371-4e98-b72f-6efe53771b2a' in http://recor
                        dings.engineering.illinois.edu/ess/portal/section/115f
                        3def-7371-4e98-b72f-6efe53771b2a)

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT_PATH, -o OUTPUT_PATH
                        Path to the desired output directory The output
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
                        Force the usydEcho360.py script to download a local
                        binary file for phantomjs (will override system bin)
  --chrome              Use Chrome Driver instead of phantomjs webdriver. You
                        must have chromedriver installed in your PATH.

```
# Examples #
```
>>> python usydEcho360.py                  \
    "041698d6-f43a-4b09-a39a-b90475a63530" \
    --output "~/Lectures"
```

### Download all available lectures ###
```
>>> python usydEcho360.py                  \
    "041698d6-f43a-4b09-a39a-b90475a63530" \
    --output "~/Lectures"
```

### Download all lectures on or before a date ###
```
>>> python usydEcho360.py                  \
    "041698d6-f43a-4b09-a39a-b90475a63530" \
    --output "~/Lectures"                  \
    --before-date "2014-10-14"
```

### Download all lectures on or after a date ###
```
>>> python usydEcho360.py                  \
    "041698d6-f43a-4b09-a39a-b90475a63530" \
    --output "~/Lectures"                  \
    --after-date "2014-10-14"
```

### Download all lectures in a given date range (inclusive) ###
```
>>> python usydEcho360.py                  \
    "041698d6-f43a-4b09-a39a-b90475a63530" \
    --output "~/Lectures"                  \
    --after-date "2014-08-26"              \
    --before-date "2014-10-14"
```

### Use chrome driver (instead of phantomjs) ###
Note: sometime it works better than phantomjs in some system
```
>>> python usydEcho360.py                  \
    "041698d6-f43a-4b09-a39a-b90475a63530" \
    --chrome
```

# FAQ #

### How do I retrieve the UUID for a course? ###portal
This is the most involved part (unless you have access to a titles file). What you need is the URL to the course's main Echo360 lecture page. It's the main page that lists all the recorded lectures and gives you the option to stream them or download them individually.

![CIVL4093 Main Echo360 Lecture Page](https://i.imgur.com/jy8a99D.png)


You can usually find this link on your course's main webpage. If your course webpage only links directly to videos, then you should be able to navigate back to the main portal via that link.

The URL for the 2017 semester 2 of CIVL4903 looks like

```
https://view.streaming.sydney.edu.au:8443/ess/portal/section/041698d6-f43a-4b09-a39a-b90475a63530
```

which you can verify is correct in the above screenshot. The UUID is the last element of the URL. So in the above example it's,

```
041698d6-f43a-4b09-a39a-b90475a63530
```

# Credits #
Credits to [jhalstead85](https://github.com/jhalstead85/lecho360) for which this script is based upon, but this has been adopted to be usable for USYD echo360.
