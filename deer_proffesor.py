"""
This is a echo bot.
It echoes any incoming text messages.
"""

import logging

from aiogram import Bot, Dispatcher, executor, types, exceptions
import logging
import asyncio
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import List
import json
import os
from utils import transform_orders
import pytz
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('broadcast')
configs = json.load(open('config.json'))
API_TOKEN = configs['AUTHORIZATION_TOKEN']
ORDERS = os.getenv('ORDERS', 'ordersexample.json')
BATTLES = os.getenv('BATTLES', 'battles.json')
battles = json.load(open(BATTLES))
# Configure logging
logging.basicConfig(level=logging.INFO)

# loop = asyncio.get_event_loop()
loop = asyncio.new_event_loop()

messages_tasks: List[asyncio.Task] = []

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN, loop=loop)
dp = Dispatcher(bot, loop=loop)


@dp.message_handler(regexp='(^cat[s]?$|puss)')
async def cats(message: types.Message):
    with open('data/cats.jpg', 'rb') as photo:
        await bot.send_photo(message.chat.id, photo, caption='Cats is here 😺',
                             reply_to_message_id=message.message_id)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await bot.send_message(message.chat.id, 'Loren es gay')


@dp.message_handler(commands=['reset_orders'])
async def reset_orders(message: types.Message):
    orders = json.load(open(ORDERS))
    ans = await _reset_orders(transform_orders(orders))
    await bot.send_message(message.chat.id, str(ans))


async def _reset_orders(orders):
    global messages_tasks, battles
    times = []
    now = datetime.now(timezone.utc)
    for battle in battles:
        hour, minutes = map(int, battle.split(':'))
        t = datetime(now.year, now.month, now.day, hour, minutes, tzinfo=timezone.utc)
        if now > t:
            t += timedelta(days=1)

        times.append(t)

    next_battle = min(times)
    log.info(f'Next Battle: {next_battle}')

    for task in messages_tasks:
        task: asyncio.Task = task
        if not task.done():
            task.cancel()
    messages_tasks.clear()

    for order in orders:
        for id in order['publish']:
            time = next_battle - timedelta(seconds=order['time'])
            # _send because clousure is a bitch
            # log.info(f'Timeout {order["time"]}')
            task = loop.create_task(
                exec_at(time,  _send(id, order['msg'])))
            messages_tasks.append(task)

    task = loop.create_task(exec_at(next_battle, lambda : _reset_orders(orders)))
    messages_tasks.append(task)
    return orders


def _send(id, msg):
    return lambda :send_message(id, msg)


@dp.message_handler(commands=['ping'])
async def pong(message: types.Message):
    log.info(message.chat.id)
    await bot.send_message(message.chat.id, 'ping pong es muñeco muy lindo y de cartón ...')


async def send_message(user_id: int, text: str, disable_notification: bool = False) -> bool:
    """
    Safe messages sender

    :param user_id:
    :param text:
    :param disable_notification:
    :return:
    """

    msg = None
    try:
        msg: types.Message = await bot.send_message(user_id, text, disable_notification=disable_notification)
    except exceptions.BotBlocked:
        log.error(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.ChatNotFound:
        log.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        log.error(
            f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return await send_message(user_id, text)  # Recursive call
    except exceptions.UserDeactivated:
        log.error(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramAPIError:
        log.exception(f"Target [ID:{user_id}]: failed")
    else:
        log.info(f"Target [ID:{user_id}]: success")
        chat: types.Chat = await bot.get_chat(user_id)
        log.info(f'Chat {chat}')
        log.info(f'MSG {msg}')
        log.info(f'MSGID {msg["message_id"]}')
        id = msg["message_id"]
        log.info(f'{chat} {id}')
        sucess = await bot.pin_chat_message(chat['id'], id)
        # sucess = await chat.pin_message(msg['message_id'])
        log.info(f'Sucess {sucess}')

        return True
    return False


async def do_delay(timeout: float, func):
    log.info(f'await start  {timeout}, {type(timeout)})')
    await asyncio.sleep(timeout, loop=loop)
    log.info(f'await finish {timeout}')

    await func()


async def exec_at(moment: datetime, func):
    assert moment > datetime.now(timezone.utc), "The moment has to be begger than now"
    now = datetime.now(timezone.utc)
    timelapse = moment - now

    await do_delay(timelapse.total_seconds(), func)


if __name__ == '__main__':
    # loop.create_task()
    loop.create_task(_reset_orders(transform_orders(json.load((open(ORDERS))))))
    executor.start_polling(dp, loop=loop, skip_updates=True)
