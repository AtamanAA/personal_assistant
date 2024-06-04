import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.chrome_driver.driver_chrome import ChromeBrowser
from variables import UEFA_EMAIL, UEFA_PASSWORD, BASE_DIR

URL = "https://www.realmadrid.com/es-ES/entradas?filter-tickets=vip;general&filter-football=primer-equipo-masculino"


class RealMadridService:
    def __init__(self):
        self.login_url = URL
        self.user_email = UEFA_EMAIL
        self.user_password = UEFA_PASSWORD
        self.driver = ChromeBrowser(headless=False).get_driver()  # for demo: headless_mode=False

    def _get_url(self, url: str):
        print(f"Get url: {url}")
        self.driver.get(url)

    def _login(self):
        print("Start login")

        self._get_url(url=self.login_url)
        self.driver.maximize_window()

        check_detected_web_driver = self.driver.execute_script('return navigator.webdriver')
        print(f"Browser detected as web-driver: {check_detected_web_driver}")

        # cookie_bottom = WebDriverWait(self.driver, 10).until(
        #     EC.invisibility_of_element_located((By.ID, "onetrust-accept-btn-handler"))
        # )

        cookie_bottom = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        self.driver.save_screenshot(f"{BASE_DIR}/screenshots/real_madrid_start_page.png")
        cookie_bottom.click()
        print("Click to cookie bottom")

        time.sleep(10)
        cookies = self.driver.get_cookies()
        if cookies:
            for cookie in cookies:
                self.driver.add_cookie(cookie)
        print("Set cookies")

        buy_ticket_button = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR,
                                              ".event-card__additionalLinks.rm-button-component.rm-button-component--block.rm-button-component--primary.rm-button-component--x-small.rm-button-component--x-smallrm-button-component"))
        )
        buy_ticket_button.click()
        print("Click to buy_ticket bottom")

        time.sleep(5)
        self.driver.save_screenshot(f"{BASE_DIR}/screenshots/real_madrid_2_step.png")

        self.driver.switch_to.window(self.driver.window_handles[1])
        print("Switch to capcha window")

        time.sleep(5)
        self.driver.save_screenshot(f"{BASE_DIR}/screenshots/real_madrid_3_step.png")

        capcha_frame = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, f'iframe[src*="https://challenges.cloudflare.com"]'))
        )

        self.driver.switch_to.frame(capcha_frame)
        input_element = self.driver.find_element(By.TAG_NAME, "input")
        input_element.click()
        print("Click to capcha checkbox")
        self.driver.save_screenshot(f"{BASE_DIR}/screenshots/real_madrid_4_step.png")
        time.sleep(5)
        self.driver.save_screenshot(f"{BASE_DIR}/screenshots/real_madrid_5_step.png")



        # self.driver.save_screenshot(f"{BASE_DIR}/screenshots/uefa_capcha_result.png")
        #
        # check_detected_web_driver = self.driver.execute_script('return navigator.webdriver')
        # print(f"Browser detected as web-driver on step 2: {check_detected_web_driver}")
        #
        # check_plugins = self.driver.execute_script('return navigator.plugins.length')
        # print(f"Check plugins: {check_plugins}")
        #
        # check_languages = self.driver.execute_script('return navigator.languages')
        # print(f"Check plugins: {check_languages}")
        #
        # vendor = self.driver.execute_script('''
        #     var canvas = document.createElement('canvas');
        #     var gl = canvas.getContext('webgl');
        #
        #     var debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
        #     var vendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
        #     return vendor;
        # ''')
        # print(f"Vendor: {vendor}")
        #
        # check_web_gl = self.driver.execute_script('''
        #     var canvas = document.createElement('canvas');
        #     var gl = canvas.getContext('webgl');
        #
        #     var debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
        #     var vendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
        #     var renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
        #
        #     if(vendor == "Brian Paul" && renderer == "Mesa OffScreen") {
        #         return true;
        #     } else {
        #         return false;
        #     }
        # ''')
        #
        # print(f"Web GL check: {check_web_gl}")
        #
        # fake_image_check = self.driver.execute_script('''
        #     var body = document.getElementsByTagName("body")[0];
        #     var image = document.createElement("img");
        #     image.src = "http://iloveponeydotcom32188.jg";
        #     image.setAttribute("id", "fakeimage");
        #     body.appendChild(image);
        #
        #     var detected = false;
        #     image.onerror = function(){
        #         if(image.width == 0 && image.height == 0) {
        #             detected = true;
        #         }
        #     }
        #
        #     return detected;
        # ''')
        # if fake_image_check:
        #     print("Chrome headless detected")
        #
        # time.sleep(3)
        #
        # self.driver.save_screenshot(f"{BASE_DIR}/screenshots/uefa_login.png")
        return True

    def run(self):
        self._login()
        time.sleep(10)
        self.driver.quit()


if __name__ == '__main__':
    try:
        RealMadridService().run()
    except Exception as error:
        print(error)
