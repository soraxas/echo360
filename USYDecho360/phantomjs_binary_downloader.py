#!/usr/bin/env python

import sys, os
import shutil

PHANTOMJS_DOWNLOAD_LINK_ROOT = 'https://bitbucket.org/ariya/phantomjs/downloads'
PHANTOMJS_VERSION = '2.1.1'

def get_os_suffix():
    if 'linux' in sys.platform:
        arch = '64' if sys.maxsize > 2**32 else '32'
        if arch == '64':
            return 'linux-x86_64'
        else:
            return 'linux-i686'
    elif 'win32' in sys.platform:
        return 'windows'
    elif 'darwin' in sys.platform:
        return 'macosx'
    else:
        raise Exception('NON-EXISTING OS VERSION')

def get_download_link():
    os_suffix = get_os_suffix()
    filename = 'phantomjs-{0}-{1}'.format(PHANTOMJS_VERSION, os_suffix)
    if 'linux' in os_suffix:
        filename = '{0}.tar.bz2'.format(filename)
    else:
        filename = '{0}.zip'.format(filename)
    download_link = '{0}/{1}'.format(PHANTOMJS_DOWNLOAD_LINK_ROOT, filename)
    return download_link, filename

def get_bin_root_path():
    return '{0}/bin'.format(os.getcwd())

def get_phantomjs_bin():
    extension = '.exe' if 'windows' in get_os_suffix() else ''
    return '{0}/phantomjs-{1}-{2}/bin/phantomjs{3}'.format(get_bin_root_path(), PHANTOMJS_VERSION, get_os_suffix(), extension)


def download():
    print('>> Downloading binary file for "{0}"'.format(get_os_suffix()))
    # Download bin for this os
    import wget
    link, filename = get_download_link()
    bin_path = get_bin_root_path()
    if not os.path.exists(bin_path): # create bin directory if not exists
        os.makedirs(bin_path)
    wget.download(link, out='{0}/{1}'.format(bin_path, filename))
    print('>> Extracting archive file "{0}"'.format(filename))
    if sys.version_info >= (3,0): # compatibility for python 2 & 3
        shutil.unpack_archive('{0}/{1}'.format(bin_path, filename), extract_dir=bin_path)
    else:
        if '.zip' in filename:
            import zipfile
            with zipfile.ZipFile('{0}/{1}'.format(bin_path, filename), 'r') as zip:
                zip.extractall(bin_path)
        elif '.tar' in filename:
            import tarfile
            with tarfile.open('{0}/{1}'.format(bin_path, filename)) as tar:
                tar.extractall(path=bin_path)
