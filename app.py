from flask import Flask, jsonify
from routes.api_gama import api_gama_blueprint
from routes.api_plazas import api_plazas_blueprint
from functions.cron_api import cron_blueprint
from testdb.dbtest import test_db_blueprint

app = Flask(__name__)

app.register_blueprint(api_gama_blueprint)
app.register_blueprint(api_plazas_blueprint)
app.register_blueprint(cron_blueprint)
app.register_blueprint(test_db_blueprint)




if __name__ == '__main__':
    app.run(debug=True)