import base64

import requests
from django.core.management import BaseCommand

from splatnet_assets.models import Challenge, LocalizationString

locale_json_url = dict(
    string_de_de='https://splatoon3.ink/data/locale/de-DE.json',
    string_en_gb='https://splatoon3.ink/data/locale/en-GB.json',
    string_en_us='https://splatoon3.ink/data/locale/en-US.json',
    string_es_es='https://splatoon3.ink/data/locale/es-ES.json',
    string_es_mx='https://splatoon3.ink/data/locale/es-MX.json',
    string_fr_ca='https://splatoon3.ink/data/locale/fr-CA.json',
    string_fr_fr='https://splatoon3.ink/data/locale/fr-FR.json',
    string_it_it='https://splatoon3.ink/data/locale/it-IT.json',
    string_ja_jp='https://splatoon3.ink/data/locale/ja-JP.json',
    string_ko_kr='https://splatoon3.ink/data/locale/ko-KR.json',
    string_nl_nl='https://splatoon3.ink/data/locale/nl-NL.json',
    string_ru_ru='https://splatoon3.ink/data/locale/ru-RU.json',
    string_zh_cn='https://splatoon3.ink/data/locale/zh-CN.json',
    string_zh_tw='https://splatoon3.ink/data/locale/zh-TW.json',
)


class Command(BaseCommand):
    help = 'Scrapes data from https://github.com/Leanny/leanny.github.io/tree/master/splat3/data/language and stores ' \
           'in the database.'

    def handle(self, *args, **options):
        locales = {}

        for locale, url in locale_json_url.items():
            locales[locale] = requests.get(url).json()

        for challenge_id, challenge_data in locales['string_en_us']['events'].items():
            challenge_real_id = base64.b64decode(challenge_id).decode('utf-8').split('-')[1]

            localized_names = {}
            localized_descriptions = {}
            localized_long_descriptions = {}
            for locale, locale_data in locales.items():
                localized_names[locale] = locale_data['events'][challenge_id]['name']
                localized_descriptions[locale] = locale_data['events'][challenge_id]['desc']
                localized_long_descriptions[locale] = locale_data['events'][challenge_id]['regulation']

            name, _ = LocalizationString.objects.update_or_create(
                internal_id=challenge_id,
                type=LocalizationString.Type.CHALLENGE_NAME,
                defaults=localized_names,
            )

            description, _ = LocalizationString.objects.update_or_create(
                internal_id=challenge_id,
                type=LocalizationString.Type.CHALLENGE_DESCRIPTION,
                defaults=localized_descriptions,
            )

            long_description, _ = LocalizationString.objects.update_or_create(
                internal_id=challenge_id,
                type=LocalizationString.Type.CHALLENGE_LONG_DESCRIPTION,
                defaults=localized_long_descriptions,
            )

            challenge, _ = Challenge.objects.update_or_create(
                internal_id=challenge_real_id,
                defaults={
                    'name': name,
                    'description': description,
                    'long_description': long_description,
                }
            )
