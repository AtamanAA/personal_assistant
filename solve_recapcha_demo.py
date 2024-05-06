import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from custom_recapcha_solver import CustomRecaptchaSolver
from driver_chrome import ChromeBrowser

DEMO_URL = "https://www.google.com/recaptcha/api2/demo"


class UserRegisterDemo:
    def __init__(self, url: str = DEMO_URL):
        self.url = url
        self.driver = ChromeBrowser(headless_mode=False).get_driver()  # for demo: headless_mode=False

    def _get_url(self):
        print(f"Get url: {self.url}")
        self.driver.get(self.url)

    def _solve_captcha(self):
        print("Start Solve Capcha")
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, '//iframe[@title="reCAPTCHA"]')))
        recaptcha_iframe = self.driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
        solver = CustomRecaptchaSolver(driver=self.driver)
        solver.click_recaptcha_v2(iframe=recaptcha_iframe)
        print("Finish solve Capcha")

    def _insert_data(self):
        # TODO: Insert user info

        print("Start insert data")
        # self.driver.find_element(By.CSS_SELECTOR, "#i_agree_check").click()
        fake_name = "fake_name"
        fake_lastname = "fake_lastname"
        fake_email = 'fake_email@google.com'
        # self.driver.find_element(By.CSS_SELECTOR, "#input1").send_keys(fake_name)
        # self.driver.find_element(By.CSS_SELECTOR, "#input2").send_keys(fake_lastname)
        # self.driver.find_element(By.CSS_SELECTOR, "#input3").send_keys(fake_email)

        # Find the input elements
        input1 = self.driver.find_element(By.CSS_SELECTOR, "#input1")
        input2 = self.driver.find_element(By.CSS_SELECTOR, "#input2")
        input3 = self.driver.find_element(By.CSS_SELECTOR, "#input3")

        # Use Actions class to send keys to the input elements
        actions = ActionChains(self.driver)
        actions.move_to_element(input1).click().send_keys(fake_name).perform()
        actions.move_to_element(input2).click().send_keys(fake_lastname).perform()
        actions.move_to_element(input3).click().send_keys(fake_email).perform()

        print("Finish insert data")

    def new_register(self):
        self._get_url()
        self._solve_captcha()
        self._insert_data()
        self.driver.find_element(By.ID, "recaptcha-demo-submit").click()
        check = self.driver.find_element(By.CSS_SELECTOR, ".recaptcha-success")
        if check:
            print("Success check")
            # TODO: make screenshot


if __name__ == '__main__':
    try:
        UserRegisterDemo().new_register()
        time.sleep(30)
    except Exception as error:
        print(error)
