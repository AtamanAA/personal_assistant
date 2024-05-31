import os
import time

from DrissionPage import ChromiumPage, ChromiumOptions, SessionOptions
from fake_useragent import UserAgent

from utils.capcha.audio_capcha import AudioCapchaSolve
from utils.capcha.slide_capcha_new import SlideCapchaSolveNew
from utils import DataDomeCaptcha, DataDomeEZCaptcha
from variables import UEFA_EMAIL, UEFA_PASSWORD, BASE_DIR
from uefa_sessions import UEFA_SESSIONS
import random
import base64
import requests


CURRENT_SESSION = UEFA_SESSIONS[1]

# PROXY_HOST = "res.proxy-seller.com"
# PROXY_PORT = "10002"
# PROXY_USER = '0aa734af980085a2'
# PROXY_PASS = 'RNW78Fm5'


PROXY_USER = CURRENT_SESSION["proxy"].lstrip("http://").split(":")[0]
PROXY_PASS = CURRENT_SESSION["proxy"].lstrip("http://").split(":")[1].split("@")[0]
PROXY_HOST = CURRENT_SESSION["proxy"].lstrip("http://").split(":")[1].split("@")[1]
PROXY_PORT = CURRENT_SESSION["proxy"].lstrip("http://").split(":")[2]

SOLUTION_COOKIE = CURRENT_SESSION["datadome_cookie"]


manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""

background_js = f"""
var config = {{
        mode: "fixed_servers",
        rules: {{
        singleProxy: {{
            scheme: "http",
            host: "{PROXY_HOST}",
            port: parseInt("{PROXY_PORT}")
        }},
        bypassList: ["localhost", "127.0.0.1"]
        }}
    }};

chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

function callbackFn(details) {{
    return {{
        authCredentials: {{
            username: "{PROXY_USER}",
            password: "{PROXY_PASS}"
        }}
    }};
}}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {{urls: ["<all_urls>"]}},
            ['blocking']
);
"""

LOGIN_URL = "https://euro2024-sales.tickets.uefa.com/account"
TICKET_URL = "https://www.uefa.com/euro2024/ticketing/"

LOGIN_URL = "https://www.zocdoc.com/"


