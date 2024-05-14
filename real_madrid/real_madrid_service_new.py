from DrissionPage import ChromiumPage, ChromiumOptions
import time
from variables import BASE_DIR

URL = "https://www.realmadrid.com/es-ES/entradas?filter-tickets=vip;general&filter-football=primer-equipo-masculino"


class RealMadridServiceNew:
    def __init__(self):
        self.login_url = URL

        options = ChromiumOptions()
        options.headless(True)
        self.page = ChromiumPage(addr_or_opts=options)

    def _get_url(self, url: str):
        print(f"Get url: {url}")
        self.page.get(URL)

    def _login(self):
        print("Start login")

        self._get_url(url=self.login_url)
        time.sleep(10)
        print("Open init URL")

        # TODO: https://github.com/g1879/DrissionPage/blob/master/docs_en/SessionPage/session_options.md
        # cookie_bottom = WebDriverWait(self.driver, 10).until(
        #     EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        # )
        # self.driver.save_screenshot(f"{BASE_DIR}/screenshots/real_madrid_start_page.png")
        # cookie_bottom.click()
        # print("Click to cookie bottom")
        #
        # time.sleep(10)
        # cookies = self.driver.get_cookies()
        # if cookies:
        #     for cookie in cookies:
        #         self.driver.add_cookie(cookie)
        # print("Set cookies")

        buy_ticket_button = self.page.ele(
            'xpath:/html/body/app-root/app-views/app-tickets/main/app-calendar-list/div/div/app-all-event-card[1]/article/main/footer/rm-button[2]/button')
        buy_ticket_button.click()
        print("Click to buy_ticket bottom")

        capcha_tab = self.page.get_tab(0)

        time.sleep(5)
        print(f"Title new tab: {capcha_tab.title}")

        iframe = capcha_tab.get_frame('@src^https://challenges.cloudflare.com/cdn-cgi')
        if iframe:
            print("Find capcha iframe")
            capcha_tab.get_screenshot(path=f"{BASE_DIR}/screenshots", name='real_madrid_capcha_tab.png',
                                      full_page=True)
            checkbox = iframe.ele('xpath:/html/body/div/div/div[1]/div/label/input')  # TODO: update be tag
            checkbox.click()
            print("Click to capcha checkbox")

        time.sleep(30)
        print("Open tickets tab")
        print(f"Title new tab after capcha: {capcha_tab.title}")
        capcha_tab.get_screenshot(path=f"{BASE_DIR}/screenshots", name='real_madrid_after_capcha.png', full_page=True)
        print(f"Tab check url: {capcha_tab.url}")
        print(f"Tab check html: {capcha_tab.html[:1000]}")

        # Open a file in write mode
        with open(f"{BASE_DIR}/screenshots/check_real_madrid.html", "w") as file:
            # Write the HTML content to the file
            file.write(capcha_tab.html)

        # try:
            # capcha_tab.wait.ele_displayed('.item-title', timeout=60)
            # check_text = capcha_tab.ele('.item-title').text
        #     if check_text:
        #         print(f"Check text: {check_text}")
        #     else:
        #         print("Check text didn't find on page")
        #     return True
        # except Exception as e:
        #     print("Element with class='item-title' didn't find")

    def run(self):
        self._login()
        time.sleep(10)
        self.page.close()
        self.page.quit()


if __name__ == '__main__':
    try:
        RealMadridServiceNew().run()
    except Exception as error:
        print(error)
