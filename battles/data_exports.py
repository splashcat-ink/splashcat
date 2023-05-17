import base64
import hashlib
from datetime import timedelta, datetime
from urllib.parse import parse_qs, urlsplit, urlunsplit, urlencode, urljoin

import boto3
from django.conf import settings


def get_last_modified(obj):
    return int(obj['LastModified'].strftime('%s'))


def get_latest_export_download_url():
    b2_client = get_boto3_client()
    objs = b2_client.list_objects_v2(Bucket='splashcat-data-exports', Prefix='global/')['Contents']
    last_added = [obj['Key'] for obj in sorted(objs, key=get_last_modified)][-1]

    url = urljoin(f'https://{settings.BUNNY_NET_DATA_EXPORTS_CDN_HOST}', last_added)
    return sign_url(url, expiration_time=timedelta(days=1))


def sign_url(url, expiration_time: timedelta):
    expiry_time = int((datetime.now() + expiration_time).timestamp())
    scheme, netloc, path, query, fragment = urlsplit(url)
    parameters = parse_qs(query)

    security_token = settings.BUNNY_NET_DATA_EXPORTS_TOKEN

    raw_hash = f'{security_token}{path}{expiry_time}'
    token = base64.b64encode(hashlib.sha256(raw_hash.encode('utf-8')).digest()).decode('utf-8')
    token = token.replace('\n', '').replace('+', '-').replace('/', '_').replace('=', '')
    parameters['token'] = token
    parameters['expires'] = expiry_time
    query = urlencode(parameters, doseq=True)

    return urlunsplit((scheme, netloc, path, query, fragment))


def get_boto3_client():
    return boto3.client(
        service_name='s3',
        endpoint_url=settings.B2_ENDPOINT_URL,
        aws_access_key_id=settings.B2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.B2_SECRET_ACCESS_KEY,
    )
