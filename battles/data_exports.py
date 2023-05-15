import base64
import hashlib
from datetime import timedelta, datetime
from urllib.parse import parse_qs, urlsplit, urlunsplit, urlencode, urljoin

from django.conf import settings

from battles.tasks import get_boto3_client


def get_last_modified(obj):
    return int(obj['LastModified'].strftime('%s'))


def get_latest_export_download_url():
    boto3 = get_boto3_client()
    objs = boto3.list_objects_v2(Bucket='splashcat-data-exports', Prefix='global/')['Contents']
    last_added = [obj['Key'] for obj in sorted(objs, key=get_last_modified)][0]

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
