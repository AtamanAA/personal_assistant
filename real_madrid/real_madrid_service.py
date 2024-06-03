from DrissionPage import ChromiumPage, ChromiumOptions
import time
from variables import BASE_DIR
from fake_useragent import UserAgent
import random

URL = "https://www.realmadrid.com/es-ES/entradas?filter-tickets=vip;general&filter-football=primer-equipo-masculino"


class RealMadridServiceNew:
    def __init__(self):
        self.login_url = URL

        ua = UserAgent(platforms='pc').random
        print(f"Set User-agent: {ua}")

        options = ChromiumOptions()
        options.headless(True)
        options.set_user_agent(user_agent=ua)
        options.set_argument("--accept-lang=en-US")
        options.set_address("localhost:9090")

        self.page = ChromiumPage(addr_or_opts=options)

        self.queue_number = None

    def _get_url(self, url: str):
        print(f"Get url: {url}")
        print(f"User agent from page: {self.page.user_agent}")
        self.page.get(URL)

    def solve_capcha(self, tab):
        iframe = tab.get_frame('@src^https://challenges.cloudflare.com/cdn-cgi')
        i = 1
        while iframe and i <= 3:
            print("Find capcha iframe")
            tab.get_screenshot(path=f"{BASE_DIR}/screenshots", name='real_madrid_capcha_tab.png',
                                      full_page=True)
            checkbox = iframe.ele('xpath:/html/body/div/div/div[1]/div/label/input')  # TODO: update be tag
            checkbox.click()
            print("Click to capcha checkbox")
            time.sleep(i * random.uniform(20, 30))

            iframe = tab.get_frame('@src^https://challenges.cloudflare.com/cdn-cgi')
            i += 1
            if not iframe:
                break

        return True

    def go_to_tickets_page(self):
        print("Start login")

        self._get_url(url=self.login_url)
        time.sleep(10)
        print("Open init URL")

        cookie_bottom = self.page.ele('#onetrust-accept-btn-handler', timeout=5)
        if cookie_bottom:
            cookie_bottom.click()
            print("Click to cookie bottom")
            time.sleep(3)

        buy_ticket_button = self.page.ele(
            'xpath:/html/body/app-root/app-views/app-tickets/main/app-calendar-list/div/div/app-all-event-card[1]/article/main/footer/rm-button[2]/button')
        buy_ticket_button.click()
        print("Click to buy_ticket bottom")

        tickets_tab = self.page.get_tab(0)
        time.sleep(5)

        print("Checkout to new tab")
        print(f"New tab title: {tickets_tab.title}")

        self.solve_capcha(tab=tickets_tab)

        time.sleep(10)
        print("Open tickets tab")
        print(f"Title new tab after capcha: {tickets_tab.title}")
        tickets_tab.get_screenshot(path=f"{BASE_DIR}/screenshots", name='real_madrid_after_capcha.png', full_page=True)
        print(f"Tab check url: {tickets_tab.url}")


        # print(f"Tab check html: {tickets_tab.html[:1000]}")
        # # Open a file in write mode
        # with open(f"{BASE_DIR}/screenshots/check_real_madrid.html", "w") as file:
        #     # Write the HTML content to the file
        #     file.write(tickets_tab.html)
        # try:
            # tickets_tab.wait.ele_displayed('.item-title', timeout=60)
            # check_text = tickets_tab.ele('.item-title').text
        #     if check_text:
        #         print(f"Check text: {check_text}")
        #     else:
        #         print("Check text didn't find on page")
        #     return True
        # except Exception as e:
        #     print("Element with class='item-title' didn't find")

        return tickets_tab

    def queue_wait(self, tab):
        queue_info = tab.ele('.warning-box')
        if queue_info:
            queue_number = tab.ele('#MainPart_lbQueueNumber').text
            self.queue_number = queue_number
            print(f"You queue_number: {queue_number}")

        while queue_info:
            wait_minutes = tab.ele('#MainPart_lbWhichIsIn').text
            online_users_count = tab.ele('#MainPart_lbUsersInLineAheadOfYou').text
            print(f"Online users in front of you: {online_users_count}")
            print(f"You will be logged in: '{wait_minutes}'")
            print("Wait 60 seconds for next check...")
            time.sleep(60)
            queue_info = tab.ele('.warning-box')
            if not queue_info:
                break

        self.solve_capcha(tab=tab)
        return tab

    def validate_member_number(self, tab):
        # TODO: Debug
        time.sleep(5)

        cookie_buttons = tab.eles('.cookie-button')
        if cookie_buttons:
            cookie_buttons[1].click()
            time.sleep(5)

        reveal_modal_dialog = tab.ele('.reveal-modal-dialog')
        if reveal_modal_dialog:
            member_user = "test_user"
            member_password = "test_password"

            member_user_input = tab.ele('.memberUser')
            member_password_input = tab.ele('.memberPwd')
            validate_botton = tab.ele('.sale-member-submit')

            member_user_input.input(member_user)
            member_password_input.input(member_password)
            validate_botton.click()

            time.sleep(5)

        return tab

    def run(self):
        tickets_tab = self.go_to_tickets_page()
        tickets_tab = self.queue_wait(tab=tickets_tab)
        tickets_tab = self.validate_member_number(tab=tickets_tab)
        time.sleep(10)
        self.page.close()
        self.page.quit()

if __name__ == '__main__':
    try:
        RealMadridServiceNew().run()
    except Exception as error:
        print(error)
