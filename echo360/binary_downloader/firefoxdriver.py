from .downloader import BinaryDownloader


class FirefoxDownloader(BinaryDownloader):
    def __init__(self):
        self._name = "geckodriver"
        self._download_link_root = (
            "https://github.com/mozilla/geckodriver/releases/download"
        )
        self._version = "v0.33.0"

    def get_os_suffix(self):
        self._os_linux_32 = "linux32"
        self._os_linux_64 = "linux64"
        self._os_windows_32 = "win32"
        self._os_windows_64 = "win64"
        self._os_darwin_32 = "macos"
        self._os_darwin_64 = "macos"
        self._os_darwin_arm = "macos-aarch64"
        return super(FirefoxDownloader, self).get_os_suffix()

    def get_download_link(self):
        os_suffix = self.get_os_suffix()
        filename = "geckodriver-{0}-{1}.{2}".format(
            self._version,
            self.get_os_suffix(),
            "zip" if "win" in self.get_os_suffix() else "tar.gz",
        )
        download_link = "{0}/{1}/{2}".format(
            self._download_link_root, self._version, filename
        )
        return download_link, filename

    def get_bin_root_path(self):
        return super(FirefoxDownloader, self).get_bin_root_path()

    def get_bin(self):
        extension = ".exe" if "win" in self.get_os_suffix() else ""
        return "{0}/{1}{2}".format(self.get_bin_root_path(), self._name, extension)

    def download(self):
        super(FirefoxDownloader, self).download()
