import time

import requests

from variables import API_KEY_EZCAPTCHA


class DataDomeEZCaptcha:
    def __init__(
            self,
            web_site_url: str,
            captcha_url: str,
            slide: dict,
            proxy: dict = None,
            user_agent: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    ):
        self.web_site_url = web_site_url
        self.captcha_url = captcha_url
        self.slide = slide
        self.proxy = proxy
        self.user_agent = user_agent

        self.create_task_url = "https://sync.ez-captcha.com/createSyncTask"
        self.result_task_url = "https://api.2captcha.com/getTaskResult"

    def create_task(self):

        create_task_post = {
            "clientKey": API_KEY_EZCAPTCHA,
            "task": {
                "type": "DataDomeTaskProxyless",
                "task_type": "Slide",
                "end_point": self.web_site_url,
                "device_type": "ChromeWeb",
                "lang": "en-US",  # TODO
                # "tzp": "America/New_York",
                # "tz": 300,
                "ua": self.user_agent,
                "slide": self.slide,
            }
        }

        proxies = {
            "http": f'http://{self.proxy["user"]}:{self.proxy["password"]}@{self.proxy["host"]}:{self.proxy["port"]}',
            "https": f'http://{self.proxy["user"]}:{self.proxy["password"]}@{self.proxy["host"]}:{self.proxy["port"]}'
        }

        ip_check_response = requests.get('https://httpbin.org/ip', proxies=proxies)
        ip_check = ip_check_response.json()

        response = requests.post(self.create_task_url, json=create_task_post, proxies=proxies)
        task_info = response.json()
        print("Create EZCaptcha task")
        return task_info

    def get_result(self, task_id: str):

        result_post = {
            "clientKey": API_KEY_EZCAPTCHA,
            "taskId": task_id
        }
        proxies = {
            "http": f'http://{self.proxy["user"]}:{self.proxy["password"]}@{self.proxy["host"]}:{self.proxy["port"]}',
            "https": f'http://{self.proxy["user"]}:{self.proxy["password"]}@{self.proxy["host"]}:{self.proxy["port"]}'
        }

        ip_check_response = requests.get('https://httpbin.org/ip', proxies=proxies)
        ip_check = ip_check_response.json()

        result_response = requests.post(self.result_task_url, json=result_post, proxies=proxies)
        result = result_response.json()
        return result

    def solve(self):
        print("Start solve DataDome captcha")
        task_info = self.create_task()
        task_id = task_info["taskId"]
        time.sleep(10)

        while True:
            result = self.get_result(task_id=task_id)
            if not result.get("errorId"):
                if result.get("status") == "ready":
                    print("Captcha solution ready")
                    return result["solution"]
                if result.get("status") == "processing":
                    print("Captcha solution is processing. Wait 5 seconds.")
                    time.sleep(5)
                    continue
                else:
                    print("Unknown statuses")
                    break
            else:
                print(f"Captcha solve error: {result}")
                break
        return None
