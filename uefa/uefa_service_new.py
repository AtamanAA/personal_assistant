from DrissionPage import ChromiumPage, ChromiumOptions
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from driver_chrome import ChromeBrowser
from utils.capcha import SlideCapchaSolve
from utils.capcha import SlideCapchaSolveNew
from variables import UEFA_EMAIL, UEFA_PASSWORD, BASE_DIR
from fake_useragent import UserAgent
from DrissionPage.common import Actions

LOGIN_URL = "https://euro2024-sales.tickets.uefa.com/account"
TICKET_URL = "https://www.uefa.com/euro2024/ticketing/"


class UefaServiceNew:
    def __init__(self):
        self.login_url = LOGIN_URL
        self.ticket_url = TICKET_URL
        self.user_email = UEFA_EMAIL
        self.user_password = UEFA_PASSWORD

        ua = UserAgent(platforms='pc').random
        print(f"Set User-agent: {ua}")

        options = ChromiumOptions()
        options.headless(True)
        options.set_user_agent(user_agent=ua)
        options.set_argument("--accept-lang=en-US")

        # Disable all pop-up windows
        # options.set_pref(arg='profile.default_content_settings.popups', value='0')

        self.page = ChromiumPage(addr_or_opts=options)

    def _get_url(self, url: str):
        print(f"Get url: {url}")
        self.page.get(url)

    def _login(self):
        print("Start login")

        self._get_url(url=self.login_url)
        time.sleep(10)
        print("Open init URL")

        check_languages = self.page.run_js('return navigator.languages')
        print(f"Check languages: {check_languages}")

        # Find capcha iframe
        iframe = self.page.get_frame('@src^https://geo.captcha-delivery.com/captcha')
        if iframe:
            capcha_human_error = iframe.ele('.captcha__human')
            if capcha_human_error:
                print(f"Capcha human error:{capcha_human_error.text}")
            # Solve slide capcha
            slide_capcha_solver = SlideCapchaSolveNew(page=self.page, capcha_frame=iframe)
            slide_capcha_solver.solve_captcha()
        else:
            print("Capcha frame didn't find")

        self.page.get_screenshot(path=f"{BASE_DIR}/screenshots", name='UEFA_after_capcha_page.png', full_page=True)

        personal_account = self.page.wait.ele_displayed('#main_content_account_home_container', timeout=5)
        if personal_account:
            # TODO:
            print("You are in you personal account!")

        else:
            email = self.page.ele('xpath://*[@id="gigya-loginID-75579930407612940"]')
            email.input(self.user_email)
            password = self.page.ele('xpath://*[@id="gigya-password-32665041627364124"]')
            password.input(self.user_password)

            submit_button = self.page.ele('xpath://*[@id="gigya-login-form"]/div[4]/div/input')
            submit_button.click()

            time.sleep(10)
            self.page.get_screenshot(path=f"{BASE_DIR}/screenshots", name='UEFA_after_login.png', full_page=True)

    def run(self):
        self._login()
        time.sleep(10)
        self.page.close()
        self.page.quit()


if __name__ == '__main__':
    try:
        UefaServiceNew().run()
    except Exception as error:
        print(error)
