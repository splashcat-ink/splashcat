import requests
from django.conf import settings

host = "splashcat.ink"


def send_indexnow_request(path: str):
    if settings.DEBUG:
        return
    print("sending indexnow request", path)
    response = requests.get("https://api.indexnow.org/indexnow", params={
        "url": f"https://{host}{path}",
        "key": settings.INDEXNOW_API_KEY,
    })
    if not response.ok:
        print("failed to send indexnow request", response.status_code, response.reason, response.text)
