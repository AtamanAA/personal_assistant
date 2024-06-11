import time

import requests
from loguru import logger

STABLE_PROXY_EXPORT_URL = "https://api.stableproxy.com/v2/package/download/39733c4c36525c9041849acb53ccf048/json/http/"


def get_proxies_list():
    response = requests.get(STABLE_PROXY_EXPORT_URL)
    proxies_list = response.json()
    return proxies_list


def check_proxy_list(proxy_list: list):
    check = []
    for proxy in proxy_list:
        proxies = {
            "http": f'http://{proxy["username"]}:{proxy["password"]}@{proxy["ip"]}:{proxy["port"]}',
            "https": f'http://{proxy["username"]}:{proxy["password"]}@{proxy["ip"]}:{proxy["port"]}'
        }
        print(f"Proxy: {proxies['http']}")
        try:
            ip_check_response = requests.get('https://httpbin.org/ip', proxies=proxies)
            ip_check = ip_check_response.json()
            print(ip_check)
            check.append({proxies['http']: ip_check})
            time.sleep(10)
        except Exception as error:
            check.append({proxies['http']: str(error.args[0].reason)})
            print(error)
            time.sleep(10)
    print(check)
    return check


def find_proxy_by_ip(proxy_list: list, ip: str):
    check = []
    for proxy in proxy_list:
        proxies = {
            "http": f'http://{proxy["username"]}:{proxy["password"]}@{proxy["ip"]}:{proxy["port"]}',
            "https": f'http://{proxy["username"]}:{proxy["password"]}@{proxy["ip"]}:{proxy["port"]}'
        }
        try:
            ip_check_response = requests.get('https://httpbin.org/ip', proxies=proxies)
            ip_check = ip_check_response.json()['origin']
            logger.debug(f"IP: {ip_check} isn't equal {ip} for proxy {proxies['http']}")
            if ip_check == ip:
                return proxy
            time.sleep(2)
        except Exception as error:
            check.append({proxies['http']: str(error.args[0].reason)})
            time.sleep(2)
    return None


if __name__ == '__main__':
    proxy_export_list = get_proxies_list()
    check_proxy_list(proxy_export_list)

