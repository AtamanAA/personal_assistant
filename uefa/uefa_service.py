import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from driver_chrome import ChromeBrowser
from utils.capcha import SlideCapchaSolve
from variables import UEFA_EMAIL, UEFA_PASSWORD, BASE_DIR

LOGIN_URL = "https://euro2024-sales.tickets.uefa.com/account"
# LOGIN_URL = "https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html"

# https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html
TICKET_URL = "https://www.uefa.com/euro2024/ticketing/"


class UefaService:
    def __init__(self):
        self.login_url = LOGIN_URL
        self.ticket_url = TICKET_URL
        self.user_email = UEFA_EMAIL
        self.user_password = UEFA_PASSWORD
        self.driver = ChromeBrowser(headless=True).get_driver()  # for demo: headless_mode=False

    def _get_url(self, url: str):
        print(f"Get url: {url}")
        self.driver.get(url)

    def _login(self):
        print("Start login")

        self._get_url(url=self.login_url)

        cookie = self.driver.get_cookies()[0]

        self.driver.add_cookie(cookie)

        # Execute JavaScript code
        # self.driver.execute_script('''
        #     if (/HeadlessChrome/.test(window.navigator.userAgent)) {
        #         console.log("Chrome headless detected");
        #     }
        # ''')

        capcha_frame = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, f'iframe[src*="https://geo.captcha-delivery.com/captcha"]'))
        )

        slide_capcha_solver = SlideCapchaSolve(driver=self.driver, capcha_frame=capcha_frame)
        slide_capcha_solver.solve_captcha()

        self.driver.save_screenshot(f"{BASE_DIR}/screenshots/uefa_capcha_result.png")
        time.sleep(3)

        self.driver.save_screenshot(f"{BASE_DIR}/screenshots/uefa_login.png")
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
