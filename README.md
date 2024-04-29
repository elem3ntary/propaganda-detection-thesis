# Telegram Parser Application

## Installation
First install all the required dependencies
```bash
pip install -r requirements.txt
```

Then create an .env file with the following variables
```text
TG_API_ID=
TG_API_HASH=
```
After that generate your session credential by executing telegram_login.py
```bash
python3 -m telegram_parser.telegram_login.main
```

Well done! Now you can execute the parser. It features the following documentation

```text
usage: main.py [-h] [-c CHANNEL] [-n NAME] [-s SHEET] [-p PARSE]

Fetches messages from provided Telegram Channels

options:
  -h, --help            show this help message and exit
  -c CHANNEL, --channel CHANNEL
                        specify channel link to parse
  -n NAME, --name NAME  specify channel to parse
  -s SHEET, --sheet SHEET
                        share link from google sheets
  -p PARSE, --parse PARSE
                        the name of the parse session
```

E.g.
```bash
python3 -m telegram_parser.main -c https://t.me/lachentyt -n Lachentyt
```