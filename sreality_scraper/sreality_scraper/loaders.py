import jmespath
from itemloaders import ItemLoader
from itemloaders.processors import Identity
from itemloaders.processors import TakeFirst


class OfferLoader(ItemLoader):
    default_output_processor = TakeFirst()
    images_out = Identity()

    def add_jpath(self, field_name, path, json_object, *processors, **kw):
        values = jmespath.search(path, json_object)
        self.add_value(field_name, values, *processors, **kw)
