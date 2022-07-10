import math
from unicodedata import normalize
from w3lib.url import add_or_replace_parameter

import jmespath
from scrapy import Spider, Request

from sreality_scraper.items import OfferItem
from sreality_scraper.loaders import OfferLoader
from sreality_scraper.site_state_data import *
from sreality_scraper.utils import get_url_path, reverse_dict_keys_values


class SrealityCzSpider(Spider):
    name = 'sreality_cz'
    allowed_domains = ['sreality.cz']

    BASE_OFFER_URL = 'https://www.sreality.cz/detail'
    BASE_API_URL = 'https://www.sreality.cz/api'
    ESTATES_API_URL = 'https://www.sreality.cz/api/cs/v2/estates'
    PRICE_CURRENCY = 'Kč'

    DEFAULT_N_RESULTS_PER_PAGE = 60

    def __init__(self, *args, **kwargs):
        self.offer_urls = kwargs.get('offer_urls')
        self.offers_pages = kwargs.get('offers_pages')
        self.n_results_per_page = int(kwargs.get(
            'n_results_per_page', self.DEFAULT_N_RESULTS_PER_PAGE))
        self.num_pages = int(kwargs.get('num_pages', 0))

    def start_requests(self):
        if self.offer_urls:
            return self.process_offer_urls()
        elif self.offers_pages:
            return self.process_offers_pages()

    def parse_offer(self, response):
        data = response.json()

        loader = OfferLoader(item=OfferItem())
        # Identity
        offer_id = self._parse_offer_id_from_url(response.url)
        loader.add_value('id', offer_id)
        loader.add_value('title', self._parse_title(data))
        loader.add_value('url', self._parse_url(data, offer_id))
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
        loader.add_value('currency', self.PRICE_CURRENCY)
        loader.add_value('price', self._parse_price(data))

        # Seller
        seller_data = jmespath.search('_embedded.seller', data)
        loader.add_jpath('seller_id', 'to_string(user_id)', seller_data)
        loader.add_jpath('seller_name', 'user_name', seller_data)
        return loader.load_item()

    @staticmethod
    def _parse_offer_id_from_url(url):
        path = get_url_path(url)
        return path[-1]

    def _parse_title(self, data):
        title = jmespath.search('name.value', data) or ''
        return normalize('NFKD', title)

    def _parse_url(self, data, offer_id):
        # getAppUrl_propertyDetail from all.js
        category_type_name = self._parse_url_category_type_name(data)
        category_main_name = self._parse_url_category_main_name(data)
        category_sub_name = self._parse_url_category_sub_name(data)
        locality = jmespath.search('seo.locality', data)
        return '/'.join((
            self.BASE_OFFER_URL,
            category_type_name,
            category_main_name,
            category_sub_name,
            locality,
            offer_id,
        ))

    def _parse_url_category_type_name(self, data):
        code = self._parse_category_type_code(data)
        return category_type_cb_detail.get(code) or 'undefined'

    def _parse_category_type_code(self, data):
        return jmespath.search('seo.category_type_cb', data)

    def _parse_url_category_main_name(self, data):
        code = self._parse_category_main_code(data)
        return category_main_cb_detail.get(code) or 'undefined'

    def _parse_category_main_code(self, data):
        return jmespath.search('seo.category_main_cb', data)

    def _parse_url_category_sub_name(self, data):
        code = self._parse_category_sub_code(data)
        return category_sub_cb_detail.get(code) or 'undefined'

    def _parse_category_sub_code(self, data):
        return jmespath.search('seo.category_sub_cb', data)

    def _parse_deal_code(self, data):
        code = self._parse_category_type_code(data)
        return category_type_cb_en.get(code)

    def _parse_property_code(self, data):
        code = self._parse_category_main_code(data)
        return category_main_cb_en.get(code)

    def _parse_features(self, data):
        features = {}
        features_data = jmespath.search('items[]', data) or []
        for feature_data in features_data:
            name = jmespath.search('name', feature_data)
            features[name] = self._parse_feature_value(feature_data)
        return features

    def _parse_feature_value(self, feature_data):
        type = jmespath.search('type', feature_data)
        if type == 'set':
            return self._parse_feature_set_value(feature_data)
        elif type == 'price':
            return self._parse_feature_price_value(feature_data)
        elif type == 'price_info':
            return self._parse_feature_price_info_value(feature_data)
        elif type == 'price_czk':
            return self._parse_feature_price_czk_value(feature_data)
        elif type in ['price_czk_m2', 'price_czk_old']:
            return self._parse_feature_price_czk_old_value(feature_data)
        elif type == 'boolean':
            return self._parse_feature_boolean_value(feature_data)
        elif type in ['url', 'energy_performance_attachment']:
            return self._parse_feature_url_value(feature_data)
        elif type == 'energy_performance':
            return self._parse_feature_energy_performance_value(feature_data)
        else:
            return self._parse_feature_other_value(feature_data)

    def _parse_feature_set_value(self, feature_data):
        values = jmespath.search('value[].value', feature_data) or []
        return ', '.join(values)

    def _parse_feature_price_value(self, feature_data):
        value = jmespath.search('value', feature_data) or ''
        value = normalize('NFKD', str(value))
        currency = jmespath.search('currency', feature_data)
        if currency:
            value = ' '.join((value, currency))
        unit = jmespath.search('unit', feature_data)
        if unit:
            value = ' '.join((value, unit))
        return value

    def _parse_feature_price_info_value(self, feature_data):
        value = jmespath.search('value', feature_data) or ''
        value = normalize('NFKD', str(value))
        negotiation = jmespath.search('negotiation', feature_data)
        if negotiation:
            value = ' '.join((value, NEGOTIATION_TEXT))
        return value

    def _parse_feature_price_czk_value(self, feature_data):
        value = self._parse_feature_price_czk_old_value(feature_data)
        negotiation = jmespath.search('negotiation', feature_data)
        if negotiation:
            value = ' '.join((value, NEGOTIATION_TEXT))
        return value

    def _parse_feature_price_czk_old_value(self, feature_data):
        value = jmespath.search('value', feature_data) or ''
        value = normalize('NFKD', str(value))
        currency = jmespath.search('currency', feature_data)
        value = ' '.join((value, currency))
        foreign_value = jmespath.search('foreign_value', feature_data)
        if foreign_value:
            value = ' ('.join((value, foreign_value))
            foreign_currency = jmespath.search(
                'foreign_currency', feature_data)
            if foreign_currency:
                value = ' '.join((value, foreign_currency))
            value = value + ')'
        unit = jmespath.search('unit', feature_data)
        if unit:
            value = ' '.join((value, unit))
        return value

    def _parse_feature_boolean_value(self, feature_data):
        value = jmespath.search('value', feature_data)
        return 'Yes' if value else 'No'

    def _parse_feature_url_value(self, feature_data):
        url = jmespath.search('url', feature_data)
        return url

    def _parse_feature_energy_performance_value(self, feature_data):
        value = jmespath.search('value', feature_data) or ''
        unit = jmespath.search('unit', feature_data) or ''
        unit2 = jmespath.search('unit2', feature_data) or ''
        list_data = (value, unit, unit2)
        return ' '.join((str(value) for value in list_data if value))

    def _parse_feature_other_value(self, feature_data):
        value = jmespath.search('value', feature_data) or ''
        unit = jmespath.search('unit', feature_data) or ''
        list_data = (value, unit)
        return ' '.join((str(value) for value in list_data if value))

    def _parse_price(self, data):
        value = jmespath.search('price_czk.value', data) or ''
        value = normalize('NFKD', value)
        unit = jmespath.search('price_czk.unit', data)
        price_data = (value, self.PRICE_CURRENCY, unit)
        price = ' '.join((value for value in price_data if value))
        if value:
            return price
        return 'Info o ceně u RK'

    def process_offer_urls(self):
        offer_urls = self.offer_urls.split('|||')
        for offer_url in offer_urls:
            offer_id = self._parse_offer_id_from_url(offer_url)
            yield Request(
                '/'.join((self.ESTATES_API_URL, offer_id)),
                self.parse_offer,
            )

    def process_offers_pages(self):
        offers_pages = self.offers_pages.split('|||')
        for offers_page in offers_pages:
            return self.make_offers_page_request(offers_page)

    def make_offers_page_request(self, offers_page):
        category_params = self._parse_category_params_from_url(offers_page)
        url = self.ESTATES_API_URL
        for key, value in category_params.items():
            url = add_or_replace_parameter(url, key, value)
        url = add_or_replace_parameter(
            url, 'per_page', self.n_results_per_page)
        yield Request(url, self.parse_offers_page)

    def parse_offers_page(self, response):
        data = response.json()
        offer_api_urls = self._parse_offer_api_urls(data)
        for offer_api_url in offer_api_urls:
            yield Request(offer_api_url, self.parse_offer)
        yield self.make_next_offers_page_request(response, data)

    def make_next_offers_page_request(self, response, data):
        total_matches = data.get('result_size')
        current_page = data.get('page')
        total_pages = math.ceil(total_matches / self.n_results_per_page)
        if self.num_pages:
            total_pages = min(self.num_pages, total_pages)
        if current_page < total_pages:
            next_page = current_page + 1
            url = add_or_replace_parameter(response.url, 'page', next_page)
            return Request(url, self.parse_offers_page)

    def _parse_category_params_from_url(self, offers_page):
        path = get_url_path(offers_page)
        category_type, category_main = path[-2:]
        category_type_data_rev = reverse_dict_keys_values(category_type_cb)
        category_main_data_rev = reverse_dict_keys_values(category_main_cb)
        return {
            'category_type_cb': category_type_data_rev.get(category_type),
            'category_main_cb': category_main_data_rev.get(category_main),
        }

    def _parse_offer_api_urls(self, data):
        jpath = '_embedded.estates[]._links.self.href'
        links = jmespath.search(jpath, data)
        return ['/'.join((self.BASE_API_URL, link.strip('/')))
                for link in links]
