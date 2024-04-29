import pandas as pd
import logging
import datetime
import time
import os
import argparse

from tqdm.asyncio import tqdm
from typing import Any, Tuple
from telethon import TelegramClient
from . import config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('app')


async def get_channel_messages_df(client, entity_like, limit: int = None,
                                  start_date: datetime.datetime = None,
                                  stop_date: datetime.datetime = None) \
        -> pd.DataFrame:
    """Returns a DataFrame with the messages from the channel

    Returns:
        pd.DataFrame: a DataFrame parsed messages: 'id', 'raw_text', 'views', 'date'
    """
    if start_date is not None and stop_date is not None:
        assert stop_date > start_date, 'stop_date should be bigger than start_date'
    message_list = []
    counter = 0
    iterable = tqdm(client.iter_messages(entity_like, limit=limit))
    try:
        async for message in iterable:

            if stop_date is not None and message.date > stop_date:
                continue
            if start_date is not None and message.date < start_date:
                break

            message_list.append({
                'id': message.id,
                'raw_text': message.raw_text,
                'views': message.views,
                'date': message.date
            })
            counter += 1
            iterable.set_description(f"Number of messages processed is {counter}")
    except Exception:
        logger.info(f'The current parsed count is {counter}')
        logger.error('Cannot find an entity')
    return pd.DataFrame(message_list)


async def get_channel_id_by_channel_link(channel_link: str) -> int:
    """Fetches a channel id by the link

    Args:
        channel_link (str): channel link e.g. https://t.me/somechannel

    Returns:
        int: channel id
    """
    channel = await client.get(channel_link)
    return channel.id


def get_sheet_export_url(sheet_share_url: str) -> str:
    """Transforms Google Sheet Share Url to the one from which a data could
    be fetched

    Args:
        sheet_share_url (str): Google Sheet Share Link

    Returns:
        str: the link that can be used to plug in into pd.read_csv()
    """
    return '/'.join(sheet_share_url.split('/')[:-1]) + '/export?format=csv'


def get_telegram_channel_df_from_sheet(sheet_share_url: str) -> pd.DataFrame:
    """Given a Google Sheet Share Url returns a pd.DataFrame

    Args:
        sheet_share_url (str): Google Sheet Share Link

    Returns:
        pd.DataFrame: DataFrame that contains parsed sheet
    """
    sheet_export_url = get_sheet_export_url(sheet_share_url)
    return pd.read_csv(sheet_export_url)


def get_channel_name_logging_format(channel_name: str, channel_link: str) -> \
        str:
    """Defines format in which channel should be printed while logging

    Returns:
        str: formatted channel_name and channel_link
    """
    return f'{channel_name}: {channel_link}'


async def count_seconds_elapsed(callable) -> Tuple[Any, int]:
    """Executes the callable and returns a results with the number of seconds elapsed

    Args:
        callable (Callable): callable that execution time should be measured

    Returns:
        Tuple[Any, int]: A result of the function execution and seconds elapsed
    """
    start_time = time.time()
    result = await callable

    time_elapsed = time.time() - start_time

    return result, time_elapsed


async def fetch_channel_messages(client, channel_name: str,
                                 channel_link: str,
                                 start_date: datetime.datetime = None,
                                 stop_date: datetime.datetime = None) -> \
        pd.DataFrame:
    """Fetches messages from the specified channel and return a DataFrame

    Args:
        channel_link (str): Link to the channel from which messages should
        be fetched. Can be either public link or join-chat link
        channel_name (str): Channel name. 


        start_date (datetime.datetime, optional): If specified parses messages
        from start_date till now. Defaults to None.
        stop_date (datetime.datetime, optional): If specified parses messages
        from the time of creation till stop_date. Defaults to None.

    Returns:
        pd.DataFrame: DataFrame of messages from the channel. Note the order
        is DESC in the creation date (most recent messages first)
    """

    # Logging configuration
    channel_logging_name = get_channel_name_logging_format(channel_name,
                                                           channel_link)
    logger.info(f'{channel_logging_name}: Started parsing')

    messages_df, seconds_elapsed = await count_seconds_elapsed(
        get_channel_messages_df(client, channel_link,
                                start_date=start_date,
                                stop_date=stop_date))

    # Add info from which channel
    messages_df['channel'] = channel_link

    logger.info(
        f'{channel_logging_name}: Parsed {len(messages_df)} messages in \
{seconds_elapsed}')

    return messages_df


def get_temp_dir_path(temp_dir_name: str) -> str:
    """Returns temporary dir path. The dir woul be located under cwd

    Args:
        temp_dir_name (str): temp directory name

    Returns:
        str: path to the temporary directory
    """
    cwd = os.getcwd()
    temp_dir_path = os.path.join(cwd, temp_dir_name)

    return temp_dir_path


def get_current_parse_dir_path(temp_dir_path: str) -> str:
    """Returns path to the current parse directory

    Args:
        temp_dir_path (str): _description_

    Returns:
        str: path to the current parse directory
    """
    current_parse_name = datetime.datetime.now(
        tz=datetime.timezone.utc).strftime('channel-message_%H-%M-%S_UTC_%Y-%m-%d')
    current_parse_path = os.path.join(temp_dir_path, current_parse_name)
    os.makedirs(current_parse_path)
    return current_parse_path