class UefaServiceNew:
    def __init__(self):
        self.login_url = LOGIN_URL
        self.ticket_url = TICKET_URL
        self.user_email = UEFA_EMAIL
        self.user_password = UEFA_PASSWORD

        # self.user_agent = UserAgent(platforms='pc').random
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'

        print(f"Set User-agent: {self.user_agent}")

        options = ChromiumOptions()
        options.headless(True)
        options.set_user_agent(user_agent=self.user_agent)
        options.set_argument("--accept-lang=en-US,uk;q=0.9")
        # options.set_argument("--accept-lang=en-US")

        options.set_address("localhost:9000")

        # options.set_argument("--start-maximized")
        # options.set_argument("--disable-blink-features=AutomationControlled")
        # options.set_argument("--incognito")
        #
        # options.remove_argument("'--disable-popup-blocking'")
        # plugin_dir = 'proxy_auth_plugin'
        # # Create plugin directory if it doesn't exist
        # if not os.path.exists(plugin_dir):
        #     os.makedirs(plugin_dir)
        # # Write manifest.json and background.js to the plugin directory
        # with open(os.path.join(plugin_dir, "manifest.json"), 'w') as f:
        #     f.write(manifest_json)
        # with open(os.path.join(plugin_dir, "background.js"), 'w') as f:
        #     f.write(background_js)
        #
        # options.add_extension(plugin_dir)
        # Disable all pop-up windows
        # options.set_pref(arg='profile.default_content_settings.popups', value='0')


        # options.remove_extensions()

        self.page = ChromiumPage(addr_or_opts=options)
        self.page.clear_cache(cookies=True)  # For debug only

    def _get_url(self, url: str):
        print(f"Get url: {url}")
        self.page.get(url)

    def _login(self):
        print("Start login")

        self._get_url(url=self.login_url)
        time.sleep(random.uniform(8, 12))
        print("Open init URL")

        check_cookies = self.page.cookies()
        print(f"Check cookie:{check_cookies}")

        # updated_cookies = [{'name': 'datadome', 'value': SOLUTION_COOKIE, 'domain': '.uefa.com', 'max-age': "31536000", "secure": True, "samesite": "Lax", "path": "/"}, {'name': 'SERVERID-BE-INTERNET1-9050', 'value': '056d2a0e7f8e7564e2734b2a6cf5b92f', 'domain': 'euro2024-sales.tickets.uefa.com'}]
        # self.page.set.cookies(cookies=updated_cookies)
        #
        # check_cookies = self.page.cookies()
        # print(f"Updated cookie:{check_cookies}")
        # time.sleep(random.uniform(8, 12))
        #
        # self.page.refresh()
        # time.sleep(random.uniform(8, 12))
        # print("Refresh page after update cookies")

        check_languages = self.page.run_js('return navigator.languages')
        print(f"Check languages: {check_languages}")

        # Find capcha iframe
        iframe = self.page.get_frame('@src^https://geo.captcha-delivery.com/captcha')
        if iframe:
            capcha_human_error = iframe.ele('.captcha__human')
            if capcha_human_error:
                print(f"Capcha human error:{capcha_human_error.text}")

            proxy = {
                "type": "http",
                "host": PROXY_HOST,
                "port": PROXY_PORT,
                "user": PROXY_USER,
                "password": PROXY_PASS,
            }

            captcha_url = iframe.attrs.get("src")
            captcha_query_param_list = captcha_url.split("?")[1].split("&")
            captcha_query_param_dict = {}
            for param in captcha_query_param_list:
                key, value = param.split("=")
                captcha_query_param_dict[key] = value

            ddm = iframe.run_js("return window.ddm;")
            captcha_callback_text = iframe.run_js("return captchaCallback.toString();")
            lines = captcha_callback_text.split('\n')

            # Extract the line containing 'getRequest += "&icid="'
            icid_line = next((line for line in lines if "getRequest += '&icid='" in line), None)
            icid_string = icid_line.split(" + ")[1]
            icid = iframe.run_js(f"return {icid_string}")

            # Extract the line containing 'getRequest += "&userEnv="'
            userEnv_line = next((line for line in lines if "getRequest += '&userEnv='" in line), None)
            userEnv_string = userEnv_line.split(" + ")[1]
            userEnv = iframe.run_js(f"return {userEnv_string}")

            # Extract the line containing 'getRequest += "&ddCaptchaChallenge="'
            ddCaptchaChallenge_line = next((line for line in lines if "getRequest += '&ddCaptchaChallenge='" in line), None)
            ddCaptchaChallenge_string = ddCaptchaChallenge_line.split(" + ")[1]
            ddCaptchaChallenge = iframe.run_js(f"return {ddCaptchaChallenge_string}")

            # Extract the line containing 'getRequest += "&ddCaptchaEnv="'
            ddCaptchaEnv_line = next((line for line in lines if "getRequest += '&ddCaptchaEnv='" in line), None)
            ddCaptchaEnv_string = ddCaptchaEnv_line.split(" + ")[1]
            ddCaptchaEnv = iframe.run_js(f"return {ddCaptchaEnv_string}")

            # Extract the line containing 'getRequest += "&ddCaptchaAudioChallenge="'
            ddCaptchaAudioChallenge_line = next((line for line in lines if "getRequest += '&ddCaptchaAudioChallenge='" in line), None)
            ddCaptchaAudioChallenge_string = ddCaptchaAudioChallenge_line.split(" + ")[1]
            ddCaptchaAudioChallenge = iframe.run_js(f"return {ddCaptchaAudioChallenge_string}")

            proxies = {
                "http": f'http://{proxy["user"]}:{proxy["password"]}@{proxy["host"]}:{proxy["port"]}',
                "https": f'http://{proxy["user"]}:{proxy["password"]}@{proxy["host"]}:{proxy["port"]}'
            }

            preload_image_url = iframe.ele('xpath=/html/head/link[4]').href

            # Download the image
            response = requests.get(preload_image_url, proxies=proxies)
            image_data = response.content

            # Convert the image data to a base64 string
            base64_encoded_image = base64.b64encode(image_data).decode('utf-8')

            slide = {
                "cid": ddm["cid"],
                "hash": ddm['hash'],
                "ua": ddm["ua"],
                "referer": ddm['referer'],
                "s": ddm['s'],
                "icid": icid,
                "userEnv": userEnv,
                "ddCaptchaChallenge": ddCaptchaChallenge,
                "ddCaptchaEnv": ddCaptchaEnv,
                "ddCaptchaAudioChallenge": ddCaptchaAudioChallenge,
                "captchaChallengeSeed": ddCaptchaAudioChallenge,  # TODO: Find this param
                "imageBase64": base64_encoded_image,  # TODO:
                "checkParentUrl": captcha_url
            }

            # Solve slide capcha
            captcha_remote_solver = DataDomeCaptcha(web_site_url=LOGIN_URL, captcha_url=captcha_url, proxy=proxy,
                                             user_agent=self.user_agent)
            solution = captcha_remote_solver.solve()
            solution_cookie = solution.get("cookie")

            # # Solve slide capcha EZCaptcha
            # captcha_remote_solver = DataDomeEZCaptcha(web_site_url=LOGIN_URL, captcha_url=captcha_url, slide=slide,
            #                                           proxy=proxy, user_agent=self.user_agent)
            # solution = captcha_remote_solver.solve()
            # solution_cookie = solution.get("cookie")

            # Set solution cookies
            current_cookies = self.page.cookies()
            print(f"Initial cookie:{current_cookies}")
            self.page.clear_cache(session_storage=False, local_storage=False, cache=False, cookies=True)
            datadome_value = solution_cookie.split(";")[0].lstrip("datadome=")
            updated_cookies = current_cookies.copy()
            for cookie in updated_cookies:
                if cookie["name"] == "datadome":
                    cookie["value"] = datadome_value
            self.page.set.cookies(cookies=updated_cookies)
            check_cookies = self.page.cookies()
            print(f"Updated cookie:{check_cookies}")
            time.sleep(random.uniform(3, 5))

            self.page.refresh()
            time.sleep(random.uniform(8, 12))
            print("Refresh page after update cookies")


            # # Move slider
            # slide_capcha_solver = SlideCapchaSolveNew(page=self.page, capcha_frame=iframe)
            # slide_capcha_solver.solve_captcha()

        # capcha_human_error = iframe.ele('.captcha__human')
        # if capcha_human_error:
        #     print(f"Capcha human error:{capcha_human_error.text}")
        else:
            print("Capcha frame didn't find")

        time.sleep(5)

        time.sleep(random.uniform(8, 12))
        cookies = self.page.cookies()
        print(f"Check cookies: {cookies}")

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
        UefaServiceNew().run()
    except Exception as error:
        print(error)
