import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from variables import UEFA_EMAIL, UEFA_PASSWORD
from driver_chrome import ChromeBrowser
from utils.capcha import SlideCapchaSolve


LOGIN_URL = "https://euro2024-sales.tickets.uefa.com/account"
TICKET_URL = "https://www.uefa.com/euro2024/ticketing/"


class UefaService:
    def __init__(self):
        self.login_url = LOGIN_URL
        self.ticket_url = TICKET_URL
        self.user_email = UEFA_EMAIL
        self.user_password = UEFA_PASSWORD
        self.driver = ChromeBrowser(headless_mode=False).get_driver()  # for demo: headless_mode=False

    def _get_url(self, url: str):
        print(f"Get url: {url}")
        self.driver.get(url)

    def _login(self):
        print("Start login")

        self._get_url(url=self.login_url)

        self.driver.add_cookie({"name": "key", "value": "value"})  # TODO:

        capcha_frame = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, f'iframe[src*="https://geo.captcha-delivery.com/captcha"]'))
        )

        slide_capcha_solver = SlideCapchaSolve(driver=self.driver, capcha_frame=capcha_frame)
        slide_capcha_solver.solve_captcha()

        time.sleep(10)
        return True

    def run(self):
        self._login()
        time.sleep(10)
        self.driver.quit()


if __name__ == '__main__':
    try:
        UefaService().run()
    except Exception as error:
        print(error)
