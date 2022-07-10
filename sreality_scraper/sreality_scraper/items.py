from scrapy import Item, Field


class OfferItem(Item):
    # Identity
    id = Field()                # (str) Ad number
    title = Field()             # (str) Offer title
    url = Field()               # (str) Full url
    deal_code = Field()         # (str) sale or rent
    property_code = Field()     # (str) apartment or house

    # Location
    longitude = Field()         # (float) longitude of the point in the map
    latitude = Field()          # (float) latitude of the point in the map
    address = Field()           # (str) address after the title

    # Description
    description = Field()       # (str) Offer description in CZ
    features = Field()          # (dict) offer features
    images = Field()            # (list) List of image urls

    # Price
    price = Field()             # (str) raw price from the offer
    price_amount = Field()      # (float) Offer price
    currency = Field()          # (str) Currency

    # Seller
    seller_id = Field()         # (str) seller id
    seller_name = Field()       # (str) seller name
