# Importing the necessary modules to successfully scrape the Coventry's pureportal website
import scrapy
from ..items import SearchEngineItem
from scrapy.crawler import CrawlerProcess

# Initializing the SearchEngineItem which helps to properly save and store the scrapped data
items = SearchEngineItem()


class CrawlSpider(scrapy.Spider):
    """An object that inherits it's properties from the scrapy.Spider class, The main purpose of the object is to
    scrape the chosen websites/urls"""

    name = 'crawler'
    page_number = 1
    start_urls = [
        'https://pureportal.coventry.ac.uk/en/organisations/school-of-computing-electronics-and-maths/publications/'
    ]

    def parse_data(self, response):
        """This function scrapes the necessary data from the Research output's page and stores them using the
        SearchEngine class"""

        items['title_link'] = response.request.url
        items['date'] = response.css(".date::text").get()
        items['author_link'] = response.css('.no-metrics a.link.person').xpath('@href').extract()

        # Due to the inconsistency in the naming of the css tags we have to use an if/else statement to check if the
        # tag is empty and if it is change the css tag in order to extract the necessary data
        if response.css('.no-metrics .persons span::text').extract():
            items['author'] = response.css('.no-metrics .persons span::text').extract()
        else:
            items['author'] = response.css('.no-metrics .persons::text').extract()
        if response.css('h1::text').extract():
            items['title'] = response.css('h1::text').extract()
        else:
            items['title'] = response.css('h1 span::text').extract()
        if response.css('.textblock::text').extract():
            items['abstract'] = response.css('.textblock::text').extract()
        else:
            items['abstract'] = response.css('.textblock p::text').extract()
        if response.css('.school span::text').extract():
            items['school'] = response.css('.school span::text').extract()
        else:
            items['school'] = response.css('.researchgroup span::text').extract()
        yield items

    def parse(self, response, **kwargs):
        """This function runs through all the pages of the Coventry's pureportal website and scrapes all the url for
        the different Research outputs"""

        container = response.css('.result-container')

        # Running a for loop through the container in order to get the urls for the Research outputs
        for research in container:
            title_link = research.css('h3.title a.link::attr(href)').get()
            yield response.follow(title_link, callback=self.parse_data)

        # Using an if statement to create a loop, that stops when the last page has been reached and continues otherwise
        next_page = 'https://pureportal.coventry.ac.uk/en/organisations/school-of-computing-electronics-and-maths/publications/?page=' + str(self.page_number)
        if response.css(".title span").extract():
            self.page_number += 1
            yield response.follow(next_page, callback=self.parse)


begin = CrawlerProcess(settings={
    'FEED_URI': 'documents.csv',
    'FEED_FORMAT': 'csv',
})

update = CrawlerProcess(settings={
    'FEED_URI': 'update.csv',
    'FEED_FORMAT': 'csv',
})

