import requests

from variables import PROXY_PASSWORD


def get_proxy_ip(proxy: dict):
    try:
        proxies = {
            "http": f'http://{proxy["user"]}:{PROXY_PASSWORD}@{proxy["host"]}:{proxy["port"]}',
            "https": f'http://{proxy["user"]}:{PROXY_PASSWORD}@{proxy["host"]}:{proxy["port"]}'
        }
        print(f"Proxy: {proxies['http']}")
        response = requests.get('https://httpbin.org/ip', proxies=proxies)
        ip = response.json()['origin']
        return ip
    except Exception as error:
        print(error)