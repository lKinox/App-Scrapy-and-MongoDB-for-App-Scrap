from flask import Flask, request, jsonify, Blueprint, json
from json import JSONDecodeError, JSONDecoder
import multiprocessing
from scrapy.spiders import Spider
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from scrapy import Request
from pymongo import MongoClient
import os
import time
import re

api_plazas_blueprint = Blueprint('api_plazas', __name__)


client = MongoClient("mongodb+srv://reyanjimenez:mjWiDjrreHl66MuY@consultor-api-db.tqpkb.mongodb.net/?retryWrites=true&w=majority&appName=consultor-api-db")
db = client["test"]
collection = db["plazas"]

class SeekerOneSpider(Spider):
    name = 'seeker_one'
    start_urls = []

    def __init__(self, url):
        self.start_urls = [url]

    def parse(self, response):
        sel = Selector(response)
        time.sleep(2)
        category = sel.xpath('//div[contains(@class, "breadcrumb")]')
        sub_category = sel.xpath('//span[contains(@class, "filter-value")]')
        products = sel.xpath('//div[contains(@class, "product-item-info")]')
        page_links = sel.xpath('//ul[contains(@class, "items pages-items")]/li[contains(@class, "pages-item-next")]/a/@href').getall()

        def extract_price(price_string):
                pattern = r'\d+(,\d+)?'
                match = re.search(pattern, price_string)
                if match:
                    return match.group()
                else:
                    return None

        product_list = []

        for page_url in page_links:
            yield Request(page_url, callback=self.parse)

        product_id = 1
        for product in products:
            price_string = product.xpath('.//div[contains(@class, "product-item-details")]/div/div/span/span/span[contains(@class, "price")]/text()').get().strip()
            price = extract_price(price_string)
            item = {
                'id': product_id,
                'title': product.xpath('.//div[contains(@class, "product-item-details")]/strong/a/text()').get().strip(),
                'price': price
            }
            product_list.append(item)
            product_id += 1 

        category = category.xpath('.//ul/li[contains(@class, "item")][2]/a/text()').get().strip() 

        sub_category = sub_category.xpath('.//text()').get().strip()

        def format_category(category):
            categories_and_results = {
                "licores": "Licores",
                "víveres": "Bebidas",
                "mascotas": "Mascotas",
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
                "cervezas": "Cervezas",
                "vodka": "Vodkas",
                "vinos y espumantes": "Vinos y Espumantes",
                "whisky": "Whisky",
                "licores dulces": "Digestivos",
                "jugos y nectares": "Jugos",
                "perros": "Perros",
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
                'supermarket': 'Plazas',
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

@api_plazas_blueprint.route('/api/plazas', methods=['POST'])
def api():
    url = request.json['url']
    p = multiprocessing.Process(target=run_crawl, args=(url,))
    p.start()

    output_file = os.path.join('temp', 'datos_de_salida.json')
    max_wait_time = 1000  # Ajusta el tiempo de espera según sea necesario
    start_time = time.time()
    while not os.path.exists(output_file) and time.time() - start_time < max_wait_time:
        time.sleep(1)

    print(os.path.exists(output_file))
    time.sleep(20)

    # Leer el archivo y devolver los datos
    if os.path.exists(output_file):
        all_data = []
        with open(output_file, 'r') as f:
            all_data = json.loads(f.read()) 

            print(all_data)

        def combine_products(product_data):
            all_products = []
            for data in product_data:
                all_products.extend(data['products'])
            return all_products
        
        combined_products = combine_products(all_data)

        result = [{'supermarket': all_data[0]['supermarket'], 
                    'category': all_data[0]['category'], 
                    'sub_category': all_data[0]['sub_category'], 
                    'products': combined_products
        }]
        
        document = {'data': result}
        result = collection.insert_one(document)
        print(result.inserted_id)

        os.remove(output_file)
        return jsonify({'data': result})
    else:
        os.remove(output_file)
        return jsonify({'error': 'El archivo no fue generado a tiempo.'})