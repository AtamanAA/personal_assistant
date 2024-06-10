import random
import time
from datetime import datetime

from DrissionPage import ChromiumPage, ChromiumOptions
from loguru import logger

from utils import create_proxy_auth_plugin
from variables import UEFA_EMAIL, UEFA_PASSWORD, BASE_DIR

log_file_path = "logs/uefa_logs.json"
logger.add(log_file_path, format="{time} {level} {message}", rotation="1 MB", serialize=True)

LOGIN_URL = "https://euro2024-sales.tickets.uefa.com/account"
TICKET_URL = "https://www.uefa.com/euro2024/ticketing/"


class UefaService:
    def __init__(self, proxy_user: str, proxy_host: str, proxy_port: str,
                 data_dome_cookie: str,
                 user_email: str = UEFA_EMAIL, user_password: str = UEFA_PASSWORD):
        logger.debug(f"Start init UefaService class")
        self.login_url = LOGIN_URL
        self.ticket_url = TICKET_URL
        self.user_email = user_email
        self.user_password = user_password

        self.data_dome_cookie = data_dome_cookie

        # self.user_agent = UserAgent(platforms='pc').random
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'

        options = ChromiumOptions()
        options.headless(True)
        options.set_user_agent(user_agent=self.user_agent)
        logger.debug(f"Set User-agent: {self.user_agent}")
        options.set_argument("--accept-lang=en-US,uk;q=0.9")
        logger.debug(f"Set languages")
        # options.set_argument("--accept-lang=en-US")

        user_data_path = f"{BASE_DIR}/temp/DrissionPage/userData_9000"
        logger.debug(f"User data path: {user_data_path}")
        options.set_user_data_path(user_data_path)

        options.set_argument('--start-maximized')

        # options.set_address("localhost:9090")  # For local test without proxy
        self.plugin_dir = f'{BASE_DIR}/proxy_auth_plugin'
        logger.debug(f"Plugin dir: {self.plugin_dir}")
        create_proxy_auth_plugin(plugin_dir=self.plugin_dir, proxy_user=proxy_user, proxy_host=proxy_host,
                                 proxy_port=proxy_port)
        logger.debug(f"Create proxy auth plugin")
        options.add_extension(self.plugin_dir)
        logger.debug(f"Add proxy auth extension")

        logger.debug(f"Check extension in options: {options.extensions}")

        self.page = ChromiumPage(addr_or_opts=options)
        logger.debug(f"Create Chrome page")
        self.page.clear_cache(cookies=True)  # For debug only

        self.successfully_completed = False
        self.screenshots_dir = f"{BASE_DIR}/screenshots/uefa"

    def _get_url(self, url: str):
        logger.info(f"Get url: {url}")
        self.page.get(url)

    def _login(self):
        logger.info("Start login")

        self._get_url(url=self.login_url)
        time.sleep(random.uniform(8, 12))

        check_cookies = self.page.cookies()
        logger.debug(f"Check cookie:{check_cookies}")

        updated_cookies = [
            {'name': 'datadome', 'value': self.data_dome_cookie, 'domain': '.uefa.com', 'max-age': "31536000",
             "secure": True, "samesite": "Lax", "path": "/"},
            {'name': 'SERVERID-BE-INTERNET1-9050', 'value': '056d2a0e7f8e7564e2734b2a6cf5b92f',
             'domain': 'euro2024-sales.tickets.uefa.com'}]
        self.page.set.cookies(cookies=updated_cookies)

        check_cookies = self.page.cookies()
        logger.debug(f"Updated cookie:{check_cookies}")
        time.sleep(random.uniform(8, 12))

        self.page.refresh()
        time.sleep(random.uniform(8, 12))
        logger.info("Refresh page after update cookies")

        check_languages = self.page.run_js('return navigator.languages')
        logger.debug(f"Check languages: {check_languages}")

        # Find capcha iframe
        iframe = self.page.get_frame('@src^https://geo.captcha-delivery.com/captcha')
        if iframe:
            capcha_human_error = iframe.ele('.captcha__human')
            if capcha_human_error:
                logger.debug(f"Capcha human error:{capcha_human_error.text}")

        # capcha_human_error = iframe.ele('.captcha__human')
        # if capcha_human_error:
        #     print(f"Capcha human error:{capcha_human_error.text}")
        else:
            logger.info("Capcha frame didn't find")

        time.sleep(5)

        time.sleep(random.uniform(8, 12))
        cookies = self.page.cookies()
        logger.debug(f"Check cookies: {cookies}")

        logger.debug(f"Page title after solve capcha: {self.page.title}")

        self.page.get_screenshot(path=self.screenshots_dir, name=f'UEFA_{datetime.now()}.png', full_page=True)

        logger.debug(f"Save screenshot for UEFA after capcha page")

        personal_account = self.page.wait.ele_displayed('#main_content_account_home_container', timeout=5)
        logger.debug(f"Save screenshot")
        if personal_account:
            # TODO:
            logger.success("You are in you personal account!")

        else:
            email = self.page.ele('xpath://*[@id="gigya-loginID-75579930407612940"]')
            email.input(self.user_email)
            logger.debug(f"Input user email")
            password = self.page.ele('xpath://*[@id="gigya-password-32665041627364124"]')
            password.input(self.user_password)
            logger.debug(f"Input user password")

            submit_button = self.page.ele('xpath://*[@id="gigya-login-form"]/div[4]/div/input')
            submit_button.click()

            time.sleep(random.uniform(8, 12))
            self.page.get_screenshot(path=self.screenshots_dir, name=f'UEFA_{datetime.now()}.png', full_page=True)
            logger.debug(f"Save screenshot for UEFA after login")
            logger.success("You are in you personal account!")

            self.successfully_completed = True

    def run(self):
        try:
            self._login()
            time.sleep(random.uniform(8, 12))
            self.page.close()
            self.page.quit()
        except Exception as e:
            logger.error(e)
            logger.info(f"Exception error")
        finally:
            self.page.close()
            self.page.quit()
            return self.successfully_completed


if __name__ == '__main__':
    try:
        UefaService(
            proxy_user="1GbgvO_0",
            proxy_host="rg-10340.sp1.ovh",
            proxy_port="11001",
            data_dome_cookie="test_cookie",
            user_email=UEFA_EMAIL,
            user_password=UEFA_PASSWORD
        ).run()
    except Exception as error:
        print(error)
