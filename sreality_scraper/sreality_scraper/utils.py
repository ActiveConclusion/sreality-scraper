from urllib.parse import urlparse


def get_url_path(url):
    parsed_url = urlparse(url)
    return parsed_url.path.split('/')
