import os
import time

from DrissionPage import ChromiumPage, ChromiumOptions
from fake_useragent import UserAgent

from utils.capcha.audio_capcha import AudioCapchaSolve
from utils.capcha.slide_capcha_new import SlideCapchaSolveNew
from variables import UEFA_EMAIL, UEFA_PASSWORD, BASE_DIR
import random

# PROXY_HOST = "f-9933.sp5.ovh"  # rotating proxy or host
# PROXY_HOST = "127.0.0.1"  # rotating proxy or host
# PROXY_PORT = "8000"  # port
# PROXY_USER = ''  # username
# PROXY_PASS = ''  # password
#
#
# manifest_json = """
# {
#     "version": "1.0.0",
#     "manifest_version": 2,
#     "name": "Chrome Proxy",
#     "permissions": [
#         "proxy",
#         "tabs",
#         "unlimitedStorage",
#         "storage",
#         "<all_urls>",
#         "webRequest",
#         "webRequestBlocking"
#     ],
#     "background": {
#         "scripts": ["background.js"]
#     },
#     "minimum_chrome_version":"22.0.0"
# }
# """
#
# background_js = f"""
# var config = {{
#         mode: "fixed_servers",
#         rules: {{
#         singleProxy: {{
#             scheme: "http",
#             host: "{PROXY_HOST}",
#             port: parseInt("{PROXY_PORT}")
#         }},
#         bypassList: ["localhost", "127.0.0.1"]
#         }}
#     }};
#
# chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});
#
# function callbackFn(details) {{
#     return {{
#         authCredentials: {{
#             username: "{PROXY_USER}",
#             password: "{PROXY_PASS}"
#         }}
#     }};
# }}
#
# chrome.webRequest.onAuthRequired.addListener(
#             callbackFn,
#             {{urls: ["<all_urls>"]}},
#             ['blocking']
# );
# """

LOGIN_URL = "https://euro2024-sales.tickets.uefa.com/account"
TICKET_URL = "https://www.uefa.com/euro2024/ticketing/"


class UefaServiceNew:
    def __init__(self):
        self.login_url = LOGIN_URL
        self.ticket_url = TICKET_URL
        self.user_email = UEFA_EMAIL
        self.user_password = UEFA_PASSWORD
        self.cursor_debug = False

        ua = UserAgent(platforms='pc').random
        print(f"Set User-agent: {ua}")

        options = ChromiumOptions()
        options.headless(True)
        options.set_user_agent(user_agent=ua)
        options.set_argument("--accept-lang=en-US,uk;q=0.9")

        options.set_address("localhost:9090")

        # options.set_argument("--start-maximized")
        # options.set_argument("--disable-blink-features=AutomationControlled")
        # options.set_argument("--incognito")
        #
        # options.remove_argument("'--disable-popup-blocking'")

        # Disable all pop-up windows
        # options.set_pref(arg='profile.default_content_settings.popups', value='0')

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
        # options.remove_extensions()

        self.page = ChromiumPage(addr_or_opts=options)
        # self.page.clear_cache(cookies=True)  # For debug only

    def _get_url(self, url: str):
        print(f"Get url: {url}")
        self.page.get(url)

    def _login(self):
        print("Start login")

        self._get_url(url=self.login_url)
        time.sleep(random.uniform(8, 12))
        print("Open init URL")

        cookies = self.page.cookies()

        check_languages = self.page.run_js('return navigator.languages')
        print(f"Check languages: {check_languages}")

        if self.cursor_debug:
            self.__check_mouse_actions()

        # Find capcha iframe
        iframe = self.page.get_frame('@src^https://geo.captcha-delivery.com/captcha')
        if iframe:
            capcha_human_error = iframe.ele('.captcha__human')
            if capcha_human_error:
                print(f"Capcha human error:{capcha_human_error.text}")

            # Solve slide capcha
            slide_capcha_solver = SlideCapchaSolveNew(page=self.page, capcha_frame=iframe)
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

        # capcha_human_error = iframe.ele('.captcha__human')
        # if capcha_human_error:
        #     print(f"Capcha human error:{capcha_human_error.text}")
        else:
            print("Capcha frame didn't find")

        time.sleep(5)
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

    def __check_mouse_actions(self):
        # HTML string to add
        html_string = (
            '<div id="graph" style="position: fixed; top: 0; left: 0; z-index: 9999; background: rgba(255, 255, 255, 0.8); padding: 10px; border: 1px solid black;">'
            '<p>Move your mouse to see its position.</p>'
            '<p id="screen-log"></p>'
            '<canvas id="canvas" width="2550" height="1440" style="border: 1px solid black;"></canvas>'
            '</div>'
        )

        # JavaScript to add
        script_content = """
        window.onclick = function(event) {
            console.log(event);
        }

        let screenLog = document.querySelector("#screen-log");
        let canvas = document.querySelector("#canvas");
        let ctx = canvas.getContext("2d");
        let lastX, lastY;

        canvas.addEventListener("mousemove", logAndDraw);

        function logAndDraw(e) {
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            screenLog.innerText = `
                Canvas X/Y: ${x}, ${y}
                Client X/Y: ${e.clientX}, ${e.clientY}`;

            if (lastX !== undefined && lastY !== undefined) {
                ctx.beginPath();
                ctx.moveTo(lastX, lastY);
                ctx.lineTo(x, y);
                ctx.stroke();
            }

            lastX = x;
            lastY = y;
        }

        setInterval(() => {
            if (lastX !== undefined && lastY !== undefined) {
                let now = new Date();
                console.log(`Coordinates: (${lastX}, ${lastY}) at ${now.toLocaleTimeString()}`);
            }
        }, 500);
        """

        # Adding the HTML content to the page
        self.page.add_ele(html_or_info=html_string)

        # Running the script content
        self.page.run_js(script_content)

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
