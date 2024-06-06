import requests
from loguru import logger

from variables import PROXY_PASSWORD


log_file_path = "logs/uefa_logs.json"
logger.add(log_file_path, format="{time} {level} {message}", rotation="1 MB", serialize=True)


def get_proxy_ip(proxy: dict):
    try:
        proxies = {
            "http": f'http://{proxy["user"]}:{PROXY_PASSWORD}@{proxy["host"]}:{proxy["port"]}',
            "https": f'http://{proxy["user"]}:{PROXY_PASSWORD}@{proxy["host"]}:{proxy["port"]}'
        }
        logger.info(f"Proxy: {proxies['http']}")
        response = requests.get('https://httpbin.org/ip', proxies=proxies)
        logger.info(f"{response.json()}")
        ip = response.json()['origin']
        return ip
    except Exception as error:
        print(error)