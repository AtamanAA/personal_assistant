import time

import requests

from variables import API_KEY_2CAPCHA

PROXY_HOST = "res.proxy-seller.com"
PROXY_PORT = "10005"
PROXY_USER = '0aa734af980085a2'
PROXY_PASS = 'RNW78Fm5'


class DataDomeCaptcha:
    def __init__(
            self,
            web_site_url: str,
            captcha_url: str,
            proxy: dict = None,
            user_agent: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    ):
        self.web_site_url = web_site_url
        self.captcha_url = captcha_url
        self.proxy = proxy
        self.user_agent = user_agent

        self.create_task_url = "https://api.2captcha.com/createTask"
        self.result_task_url = "https://api.2captcha.com/getTaskResult"

    def create_task(self):
        create_task_post = {
            "clientKey": API_KEY_2CAPCHA,
            "task": {
                "type": "DataDomeSliderTask",
                "websiteURL": self.web_site_url,
                "captchaUrl": self.captcha_url,
                "userAgent": self.user_agent,
                "proxyType": self.proxy["type"],
                "proxyAddress": self.proxy["host"],
                # "proxyAddress": "107.195.8.162",
                "proxyPort": self.proxy["port"],
                "proxyLogin": self.proxy["user"],
                "proxyPassword": self.proxy["password"]
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
        print("Create 2Captcha task")
        return task_info

    def get_result(self, task_id: str):

        result_post = {
            "clientKey": API_KEY_2CAPCHA,
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

if __name__ == '__main__':
    try:
        proxy = {
            "type": "http",
            "host": PROXY_HOST,
            "port": PROXY_PORT,
            "user": PROXY_USER,
            "password": PROXY_PASS,
        }
        captcha_remote_solver = DataDomeCaptcha(
            web_site_url="https://euro2024-sales.tickets.uefa.com/account",
            captcha_url="https://geo.captcha-delivery.com/captcha/?initialCid=AHrlqAAAAAMAE00We2rYdIQATCTptw%3D%3D&hash=EC3B9FB6F2A31D3AF16C270E6531D2&cid=CnKQfv_H4BfjzPq6nRo0aD7Ta3_Zlj~8slrMZhllkZaJGiZ7TbbZrHfOA_9PmhLgySkjTECARZ2bpHl9bwhNRFCf1ay_wBxXNYpvfW6YAIpA2FWdWwX9_280Jw9B~cpb&t=fe&referer=https%3A%2F%2Feuro2024-sales.tickets.uefa.com%2Faccount&s=43337&e=b7ba73740db341deb7d7a02e85dbc266a90826164caad3d1e8696a234c583c2e&dm=cd",
            proxy=proxy,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36')
        solution = captcha_remote_solver.solve()
        solution_cookie = solution.get("cookie")
        test = 3
    except Exception as error:
        print(error)
