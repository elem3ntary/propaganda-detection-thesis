'''
Use this file if you want to preauthenticate telegram account
so that anon.session file will be saved
'''
from . import config

from telethon import TelegramClient

client = TelegramClient('anon', config.TG_API_ID, config.TG_API_HASH)


async def get_me():
    me = await client.get_me()
    print(me.stringify())


if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(get_me())
