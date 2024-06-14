"""House price prediction service"""
import os
from dotenv import dotenv_values
from flask import Flask, request, url_for
from flask_cors import CORS
from joblib import load
from flask_httpauth import HTTPTokenAuth
from flask import send_from_directory
import numpy as np
from geopy.geocoders import Nominatim
import geopy.distance
geolocator = Nominatim(user_agent="Tester")
from utils import predict_io_bounded, predict_cpu_bounded, predict_cpu_multithread

MODEL_SAVE_PATH = 'models/lin_reg_ff_v1.joblib'

app = Flask(__name__)
CORS(app)

config = dotenv_values(".env")
auth = HTTPTokenAuth(scheme='Bearer')

tokens = {
    config['APP_TOKEN']: "user1",
}

model = load(MODEL_SAVE_PATH)


@auth.verify_token
def verify_token(token):
    if token in tokens:
        return tokens[token]

def calculate_distance(loc1, loc2):
    location1 = geolocator.geocode(loc1)
    location2 = geolocator.geocode(loc2)
    try:    
       coords_1 = (location1.latitude, location1.longitude)
       coords_2 = (location2.latitude, location2.longitude)
       return geopy.distance.geodesic(coords_1, coords_2).km
    except:
        np.nan

def predict(in_data: dict) -> int:
    """ Predict house price from input data parameters.
    :param in_data: house parameters.
    :raise Error: If something goes wrong.
    :return: House price, RUB.
    :rtype: int
    """
    area = float(in_data['area'])
    floor = int(in_data['floor'])
    floors_count = int(in_data['floors_count'])
    is_first = (floor == 1)
    is_last = (floor == floors_count)
    rooms_count = int(in_data['rooms_count'])
    address_flat = "Москва, " + in_data['district'] + ', ' + in_data['street'] + ', ' + in_data['house_number']
    distance_center = calculate_distance(address_flat, 'Москва, Красная Площадь, 1')
    price = model.predict([[area,
                            is_first,
                            is_last,
                            floors_count,
                            rooms_count,
                            distance_center]])
    return int(price)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/")
def home():
    return """
    <html>
    <head>
    <link rel="shortcut icon" href="/favicon.ico">
    </head>
    <body>
    <h1>Housing price service.</h1> Use /predict endpoint
    </body>
    </html>
    """


@app.route("/predict", methods=['POST'])
@auth.login_required
def predict_web_serve():
    """Dummy service"""
    in_data = request.get_json()
    price = predict(in_data)
    return {'price': price}


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)