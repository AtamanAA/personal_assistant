import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from driver_chrome import ChromeBrowser
from variables import DOC_STUDIO_EMAIL, DOC_STUDIO_PASSWORD

DEMO_URL = "https://app.docstudio.com/auth/login"


class DocStudioLoginDemo:
    def __init__(self, url: str = DEMO_URL):
        self.url = url
        self.doc_studio_email = DOC_STUDIO_EMAIL
        self.doc_studio_password = DOC_STUDIO_PASSWORD
        # self.driver = ChromeBrowser(headless_mode=False).get_driver()  # for demo: headless_mode=False
        self.driver = ChromeBrowser(headless_mode=True).get_driver()  # for demo: headless_mode=False

    def _get_url(self):
        print(f"Get url: {self.url}")
        self.driver.get(self.url)

    def _login(self):
        print("Start login")

        email_xpath = '/html/body/app-root/app-auth/div/div[1]/div/app-login/div[3]/form/mat-form-field[1]/div[1]/div/div[2]/input'
        password_xpath = '/html/body/app-root/app-auth/div/div[1]/div/app-login/div[3]/form/mat-form-field[2]/div[1]/div/div[2]/input'
        email_input = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, email_xpath)))

        password_input = self.driver.find_element(By.XPATH, password_xpath)
        submit_button = self.driver.find_element(By.CSS_SELECTOR, ".auth-submit")

        email_input.send_keys(self.doc_studio_email)
        password_input.send_keys(self.doc_studio_password)
        submit_button.click()

        time.sleep(10)
        self.driver.save_screenshot("screenshots/doc_studio_success_login.png")

    def _go_to_waiting_for_you(self):
        print("Open 'Wating for you' folder")
        waiting_for_you_filter = self.driver.find_element(By.CSS_SELECTOR, ".waiting")
        waiting_for_you_filter.click()

    def _open_first_document(self):
        print("Open first document")
        first_waiting_document = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".subject")))
        first_waiting_document.click()
        time.sleep(10)
        self.driver.save_screenshot("screenshots/doc_studio_success_open_first_document.png")

    def sign_doc(self):
        print("Make signature")
        signature = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".envelope-sign")))
        signature.click()
        time.sleep(10)
        self.driver.save_screenshot("screenshots/doc_studio_success_sign_first_document.png")
        # TODO: click send or not now bottom
        # not_now_button = WebDriverWait(self.driver, 10).until(
        #     EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.grey-button')))
        # not_now_button.click()
        # time.sleep(10)
        # self.driver.save_screenshot("screenshots/doc_studio_success_not_send_first_document.png")

    def sign_first_document(self):
        self._get_url()
        self._login()
        self._go_to_waiting_for_you()
        self._open_first_document()
        self.sign_doc()
        time.sleep(20)
        self.driver.quit()


if __name__ == '__main__':
    try:
        DocStudioLoginDemo().sign_first_document()
    except Exception as error:
        print(error)
