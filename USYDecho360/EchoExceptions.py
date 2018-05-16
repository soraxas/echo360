class EchoLoginError(Exception):
    def __init__(self, driver):
        driver.quit()


class HlsDownloaderError(Exception):
    pass
