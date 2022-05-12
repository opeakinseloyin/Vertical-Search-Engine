# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SearchEngineItem(scrapy.Item):
    """This class inherits it's properties from the scrapy.Item class and is used to properly store the scraped data"""

    title = scrapy.Field()
    title_link = scrapy.Field()
    author = scrapy.Field()
    author_link = scrapy.Field()
    date = scrapy.Field()
    abstract = scrapy.Field()
    school = scrapy.Field()

