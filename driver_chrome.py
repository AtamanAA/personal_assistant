import os
import subprocess

from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options

from custom_undetected_chromedriver import CustomUndetectedChromeDriver
from variables import BASE_DIR


class ChromeBrowser:

    def __init__(self, headless: bool = False):
        self.headless = headless

    def __set_up(self):
        options = Options()
        ua = UserAgent(platforms='pc').random
        print(f"User-agent: {ua}")
        options.add_argument(f'--user-agent={ua}')
        options.add_argument("--window-size=800,600")
        options.add_argument("--enable-javascript")

        # TODO: add user-data-dir
        # username = os.getenv("USERNAME")
        # user_data_dir = os.path.join("C:\\Users", username, "AppData", "Local", "Google", "Chrome", "User Data",
        #                              "Default")
        # options.add_argument("user-data-dir={}".format(user_data_dir))

        # options.add_argument('--allow-profiles-outside-user-dir')
        # options.add_argument('--enable-profile-shortcut-manager')
        # # options.add_argument(r'user-data-dir=.\User')
        # options.add_argument(f"user-data-dir={os.path.join(BASE_DIR, 'User')}")
        # options.add_argument('--profile-directory=Profile 1')

        if self.headless:
            options.add_argument('--headless')  # headless mode
        version_main = int(self.__get_chrome_version)
        print(f"Browser version main: {version_main}")
        self.driver = CustomUndetectedChromeDriver(version_main=int(self.__get_chrome_version), options=options,
                                                   headless=self.headless)

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
