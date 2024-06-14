"""Transform raw data to train / val datasets """
import argparse
import logging
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
import geopy.distance
geolocator = Nominatim(user_agent="Tester")

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename='log/preprocess_data.log',
    encoding='utf-8',
    level=logging.DEBUG,
    format='%(asctime)s %(message)s')


IN_FILES = ['data/raw/1_2024-05-19_19-28.csv',
            'data/raw/2_2024-05-19_19-29.csv',
            'data/raw/3_2024-05-19_19-29.csv']

OUT_TRAIN = 'data/proc/train.csv'
OUT_TEST = 'data/proc/test.csv'

TRAIN_SIZE = 0.9
PRICE_THRESHOLD = 30_000_000

def calculate_distance(loc1, loc2):
    location1 = geolocator.geocode(loc1)
    location2 = geolocator.geocode(loc2)
    try:    
       coords_1 = (location1.latitude, location1.longitude)
       coords_2 = (location2.latitude, location2.longitude)
       return geopy.distance.geodesic(coords_1, coords_2).km
    except:
        np.nan

def main(args):
    main_dataframe = pd.read_csv(args.input[0], delimiter=';')
    for i in range(1, len(args.input)):
        data = pd.read_csv(args.input[i], delimiter=';')
        df = pd.DataFrame(data)
        main_dataframe = pd.concat([main_dataframe, df], axis=0)

    main_dataframe['url_id'] = main_dataframe['url'].map(lambda x: x.split('/')[-2])

    df = main_dataframe

    df['district'].fillna('', inplace=True)

    df['first_floor'] = df['floor'] == 1
    df['last_floor'] = df['floor'] == df['floors_count']

    df['address_flat'] = "Москва, " + df['district'] + ', ' + df['street'] + ', ' + df['house_number']
    df['distance_center'] = df.apply(lambda row: calculate_distance(row['address_flat'], 'Москва, Красная Площадь, 1'), axis=1)

    new_dataframe = main_dataframe[['url_id',
                        'total_meters',
                        'first_floor',
                        'last_floor',
                        'floors_count',
                        'rooms_count',
                        'distance_center',
                        'price']].set_index('url_id')

    new_df = new_dataframe[new_dataframe['price'] < PRICE_THRESHOLD]

    border = int(args.split * len(new_df))
    train_df, val_df = new_df[0:border], new_df[border:-1]
    if args.split == 1:
        train_df.to_csv(OUT_TRAIN)
    elif args.split == 0:
        val_df.to_csv(OUT_TEST)
    elif 0 < args.split < 1:
        train_df.to_csv(OUT_TRAIN)
        val_df.to_csv(OUT_TEST)
    else:
        raise "Wrong split test size!"

    logger.info(f'Write {args.input} to train.csv and test.csv. Train set size: {args.split}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--split', type=float, 
                        help='Split data, test relative size, from 0 to 1',
                        default=TRAIN_SIZE)
    parser.add_argument('-i', '--input', nargs='+',
                        help='List of input files', 
                        default=IN_FILES)
    args = parser.parse_args()
    main(args)