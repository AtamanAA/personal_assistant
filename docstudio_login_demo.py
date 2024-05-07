import time

from selenium.webdriver.common.by import By

from driver_chrome import ChromeBrowser
from variables import DOC_STUDIO_EMAIL, DOC_STUDIO_PASSWORD

DEMO_URL = "https://app.docstudio.com/auth/login"


class DocStudioLoginDemo:
    def __init__(self, url: str = DEMO_URL):
        self.url = url
        self.doc_studio_email = DOC_STUDIO_EMAIL
        self.doc_studio_password = DOC_STUDIO_PASSWORD
        self.driver = ChromeBrowser(headless_mode=False).get_driver()  # for demo: headless_mode=False

    def _get_url(self):
        print(f"Get url: {self.url}")
        self.driver.get(self.url)

    def _login(self):
        print("Start login")
        time.sleep(10)

        email_input = self.driver.find_element(By.XPATH, '/html/body/app-root/app-auth/div/div[1]/div/app-login/div[3]/form/mat-form-field[1]/div[1]/div/div[2]/input')
        password_input = self.driver.find_element(By.XPATH, '/html/body/app-root/app-auth/div/div[1]/div/app-login/div[3]/form/mat-form-field[2]/div[1]/div/div[2]/input')
        submit_button = self.driver.find_element(By.CSS_SELECTOR, ".auth-submit")

        email_input.send_keys(self.doc_studio_email)
        password_input.send_keys(self.doc_studio_password)
        submit_button.click()

        time.sleep(10)
        self.driver.save_screenshot("screenshots/doc_studio_success_login.png")

        print("Finish login")

    def go_to_dashboard(self):
        self._get_url()
        self._login()
        time.sleep(20)
        self.driver.quit()


if __name__ == '__main__':
    try:
        DocStudioLoginDemo().go_to_dashboard()
    except Exception as error:
        print(error)
