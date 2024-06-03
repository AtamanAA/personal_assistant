from DrissionPage import ChromiumPage, ChromiumOptions
import time
from variables import BASE_DIR
from fake_useragent import UserAgent

URL = "https://test-english.com"


class CloudCapchaDemo:
    def __init__(self):
        self.login_url = URL

        ua = UserAgent(platforms='pc').random
        print(f"Set User-agent: {ua}")

        options = ChromiumOptions()
        options.headless(True)
        options.set_user_agent(user_agent=ua)

        self.page = ChromiumPage(addr_or_opts=options)

    def _get_url(self, url: str):
        print(f"Get url: {url}")
        print(f"User agent from page: {self.page.user_agent}")
        self.page.get(URL)

    def _login(self):
        print("Start login")

        self._get_url(url=self.login_url)
        time.sleep(10)
        print("Open init URL")

        iframe = self.page.get_frame('@src^https://challenges.cloudflare.com/cdn-cgi')
        if iframe:
            print("Find capcha iframe")
            self.page.get_screenshot(path=f"{BASE_DIR}/screenshots", name='real_madrid_capcha_tab.png',
                                     full_page=True)
            checkbox = iframe.ele('xpath:/html/body/div/div/div[1]/div/label/input')  # TODO: update be tag
            checkbox.click()
            print("Click to capcha checkbox")
        else:
            print("Capcha didn't find")

        time.sleep(10)
        print(f"Title new tab after capcha: {self.page.title}")
        self.page.get_screenshot(path=f"{BASE_DIR}/screenshots", name='real_madrid_after_capcha.png', full_page=True)
        print(f"Tab check url: {self.page.url}")

    def run(self):
        self._login()
        time.sleep(10)
        self.page.close()
        self.page.quit()


if __name__ == '__main__':
    try:
        CloudCapchaDemo().run()
    except Exception as error:
        print(error)
