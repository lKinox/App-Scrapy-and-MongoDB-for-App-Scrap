from flask import Flask, request, jsonify, Blueprint, json
import multiprocessing
from scrapy.spiders import Spider
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from pymongo import MongoClient
from fake_useragent import UserAgent
from scrapy import signals
import os
import time
import re

api_gama_blueprint = Blueprint('api_gama', __name__)


client = MongoClient("mongodb+srv://reyanjimenez:mjWiDjrreHl66MuY@consultor-api-db.tqpkb.mongodb.net/?retryWrites=true&w=majority&appName=consultor-api-db")
db = client["test"]
collection = db["gama"]

class SeekerOneSpider(Spider):
    name = 'seeker_one'
    start_urls = []

    def __init__(self, url, user_agent="Scrapy"):
        self.start_urls = [url]
        #self.user_agent = user_agent
        
    def parse(self, response):
        #if self.user_agent:
            #request.headers.setdefault(b"User-Agent", self.user_agent)
        sel = Selector(response)
        time.sleep(1)
        category = sel.xpath('//ol[contains(@class, "breadcrumb")]')
        sub_category = sel.xpath('//app-eg-category-title')
        products = sel.xpath('//div[contains(@class, "product-item")]')

        def extract_price(price_string):
                pattern = r'\d+(,\d+)?'
                match = re.search(pattern, price_string)
                if match:
                    return match.group()
                else:
                    return None

        product_list = []
        product_id = 1
        for product in products:
            price_string = product.xpath('.//div[contains(@class, "cx-product-price")]/span/text()').get().strip()
            price = extract_price(price_string)
            item = {
                'id': product_id,
                'title': product.xpath('.//h3/text()').get().strip(),
                'price': price
            }
            product_list.append(item)
            product_id += 1 
        
        """for _ in range(3):
            try:
                category = category.xpath('.//li[contains(@class, "breadcrumb__item")][2]/a/text()').get().strip()
                return category
            except AttributeError:
                time.sleep(5)
                print("Error al extraer la categoría")
            continue"""

        """for _ in range(3):
            try:
                sub_category = sub_category.xpath('.//h1/text()').get().strip()
                return category
            except AttributeError:
                time.sleep(5)
            continue"""

        category = category.xpath('.//li[contains(@class, "breadcrumb__item")][2]/a/text()').get().strip()
        sub_category = sub_category.xpath('.//h1/text()').get().strip()

        print(category)
        print(sub_category)

        def format_category(category):
            categories_and_results = {
                "licores": "Licores",
                "bebidas": "Bebidas",
            }

            formatCategory = category.lower()

            for category_key, category_value in categories_and_results.items():
                pattern = rf"\b{category_key}\b"
                if re.search(pattern, formatCategory):
                    return category_value
            return None

        def format_sub_category(sub_category):
            sub_categories_and_results = {
                "rones": "Rones",
                "cerveza": "Cervezas",
                "vodka": "Vodkas",
                "vino": "Vinos y Espumantes",
                "espumantes": "Vinos y Espumantes",
                "whisky": "Whisky",
                "aperitivos y digestivos": "Digestivos",
                "refrescos": "Refrescos",
                "jugos": "Jugos",
                "agua": "Agua",
                "bebidas listas": "Bebidas Listas",
                "té e infusiones": "Té e Infusiones",
            }

            formatCategory = sub_category.lower()

            for category_key, category_value in sub_categories_and_results.items():
                pattern = rf"\b{category_key}\b"
                if re.search(pattern, formatCategory):
                    return category_value
            return None
        
        categoryResult = format_category(category)
        
        subCategoryResult = format_sub_category(sub_category)

        if subCategoryResult and categoryResult:
            result = {
                'supermarket': 'Gama',
                'category': categoryResult,
                'sub_category': subCategoryResult,
                'products': product_list
            }
            yield result
        else:
            print("Categoría no encontrada")

def run_crawl(url):
    process = CrawlerProcess({
        'FEED_FORMAT': 'json',
        'FEED_URI': 'temp/datos_de_salida.json'
    })
    process.crawl(SeekerOneSpider, url=url)
    process.start()

@api_gama_blueprint.route('/api/gama', methods=['POST'])
def api():
    url = request.json['url']
    p = multiprocessing.Process(target=run_crawl, args=(url,))
    p.start()

    output_file = os.path.join('temp', 'datos_de_salida.json')
    max_wait_time = 600  # Ajusta el tiempo de espera según sea necesario
    start_time = time.time()
    while not os.path.exists(output_file) and time.time() - start_time < max_wait_time:
        time.sleep(1)

    # Leer el archivo y devolver los datos
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            scraped_data = json.load(f)
            document = {'data': scraped_data}
            result = collection.insert_one(document)
            print(result.inserted_id)
        os.remove(output_file)
        return jsonify({'data': scraped_data})
    else:
        os.remove(output_file)
        return jsonify({'error': 'El archivo no fue generado a tiempo.'})

