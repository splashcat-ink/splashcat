import requests
from django.core.management import BaseCommand

from splatnet_assets.models import TitleAdjective, LocalizationString, TitleSubject

prefix = 'https://gitlab.com/AeonSake/splat3-data/-/raw/master/MSBT/JSON_merged/CommonMsg/Byname'
adjectives = f'{prefix}/BynameAdjective.msbt.json'
subjects = f'{prefix}/BynameSubject.msbt.json'

locale_to_localization_string_property = {
    "CNzh": "string_zh_cn",
    "EUde": "string_de_de",
    "EUen": "string_en_gb",
    "EUes": "string_es_es",
    "EUfr": "string_fr_fr",
    "EUit": "string_it_it",
    "EUnl": "string_nl_nl",
    "EUru": "string_ru_ru",
    "JPja": "string_ja_jp",
    "KRko": "string_ko_kr",
    "TWzh": "string_zh_tw",
    "USen": "string_en_us",
    "USes": "string_es_mx",
    "USfr": "string_fr_ca",
}


def process_data(data, localization_type, model):
    for title_part in data:
        string_data = {}

        for language, string in title_part['locale'].items():
            string_data[locale_to_localization_string_property[language]] = string

        localization_string, _ = LocalizationString.objects.update_or_create(
            internal_id=title_part['label'],
            type=localization_type,
            defaults=string_data
        )

        model.objects.update_or_create(
            internal_id=title_part['label'],
            defaults={
                'string': localization_string
            }
        )


class Command(BaseCommand):
    def handle(self, *args, **options):
        adjective_data = requests.get(adjectives).json()
        subject_data = requests.get(subjects).json()

        process_data(adjective_data, LocalizationString.Type.TITLE_ADJECTIVE, TitleAdjective)
        process_data(subject_data, LocalizationString.Type.TITLE_SUBJECT, TitleSubject)
