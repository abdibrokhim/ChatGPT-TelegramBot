# Installation

Go to .env file and change the following variables:

```
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
CHATGPT_API_KEY=your-chatgpt-api-key
```

## Requirements


```
pip install -r reqs.txt
```

```
source env/bin/activate
```

## Django
```
python3 manage.py migrate
```

```
python3 manage.py makemigrations
```

```
python3 manage.py createsuperuser
```

```
python3 manage.py runserver
```

## Telegram Bot

```
python3 bot.py
```

Go to your bot and check it.