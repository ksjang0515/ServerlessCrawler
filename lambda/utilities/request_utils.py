import requests
import time

from constants import URL
from utilities.gql_utils import get_proxy

default_proxy = get_proxy()


def make_http_request(header, data, url=URL, proxy=default_proxy, retries=3):
    print(f"Starting request")
    request_success = False
    start_time = time.time()

    for _ in range(retries):
        try:
            response = requests.post(url, headers=header, json=data, proxies=proxy)
        except Exception as e:
            print("Exception Occurred")
            print(e)
            continue

        request_success = True
        break

    end_time = time.time()
    print(f"Request time - {end_time - start_time}")
    if not request_success:
        raise Exception("Request Failed")

    if response.status_code != 200:
        print(response.text)
        raise Exception(f"Got status code of {response.status_code}")

    return response
