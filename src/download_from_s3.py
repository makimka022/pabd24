"""Upload selected files to S3 storage"""
import argparse

from dotenv import dotenv_values
import boto3

BUCKET_NAME = 'pabd24'
YOUR_ID = '26'
CSV_PATH = ['data/raw/1_2024-05-19_19-28.csv',
            'data/raw/2_2024-05-19_19-29.csv',
            'data/raw/3_2024-05-19_19-29.csv']

config = dotenv_values(".env")
client = boto3.client(
    's3',
    endpoint_url='https://storage.yandexcloud.net',
    aws_access_key_id=config['KEY'],
    aws_secret_access_key=config['SECRET']
)


def main(args):
    for csv_path in args.input:
        remote_name = f'{YOUR_ID}/' + csv_path.replace('\\', '/')
        client.download_file(BUCKET_NAME, remote_name, csv_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', nargs='+',
                        help='Remote data files to download from S3 storage',
                        default=CSV_PATH)
    args = parser.parse_args()
    main(args)
