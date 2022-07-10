import jmespath
from scrapy import Spider, Request

from sreality_scraper.items import OfferItem
from sreality_scraper.loaders import OfferLoader
from sreality_scraper.utils import get_url_path


class SrealityCzSpider(Spider):
    name = 'sreality_cz'
    allowed_domains = ['sreality.cz']

    ESTATES_API_URL = 'https://www.sreality.cz/api/cs/v2/estates'

    def __init__(self, *args, **kwargs):
        self.offer_urls = kwargs.get('offer_urls')
        self.offers_pages = kwargs.get('offers_pages')

    def start_requests(self):
        if self.offer_urls:
            return self.process_offer_urls()
        elif self.offers_pages:
            return self.process_offers_pages()

    def parse_offer(self, response):
        data = response.json()

        loader = OfferLoader(item=OfferItem())
        # Identity
        loader.add_value('id', self._parse_offer_id_from_url(response.url))
        loader.add_jpath('title', 'name.value', data)
        loader.add_value('url', self._parse_url(data))
        loader.add_value('deal_code', self._parse_deal_code(data))
        loader.add_value('property_code', self._parse_property_code(data))

        # Location
        loader.add_jpath('longitude', 'map.lon', data)
        loader.add_jpath('latitude', 'map.lat', data)
        loader.add_jpath('address', 'locality.value', data)

        # Description
        loader.add_jpath('description', 'text.value', data)
        loader.add_value('features', self._parse_features(data))
        loader.add_jpath('images', '_embedded.images[]._links.view.href', data)

        # Price
        loader.add_jpath('price_amount', 'price_czk.value_raw', data)
        loader.add_value('currency', 'Kč')

        # Seller
        seller_data = jmespath.search('_embedded.seller', data)
        loader.add_jpath('seller_id', 'to_string(user_id)', seller_data)
        loader.add_jpath('seller_name', 'user_name', seller_data)
        return loader.load_item()

    @staticmethod
    def _parse_offer_id_from_url(url):
        path = get_url_path(url)
        return path[-1]

    def _parse_url(self, data):
        # getAppUrl_propertyDetail from all.js
        pass

    def _parse_deal_code(self, data):
        pass

    def _parse_property_code(self, data):
        pass

    def _parse_features(self, data):
        pass

    def process_offer_urls(self):
        offer_urls = self.offer_urls.split('|||')
        for offer_url in offer_urls:
            offer_id = self._parse_offer_id_from_url(offer_url)
            yield Request(
                '/'.join((self.ESTATES_API_URL, offer_id)),
                self.parse_offer,
            )
