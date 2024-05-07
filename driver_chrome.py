import os
import subprocess

from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options

from custom_undetected_chromedriver import CustomUndetectedChromeDriver


class ChromeBrowser:

    def __init__(self, headless_mode: bool = True):
        self.headless_mode = headless_mode

    def __set_up(self):
        options = Options()
        ua = UserAgent(platforms='pc').random
        print(f"User-agent: {ua}")
        options.add_argument(f'--user-agent={ua}')
        options.add_argument("--window-size=800,600")
        if self.headless_mode:
            options.add_argument('--headless')  # headless mode
        self.driver = CustomUndetectedChromeDriver(version_main=int(self.__get_chrome_version), options=options,
                                                   headless=False)

    @property
    def __get_chrome_version(self):
        """Detects Chrome version depending on platform"""
        if os.name == 'nt':
            import winreg
            # open the registry key containing information about Google Chrome
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            # read the value of the "version" key
            version = winreg.QueryValueEx(reg_key, "version")[0]
            return version.split(".")[0]
        else:
            output = subprocess.check_output(['google-chrome', '--version'])
            try:
                version = output.decode('utf-8').split()[-1]
                version = version.split(".")[0]
                return version
            except Exception as error:
                raise Exception(f"Chrome Exception: {error}")

    def get_driver(self):
        self.__set_up()
        return self.driver


if __name__ == '__main__':
    ChromeBrowser().get_driver()
