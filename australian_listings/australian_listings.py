
import sys
import io
import pandas as pd 
import requests
import base64
import boto3
from datetime import datetime

from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
client_id = "client_0b205b5e26b46b96c3d81cc0aeb71cd3"
client_secret = "secret_d89b759bd6e47de21d7c064a4f307657"

def encode_credentials(): 
    client_credentials = f"{client_id}:{client_secret}"
    client_credentials_b64 = base64.b64encode(client_credentials.encode())
    return client_credentials_b64.decode()

def get_token():
    url = 'https://auth.domain.com.au/v1/connect/token'
    headers = {
    'Authorization': f'Basic {encode_credentials()}'
    }
    data = {
    'grant_type': 'client_credentials',
    'scope': 'api_listings_read api_salesresults_read'
    }
    r = requests.post(url, headers=headers, data=data)
    return r.json()['access_token']

def get_listings(city:str):
    url = f'https://api.domain.com.au/v1/salesResults/{city}/listings'

    headers = {
        'Authorization': f'Bearer {get_token()}'
    }
    response = requests.get(url, headers=headers)
    return response

def response_to_csv(response:str):
    return pd.read_json(io.StringIO(response.text))

cities = ["Melbourne", "Sydney", "Canberra", "Adelaide", "Brisbane"]

df = pd.concat([response_to_csv(get_listings(city)) for city  in cities])
# Drop duplicates
df = df.drop_duplicates(subset='id')

# Unpack GeoLocation
df[['latitude', 'longitude']] = pd.json_normalize(df['geoLocation'])
df = df.drop(columns='geoLocation')
year = datetime.now().year
month = datetime.now().month
date = datetime.now().strftime('%Y-%m-%d')

bucket_name = 'knedliky-bronze'
object_key = f'domain/{year}/{month}/australian_house_prices_{date}.csv'

# buffer = io.BytesIO()
# df.to_csv(buffer, index=False)
# bytes = buffer.getvalue().encode('utf8')
csv = df.to_csv(index=False)
bytes = csv.encode()

s3 = boto3.client('s3')
s3.put_object(Bucket=bucket_name, Key=object_key, Body=bytes)
bytes
job.commit()