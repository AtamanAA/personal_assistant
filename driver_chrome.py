import os
import subprocess
from random import choice

from selenium.webdriver.chrome.options import Options

from custom_undetected_chromedriver import CustomUndetectedChromeDriver


class ChromeBrowser:

    def __init__(self, headless_mode: bool = True, captcha_app: bool = False):
        self.headless_mode = headless_mode
        # self.captcha_app = captcha_app

    def __set_up(self):
        options = Options()
        _ua = choice(list(map(str.rstrip, open("user_agent_pc.txt").readlines())))
        options.add_argument(f'--user-agent={_ua}')
        if self.headless_mode:
            options.add_argument('--headless')  # headless mode
        # if self.captcha_app:
        #     _path = os.path.abspath("captcha")
        #     options.add_argument(f'--load-extension={_path}')
        #     self.driver = CustomUndetectedChromeDriver(version_main=int(self.__get_chrome_version), options=options,
        #                                                headless=False)
        #     return
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