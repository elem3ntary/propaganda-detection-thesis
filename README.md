# Cyrillic text classification using semantic capabilities of LLM Embeddings: A propaganda detection use case

## Accessing the dataset and the model
Files related to the dataset and the model are stored in the Google Drive folder. One can conveniently access it by [this](https://drive.google.com/drive/folders/1r6lWltzvTpUrcjS1Hr_iP4A3V0eCDeU1?usp=sharing) link. To download files using the terminal `gdown` utility can be used. The description of the files is provided below:
- `dataset.csv`: full dataset containing 0.8M messages. We will further refer to it as **the original dataset**
- `100k_en_sample_dataset.csv`: sampled 0.1M messages with `text_en` column featuring the English translation of the text message
- `language_invesrsed_dataset.csv`: the original `dataset.csv` has a language imbalance (propagandistic messages are mostly written in russiand and non-propagandistic in Ukrainian). This file contains messages **not present** in the `dataset.csv`. It features non-propagandistic russian-language messages. Thus can be conveniently used to check if model overfits.
- `story_dataset.csv` contains messages that were used in Section 5.1 to check performance on the data. Included messages (and channel) are not present in the original dataset.
- `model.pkl` architecture and weightes of the model used in Results Chapter. 

### Dowloading data via CLI
```bash
pip install gdown
gdown <file_id>
```
List of file ids of the presented content:
- `dataset.csv`: `1OTOWUm79a6Mux8oykazsPyKbeJqjxex3`
- `100k_en_sample_dataset.csv`: `1vKcfFh6yhkx0vy2XYHDNVz1fus1JqiGO`
- `language_inversed_dataset.csv`: `11xDwwe32f3D_yudYhZwVV5EnMvHfGDWi`
- `story_dataset.csv`: `1CJhXq8PoKxmQY39gcQCeel32XCmCnfrq`
- `model.pkl`: `1zKfDp9kmmNdfs2-zxSo80cit1p2QncrI`


## Telegram Parser Application
The Telegram Parser Applications leverages the `telethon` library that is a wrapper for Telegram API in Python. One can  quickly parse a Telegram Channel using it.

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