def get_checkpoint_dir_path(current_parse_path: str) -> str:
    """Creates parse directory if does not exist and return path

    Args:
        current_parse_path (str): path of the curernt path

    Returns:
        str: path to the checkpoints directory
    """
    checkpoints_folder = os.path.join(current_parse_path, 'checkpoints')
    os.mkdir(checkpoints_folder)
    return checkpoints_folder


def get_channel_tag_from_link(link: str) -> str:
    """Get channel's tag from the link

    Args:
        link (str): channels link e.g. https://t.me/somechannel

    Returns:
        str: _description_
    """

    return link.rstrip('/').split('/')[-1]


def get_channel_checkpoint_path(checkpoints_dir_path: str, channel_tag: str) -> str:
    """Returns the checkpoint path of the channel

    Args:
        checkpoints_dir_path (str): path to the checkpoint dir of 
        some parsing session
        channel_tag (srt): channel tag like 'somechannel'

    Returns:
        srt: _description_
    """
    return os.path.join(
        checkpoints_dir_path, f'{channel_tag}.pkl')


async def fetch_messaged_from_channel_df(client, parse_name: str,
                                         many_channel_df: pd.DataFrame,
                                         checkpoint=None) -> pd.DataFrame:
    """Parse messages from the DataFrame of channel

    Args:
        many_channel_df (pd.DataFrame): Should contain columns 'Link' and 'Name'
        checkpoint (_type_, optional): Name of the parse from
        which to take messages. Defaults to None.

    Returns:
        pd.DataFrame: returns a DataFrame of messages parsed from many_channel_df
    """

    # Check if required df columns are present
    required_columns = ['Link', 'Name']
    assert len(set(required_columns) & set(many_channel_df)) == \
        len(required_columns), 'Link and Name columns are required.'

    # Create temp dir
    TEMP_DIR_NAME = 'telegram_channels_data'
    temp_dir_path = get_temp_dir_path(TEMP_DIR_NAME)

    # Create directory for the current parse
    parse_dir_path = get_current_parse_dir_path(temp_dir_path)
    logger.info(f'Results will be in {parse_dir_path} folder')
    current_checkpoints_dir_path = get_checkpoint_dir_path(parse_dir_path)

    # Define start and stop date parameters
    start_date = datetime.datetime(2022, 1, 1, tzinfo=datetime.timezone.utc)
    stop_date = datetime.datetime(2024, 2, 9, tzinfo=datetime.timezone.utc)

    messages_df = pd.DataFrame()
    rows = list(many_channel_df.iterrows())
    for idx, row in rows:
        channel_name = row['Name']
        channel_link = row['Link']
        channel_tag = get_channel_tag_from_link(channel_link)
        channel_checkpoint_path = get_channel_checkpoint_path(current_checkpoints_dir_path,
                                                              channel_tag)

        if checkpoint is None:
            channel_messages_df = await fetch_channel_messages(
                client,
                channel_name=channel_name,
                channel_link=channel_link,
                start_date=start_date,
                stop_date=stop_date
            )
        else:
            # Checkpoint is the name of the dir
            selected_checkpoint_dir_path = \
                os.path.join(temp_dir_path, checkpoint, 'checkpoints')
            channel_checkpot_pkl_path = get_channel_checkpoint_path(selected_checkpoint_dir_path,
                                                                    channel_tag)
            channel_messages_df = pd.read_pickle(channel_checkpot_pkl_path)
            logger.info(f'Data from {checkpoint} found for {channel_tag}.'
                        'Skipping fetching...')
        channel_messages_df.to_pickle(channel_checkpoint_path)

        logger.info(f'Processed {idx + 1} out of {len(rows)}')

        messages_df = pd.concat(
            [messages_df, channel_messages_df], axis=0)
    messages_df.to_csv(os.path.join(
        parse_dir_path, f'{parse_name}_dataset.csv'))
    return messages_df


async def main(client):
    parser = argparse.ArgumentParser(
        description='Fetches messages from provided Telegram Channels')
    parser.add_argument('-c', '--channel', help='specify channel link to parse')
    parser.add_argument('-n', '--name', help='specify channel to parse')
    parser.add_argument('-s', '--sheet', help='share link from google sheets')
    parser.add_argument('-p', '--parse', help='the name of the parse session')

    args = parser.parse_args()

    if args.sheet:
        channel_df = get_telegram_channel_df_from_sheet(args.sheet)
    elif args.channel or args.name:

        if not (args.channel and args.name):
            raise ValueError('Provide both -n and -c parameters')

        channel_df = pd.DataFrame([(args.name, args.channel)], columns=['Name', 'Link'])
    else:
        raise ValueError('Provide sheet link or name and channel link')

    checkpoint_name = None
    all_messages_df = await fetch_messaged_from_channel_df(client, args.parse, channel_df, checkpoint=checkpoint_name)

    logger.info(
        f'Finished parsing. Total amount of messages is {len(all_messages_df)}'
    )

# Setup Telegram Client
client = TelegramClient('anon', config.TG_API_ID, config.TG_API_HASH)
with client:
    client.loop.run_until_complete(main(client))
