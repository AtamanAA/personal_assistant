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

        check_detected_web_driver = self.driver.execute_script('return navigator.webdriver')
        print(f"Browser detected as web-driver: {check_detected_web_driver}")

        cookie = self.driver.get_cookies()[0]

        self.driver.add_cookie(cookie)

        capcha_frame = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, f'iframe[src*="https://geo.captcha-delivery.com/captcha"]'))
        )

        slide_capcha_solver = SlideCapchaSolve(driver=self.driver, capcha_frame=capcha_frame)
        slide_capcha_solver.solve_captcha()

        self.driver.save_screenshot(f"{BASE_DIR}/screenshots/uefa_capcha_result.png")

        check_detected_web_driver = self.driver.execute_script('return navigator.webdriver')
        print(f"Browser detected as web-driver on step 2: {check_detected_web_driver}")

        check_plugins = self.driver.execute_script('return navigator.plugins.length')
        print(f"Check plugins: {check_plugins}")

        check_languages = self.driver.execute_script('return navigator.languages')
        print(f"Check plugins: {check_languages}")

        vendor = self.driver.execute_script('''
            var canvas = document.createElement('canvas');
            var gl = canvas.getContext('webgl');

            var debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
            var vendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
            return vendor;
        ''')
        print(f"Vendor: {vendor}")

        check_web_gl = self.driver.execute_script('''
            var canvas = document.createElement('canvas');
            var gl = canvas.getContext('webgl');

            var debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
            var vendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
            var renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);

            if(vendor == "Brian Paul" && renderer == "Mesa OffScreen") {
                return true;
            } else {
                return false;
            }
        ''')

        print(f"Web GL check: {check_web_gl}")

        fake_image_check = self.driver.execute_script('''
            var body = document.getElementsByTagName("body")[0];
            var image = document.createElement("img");
            image.src = "http://iloveponeydotcom32188.jg";
            image.setAttribute("id", "fakeimage");
            body.appendChild(image);

            var detected = false;
            image.onerror = function(){
                if(image.width == 0 && image.height == 0) {
                    detected = true;
                }
            }

            return detected;
        ''')
        if fake_image_check:
            print("Chrome headless detected")

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
