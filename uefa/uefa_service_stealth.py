import time

from DrissionPage import ChromiumPage, ChromiumOptions
from fake_useragent import UserAgent

from utils.capcha.audio_capcha import AudioCapchaSolve
from utils.capcha.slide_capcha_stealt import SlideCapchaSolveStealth
from variables import UEFA_EMAIL, UEFA_PASSWORD, BASE_DIR
import random

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from seleniumwire import webdriver

LOGIN_URL = "https://euro2024-sales.tickets.uefa.com/account"
TICKET_URL = "https://www.uefa.com/euro2024/ticketing/"


class UefaServiceStealth:
    def __init__(self):
        self.login_url = LOGIN_URL
        self.ticket_url = TICKET_URL
        self.user_email = UEFA_EMAIL
        self.user_password = UEFA_PASSWORD

        ua = UserAgent(platforms='pc').random
        print(f"Set User-agent: {ua}")

        options = webdriver.ChromeOptions()
        # options.add_argument('--headless=new')
        options.add_argument("--start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        proxy_ip = "f-9933.sp5.ovh"
        proxy_port = "11005"
        proxy_user = "N0eQ06hVPd_4"
        proxy_password = "rNA1eGRLec1Z"
        proxy = f"{proxy_user}:{proxy_password}@{proxy_ip}:{proxy_port}"  # Replace with your proxy details
        # options.add_argument(f'--proxy-server={proxy}')

        s = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=s, options=options)

        stealth(self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )

    def _get_url(self, url: str):
        print(f"Get url: {url}")
        self.driver.get(url)

    def _login(self):
        print("Start login")

        self._get_url(url=self.login_url)
        time.sleep(random.uniform(8, 12))
        print("Open init URL")

        # check_languages = self.page.run_js('return navigator.languages')
        # print(f"Check languages: {check_languages}")

        # Find capcha iframe
        capcha_frame = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, f'iframe[src*="https://geo.captcha-delivery.com/captcha"]'))
        )
        if capcha_frame:
            # capcha_human_error = capcha_frame.ele('.captcha__human')
            # if capcha_human_error:
            #     print(f"Capcha human error:{capcha_human_error.text}")

            # Solve slide capcha
            slide_capcha_solver = SlideCapchaSolveStealth(driver=self.driver, capcha_frame=capcha_frame)
            slide_capcha_solver.solve_captcha()

            # Solve audio capcha
            # while True:  # TODO: refactor
            #     audio_capcha_solver = AudioCapchaSolve(page=self.page, capcha_frame=iframe)
            #     solve_audio_capcha = audio_capcha_solver.solve_audio_capcha()
            #     if solve_audio_capcha:
            #         break
            #     iframe.ele('#captcha__reload__button').click()
            #     print("Reload audio challenge")
            #     continue

        time.sleep(5)
        self.driver.save_screenshot(f"{BASE_DIR}/screenshots/uefa_capcha_result.png")

        #TODO: conver for selenium
        print(f"Page title after solve capcha: {self.page.title}")

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

            time.sleep(random.uniform(8, 12))
            self.page.get_screenshot(path=f"{BASE_DIR}/screenshots", name='UEFA_after_login.png', full_page=True)

    def run(self):
        self._login()
        time.sleep(random.uniform(8, 12))
        self.page.close()
        self.page.quit()


if __name__ == '__main__':
    try:
        UefaServiceStealth().run()
    except Exception as error:
        print(error)
