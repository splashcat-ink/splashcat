<h1 align='center'>
<img src="https://raw.githubusercontent.com/splashcat-ink/splashcat/refs/heads/main/static/images/judd-pride.png" width="150">
Splashcat
</h1>

[Splashcat](http://splashcat.ink "Splashcat") is an award-winning service to track Splatoon 3 battles. Built upon Django, HTMX, _hyperscript, and Tailwind.CSS.

##How to contribute
Thank you for taking the time to contribute to Splashcat! We appreciate your help. There are multiple ways you can help:
- [Getting Started](#getting-started)
- [Contributing to the codebase](#contributing)
- [Reporting bugs](#reporting-bugs)
- [Donating](https://github.com/sponsors/catgirlinspace)

## Getting Started
Required Dependencies: [Python](https://www.python.org/downloads/ "Python"), [Poetry](http://python-poetry.org/docs "Poetry") & [NPM](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm "NPM")
1. Fork the repository.
2. Clone the repo:
    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    ```
3.  cd into the directory:
```bash
    cd *file path*
    ```
4. Install dependencies:
    ```bash
	poetry install
	npm install
	npx update-browserslist-db@latest
	npm run build
    ```
5. Run the website:
	macOS/Linux:
```bash
poetry shell
./manage.py runserver
```
Windows:
```bash
poetry shell
python manage.py runserver
```

## Contributing to the codebase
1. **Create a branch** for your feature or fix:
    ```bash
    git checkout -b myfeature
    ```
2. **Commit your changes**:
    ```bash
    git commit -m "Description of the change"
    ```
3. **Push** to the branch:
    ```bash
    git push origin myfeature
    ```
4. **Submit a pull request**.

## Reporting Bugs
If you've found a bug in Splashcat please [report it! ](https://github.com/splashcat-ink/splashcat/issues/new "report it! ")
If it's a security vulnerability please contact splashcat@rosalina.saige.ink or use GitHub's tools for reporting security issues. Do **not** use a public GitHub issue.

## Donating
Sponsoring me will support Splashcat and its server costs. Getting $5+ monthly tier also gives you some little additional features in Splashcat! For more details, see [here](https://splashcat.ink/sponsor/ "here") and to donate click [here](https://github.com/sponsors/catgirlinspace "here")!

##Contact
Want to get in touch with us you can join the Discord server [here!](https://discord.gg/JPFwvbSWMS "here!") 

## License
Splashcat is licensed under the terms of the [AGPL-3.0 license ](https://github.com/splashcat-ink/splashcat/blob/main/LICENSE "AGPL-3.0 license ")

