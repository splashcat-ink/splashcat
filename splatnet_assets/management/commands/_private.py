import requests


def get_latest_version():
    version_data_url = 'https://raw.githubusercontent.com/Leanny/leanny.github.io/master/splat3/versions.json'
    return requests.get(version_data_url).json()[-1]
