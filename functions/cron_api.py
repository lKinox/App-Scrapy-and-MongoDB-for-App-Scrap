from flask import Flask, Blueprint, jsonify
import requests

cron_blueprint = Blueprint('cron', __name__)

def send_data(url, api_url):
    data = {
        "url": url
    }
    response = requests.post(api_url, json = data)

    if response.status_code == 200:
        print(f'Solicitud exitosa para {url}:')
    else:
        print(response.raise_for_status())
        print(f'Error en la solicitud para {url}:', response.text)

urls_gama = [
    #Licores #Cervezas
    "https://gamaenlinea.com/es/cerveza/c/A0408?pageSize=100",
    #Licores #Rones
    "https://gamaenlinea.com/es/rones/c/A0403?pageSize=100",
    #Licores #Vodkas
    "https://gamaenlinea.com/es/vodka/c/A0404?pageSize=100",
    #Licores #Vinos y Espumantes
    "https://gamaenlinea.com/es/vino/c/A0407?pageSize=100",
    #Licores #Vinos y Espumantes
    "https://gamaenlinea.com/es/espumantes/c/A0401?pageSize=100",
    #Licores #Whisky
    "https://gamaenlinea.com/es/whisky/c/A0402?pageSize=100",
    #Licores #Digestivos
    "https://gamaenlinea.com/es/aperitivos-digestivos/c/A0409?pageSize=100",
    #Bebidas #Refrescos
    "https://gamaenlinea.com/es/refrescos/c/A050401?pageSize=100",
    #Bebidas #Jugos
    "https://gamaenlinea.com/es/jugos/c/A0503?pageSize=100",
    #Bebidas #Agua
    "https://gamaenlinea.com/es/bebidas/agua/c/A0501?pageSize=100",
    #Bebidas #Bebidas listas
    "https://gamaenlinea.com/es/bebidas-listas/c/A0506?pageSize=100",
    #Bebidas #Té e infuciones
    "https://gamaenlinea.com/es/bebidas/te-e-infusiones/c/A0502?pageSize=100",
]

urls_plazas = [
    #Licores Rones
    "https://vallearriba.elplazas.com/licores.html?_=&cat=1176",
    #Licores Cervezas
    "https://vallearriba.elplazas.com/licores.html?_=&cat=1186",
    #Licores Vodkas
    "https://vallearriba.elplazas.com/licores.html?_=&cat=1183",
    #Licores #Whisky
    "https://vallearriba.elplazas.com/licores.html?_=&cat=1168",
    #Licores Vinos y Espumantes
    "https://vallearriba.elplazas.com/licores.html?_=&cat=1191",
    #Licores Aperitivos y Digestivos
    "https://vallearriba.elplazas.com/licores.html?_=&cat=1200",
    #Bebidas Refrescos
    "https://vallearriba.elplazas.com/viveres/bebidas.html?_=&cat=1511",
    #Bebidas Jugos,
    "https://vallearriba.elplazas.com/viveres/bebidas/jugos.html"
    #Mascotas
    "https://vallearriba.elplazas.com/mascotas.html?cat=1210"
]

@cron_blueprint.route('/cron', methods=['GET'])
def cron_api():
    for url in urls_gama:
        api_url = 'http://127.0.0.1:5000/api/gama'
        send_data(url, api_url)
    for url in urls_plazas:
        api_url = 'http://127.0.0.1:5000/api/plazas'
        send_data(url, api_url)
    return jsonify({'message': 'Cron job ejecutado exitosamente', 'status': 'success'}), 200
