"""
This is a echo bot.
It echoes any incoming text messages.
"""
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
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


# Configure logging
logging.basicConfig(level=logging.INFO)
configs = json.load(open('info.json'))
API_TOKEN = configs['token']

loop = asyncio.get_event_loop()
bot = Bot(token=API_TOKEN, loop=loop)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

castles = {
    "deer": "🦌",
    "shark": "🦈",
    "dragon": "🐉",
    "moon": "🌑",
    "wolf": "🐺",
    "potato": "🥔",
    "eagle": "🦅"
}


class Form(StatesGroup):
    me = State()  # Will be represented in storage as 'Form:name'
    pledge = State()  # Will be represented in storage as 'Form:age'
    badpledge = State()  # Will be represented in storage as 'Form:gender'


@dp.message_handler(commands=['start'], commands_prefix='/')
async def send_welcome(message: types.Message):
    """
    This handler will be called when client send `/start` command.
    """
    await Form.me.set()
    await bot.send_message(message.chat.id, "Welcome, young fawn. I'm the Deer Professor, manager of the Acadeermy. \n Please go to @chtwrsbot and type /me and forward it to me so we can continue with the admission process...")


@dp.message_handler(state=Form.me)
async def process_me(message: types.Message, state: FSMContext):
    """
    Process user's me
    """
    if message.forward_from == None or not message.forward_from['id'] == 408101137:
        await bot.send_message(message.chat.id, "It looks like you just copied your /me and didn't forward it from @chtwrsbot. \nHow do I know that you didn't make that up? ")

    elif 'of deerhorn castle' in message.text.lower():
        async with state.proxy() as data:
            data['me'] = message.text
        await Form.next()
        await bot.send_message(message.chat.id, "Great, now send your pledge")

    else:
        await bot.send_message(message.chat.id, "It looks like you're not a warrior from Deerhorn Castle, buh bye")


# Check age. Age gotta be digit
@dp.message_handler(state=Form.pledge)
async def process_pledge(message: types.Message):
    """
    Process user's pledge
    """

    if message.forward_from == None or not message.forward_from['id'] == 408101137:
        print('copied or not forwarded')
        await bot.send_message(message.chat.id, "It looks like you just copied your pledge and didn't forward it from @chtwrsbot. \nHow do I know that you didn't make that up? Please forward it now.")
    
    elif 'you were invited by the knight of the' and 'deerhorn castle' in message.text.lower():
        # await state.update_data(pledge = message.text)
        print('good')
        await bot.send_message(message.chat.id, "Fabulous, you were invited by a fellow deer, you're good to go")
        return await bot.send_message(message.chat.id, "You can join the Acadeermy using this link t.me/commandbottest")

    else:
        print('bad pledge')
        # await Form.badpledge.set()
        # markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        # markup.add("@larrygf", "@hiancd")
        # markup.add("@scarlettV","@cptspooks")
        await bot.send_message(message.chat.id, "Hmmm, it looks like you were invited by a knight from another castle \nI'll put you in contact with our human teachers, feel free to PM (Private Message) them and they'll finish processing your admission.")
        return await bot.send_message(message.chat.id, 'This is the list of available teachers: \n@larrygf \n@hiancd \n@scarlettV \n@cptspooks')
        




# @dp.message_handler(state=Form.badpledge)
# async def bad_pledge(message: types.Message):
#     # Update state and data
#     await Form.next()
#     # await state.update_data(age=int(message.text))

#     # Configure ReplyKeyboardMarkup
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
#     markup.add("Male", "Female")
#     markup.add("Other")

#     await message.reply("What is your gender?", reply_markup=markup)




# @dp.message_handler(state=Form.gender)
# async def process_gender(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['gender'] = message.text

#         # Remove keyboard
#         markup = types.ReplyKeyboardRemove()

#         # And send message
#         await bot.send_message(message.chat.id, md.text(
#             md.text('Hi! Nice to meet you,', md.bold(data['name'])),
#             md.text('Age:', data['age']),
#             md.text('Gender:', data['gender']),
#             sep='\n'), reply_markup=markup, parse_mode=ParseMode.MARKDOWN)

#         # Finish conversation
#         data.state = None


if __name__ == '__main__':
    executor.start_polling(dp, loop=loop, skip_updates=True)
