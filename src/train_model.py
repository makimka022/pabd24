"""Train model and save checkpoint"""

import argparse
import logging
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from joblib import dump
import xgboost as xgb

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename='log/train_model.log',
    encoding='utf-8',
    level=logging.DEBUG,
    format='%(asctime)s %(message)s')

TRAIN_DATA = 'data/proc/train.csv'
VAL_DATA = 'data/proc/test.csv'
MODEL_SAVE_PATH = 'models/xgb_regression_v01.joblib'


def main(args):
    df_train = pd.read_csv(TRAIN_DATA)
    x_train = df_train[['total_meters',
                        'first_floor',
                        'last_floor',
                        'floors_count',
                        'rooms_count',
                        'distance_center'
                        ]]
    y_train = df_train['price']

    bxgb_model = xgb.XGBRegressor()
    bxgb_model.fit(x_train, y_train)
    dump(bxgb_model, args.model)
    logger.info(f'Saved to {args.model}')

    r2 = bxgb_model.score(x_train, y_train)

    logger.info(f'R2 = {r2:.3f}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model', 
                        help='Model save path',
                        default=MODEL_SAVE_PATH)
    args = parser.parse_args()
    main(args)