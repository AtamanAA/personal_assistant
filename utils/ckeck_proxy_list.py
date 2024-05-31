import time

import requests

STABLE_PROXY_EXPORT_URL = "https://api.stableproxy.com/v2/package/download/39733c4c36525c9041849acb53ccf048/json/http/"


def get_proxies_list():
    response = requests.get(STABLE_PROXY_EXPORT_URL)
    proxies_list = response.json()
    return proxies_list


def check_proxy_list(proxy_list: list):
    for proxy in proxy_list[3:4]:
        try:
            proxies = {
                "http": f'http://{proxy["username"]}:{proxy["password"]}@{proxy["ip"]}:{proxy["port"]}',
                "https": f'http://{proxy["username"]}:{proxy["password"]}@{proxy["ip"]}:{proxy["port"]}'
            }
            print(f"Proxy: {proxies['http']}")
            ip_check_response = requests.get('https://httpbin.org/ip', proxies=proxies)
            ip_check = ip_check_response.json()
            print(ip_check)
            time.sleep(3)
        except Exception as error:
            print(error)


if __name__ == '__main__':
    proxy_export_list = get_proxies_list()
    check_proxy_list(proxy_export_list)

