import requests


def httphello():
    response = requests.get("https://httpbin.org/get")
    print("Status:", response.status_code)
    print("Headers:", response.headers["Content-Type"])
    print("Body:", response.json())


if __name__ == "__main__":
    httphello()
