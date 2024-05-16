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

        self.page = ChromiumPage(addr_or_opts=options)

    def _get_url(self, url: str):
        print(f"Get url: {url}")
        self.page.get(url)

    def _login(self):
        print("Start login")

        self._get_url(url=self.login_url)
        time.sleep(10)
        print("Open init URL")

        # Find capcha iframe
        iframe = self.page.get_frame('@src^https://geo.captcha-delivery.com/captcha')
        if iframe:
            capcha_human_error = iframe.ele('.captcha__human')
            if capcha_human_error:
                print(f"Capcha human error:{capcha_human_error.text}")
            # Solve slide capcha
            # slide_capcha_solver = SlideCapchaSolveNew(page=self.page, capcha_frame=iframe)
            # slide_capcha_solver.solve_captcha()
        else:
            print("Capcha frame didn't find")

        self.page.get_screenshot(path=f"{BASE_DIR}/screenshots", name='UEFA_after_capcha_page.png', full_page=True)

        ac = Actions(self.page)

        # TODO: Debug input data
        # Input user data
        self.page.ele('@type=email').input(self.user_email)
        # email_input.input(self.user_email)
        self.page.ele('@type=password').input(self.user_password)
        # password_input.input(self.user_password)

        # submit_button = self.page.ele('.gigya-input-submit')
        submit_button = self.page.ele('.gigya-composite-control-submit')

        ac.move_to(submit_button).click()
        # submit_button.click()

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
