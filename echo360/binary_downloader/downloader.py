import sys
import os
import platform
import stat
import wget
import shutil
import logging

_LOGGER = logging.getLogger(__name__)


class BinaryDownloader(object):
    def __init__(self):
        raise NotImplementedError

    def get_os_suffix(self):
        arch = "64" if sys.maxsize > 2**32 else "32"
        if "linux" in sys.platform:
            if arch == "64":
                return self._os_linux_64
            else:
                return self._os_linux_32
        elif "win32" in sys.platform:
            if arch == "64":
                return self._os_windows_64
            else:
                return self._os_windows_32
        elif "darwin" in sys.platform:
            # detect if this is using arm processor (e.g. M1/M2 Mac)
            if platform.processor() == "arm":
                return self._os_darwin_arm
            if arch == "64":
                return self._os_darwin_64
            else:
                return self._os_darwin_32
        else:
            raise Exception("NON-EXISTING OS VERSION")

    def get_download_link(self):
        raise NotImplementedError

    def get_bin_root_path(self):
        return "{0}/bin".format(os.getcwd())

    def get_bin(self):
        raise NotImplementedError

    def download(self):
        print(
            '>> Downloading {0} binary file for "{1}"'.format(
                self._name, self.get_os_suffix()
            )
        )
        # Download bin for this os
        link, filename = self.get_download_link()
        bin_path = self.get_bin_root_path()
        # delete bin directory if exists
        if os.path.exists(bin_path):
            shutil.rmtree(bin_path)
        os.makedirs(bin_path)
        # remove existing binary file or folder
        wget.download(link, out="{0}/{1}".format(bin_path, filename))
        print('\r\n>> Extracting archive file "{0}"'.format(filename))
        if sys.version_info >= (3, 0):  # compatibility for python 2 & 3
            shutil.unpack_archive(
                "{0}/{1}".format(bin_path, filename), extract_dir=bin_path
            )
        else:
            if ".zip" in filename:
                import zipfile

                with zipfile.ZipFile("{0}/{1}".format(bin_path, filename), "r") as zip:
                    zip.extractall(bin_path)
            elif ".tar" in filename:
                import tarfile

                with tarfile.open("{0}/{1}".format(bin_path, filename)) as tar:
                    tar.extractall(path=bin_path)
        # Make the extracted bin executable
        st = os.stat(self.get_bin())
        os.chmod(self.get_bin(), st.st_mode | stat.S_IEXEC)
