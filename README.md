# Sreality.cz Scraper

## Installation
It's recommended to use a virtual environment.
To install requirements, run:
```
pip install -r requirements.txt
```
## Usage
To scrape single offer url, use <code>offer_urls</code> argument.
It is possible to scrape data for multiple URLs using <code>|||</code> separator. 
Examples
```
# Single offer url
scrapy crawl sreality_cz -a offer_urls="https://www.sreality.cz/detail/prodej/byt/4+1/praha-veleslavin-jose-martiho/2054568028"

# Multiple offer urls
scrapy crawl sreality_cz -a offer_urls="https://www.sreality.cz/detail/prodej/byt/4+1/praha-veleslavin-jose-martiho/2054568028|||https://www.sreality.cz/detail/pronajem/dum/rodinny/praha-slivenec-/657077836"
```
To scrape offers page, use the <code>offers_page</code> argument. It's also possible to scrape multiple offers pages using <code>|||</code> separator.

Examples of offers pages:

Apartments for sale: https://www.sreality.cz/hledani/prodej/byty

Apartments for rent: https://www.sreality.cz/hledani/pronajem/byty

Houses for sale: https://www.sreality.cz/hledani/prodej/domy

Houses for rent: https://www.sreality.cz/hledani/pronajem/domy

Run example:
```
scrapy crawl sreality_cz -a offers_pages="https://www.sreality.cz/hledani/pronajem/domy"
```

If you want limit the number of pages for crawl, use optional argument <code>num_pages</code>

Example:
```
# Scrape 3 first pages
scrapy crawl sreality_cz -a offers_pages="https://www.sreality.cz/hledani/pronajem/domy" -a num_pages=3
```
## Output
[JSONs](sreality_scraper/scraped_data)
