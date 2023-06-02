from storages.backends.s3boto3 import S3ManifestStaticStorage


class StaticStorage(S3ManifestStaticStorage):
    bucket_name = 'splashcat-static'
    custom_domain = 'static.splashcat.ink'
