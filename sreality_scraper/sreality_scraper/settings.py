BOT_NAME = 'sreality_scraper'

SPIDER_MODULES = ['sreality_scraper.spiders']
NEWSPIDER_MODULE = 'sreality_scraper.spiders'


USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.49'
)

COOKIES_ENABLED = False

DEFAULT_REQUEST_HEADERS = {
    'Accept': 'application/json, text/plain, */*',
}
