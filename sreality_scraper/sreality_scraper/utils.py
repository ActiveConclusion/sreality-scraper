from urllib.parse import urlparse


def get_url_path(url):
    parsed_url = urlparse(url)
    return parsed_url.path.split('/')


def reverse_dict_keys_values(d):
    return dict(zip(d.values(), d.keys()))
