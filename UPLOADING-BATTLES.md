## How to upload battles (For Development)
This guide is for uploading battles to splashcat in a local debug instance. The guide for uploading it to the production website is [here](https://splashcat.ink/uploaders-information/)

Ensure that you are running Splashcat in **debug** mode and at address `http:127.0.0.1:8000`
1.  Enter poetry shell
```bash
cd *splashcat directory*
poetry shell
```
2. Download the required SplatNet 3 assets (Note: This might take a long time if you have a slow internet connection and it is important you do it in the order below)
```bash
python manage.py updateall
```
3. Install [Deno](https://deno.land/) (if it isn't installed)

4. Upload battles to Splashcat
```bash
python manage.py runserver
deno run -Ar https://raw.githubusercontent.com/bentheminernz/s3si.ts-local-splashcat/main/s3si.ts -e splashcat
```

5. Follow the instuctions to setup s3si.ts and afterwards your battles should just upload to Splashcat!

### Manually Update SplatNet 3 assets
Use this if updateall isn't working or you want to update individual asset types.
```bash
./manage.py updatelocalizationstrings
./manage.py updategear
./manage.py updatesplashtags
./manage.py updatestages
./manage.py updateweapons
./manage.py updatetitles
./manage.py updateawards
./manage.py updatechallenges
./manage.py updatesplatfests
```