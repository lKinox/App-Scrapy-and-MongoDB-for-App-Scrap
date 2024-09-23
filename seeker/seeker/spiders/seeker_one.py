from flask import jsonify
from scrapy.item import Field
from scrapy.item import Item
from scrapy.spiders import Spider
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector

class Noticia(Item):
    id = Field()
    title = Field()
    price = Field()

class SeekerOneSpider(Spider):
    name = 'seeker_one'
    start_urls = ['https://gamaenlinea.com/es/rones/c/A0403?pageSize=100']

    def parse(self, response):
        sel = Selector(response)
        products = sel.xpath('//div[contains(@class, "product-item")]')
        
        product_list = []
        product_id = 1
        for product in products:
            item = {
                'id': product_id,
                'title': product.xpath('.//h3/text()').get().strip(),
                'price': product.xpath('.//div[contains(@class, "cx-product-price")]/span/text()').get().strip()
            }
            yield item
            product_list.append(item)
            product_id += 1 

        return product_list

process = CrawlerProcess({
    'FEED_FORMAT': 'json',
    'FEED_URI': 'datos_de_salida_3.json'
})

process.crawl(SeekerOneSpider)
process.start()

