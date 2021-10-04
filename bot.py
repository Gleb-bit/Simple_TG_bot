import random

import config
import logging

from aiogram import Bot, Dispatcher, executor, types

from filters import IsAdminFilter

# log level
logging.basicConfig(level=logging.INFO)

# bot init
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

# activate filters
dp.filters_factory.bind(IsAdminFilter)


# bot's welcome message
@dp.message_handler(commands='start')
async def welcome(message: types.Message):
    with open('Telegram stickers/AnimatedSticker.tgs', 'rb') as sticker:
        await bot.send_sticker(message.chat.id, sticker)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('🤩 How are you?')
    button2 = types.KeyboardButton('🎲 Random number')

    markup.add(button1, button2)

    me = await bot.get_me()

    await message.answer(f'Welcome here, {message.from_user.username}, I am {me.first_name}',
                         parse_mode='html', reply_markup=markup)


# ban command (admins only!)
@dp.message_handler(is_admin=True, commands=["ban"], commands_prefix="!/")
async def cmd_ban(message: types.Message):
    if not message.reply_to_message:
        await message.reply('This command must be only answer on message!')
        return

    await message.bot.delete_message(config.GROUP_ID, message.message_id)
    await message.bot.kick_chat_member(chat_id=config.GROUP_ID, user_id=message.reply_to_message.from_user.id)

    await message.reply_to_message.reply('User was banned!')


# remove new user joined messages
@dp.message_handler(content_types=['new_chat_members'])
async def on_user_joined(message: types.Message):
    await message.delete()


# bot's job
@dp.message_handler()
async def filter_messages(message: types.Message):
    if 'bad word' in message.text:
        await message.delete()

    if message.chat.type == 'private':
        await choose_answer(message)


async def choose_answer(message):
    if message.text == '🤩 How are you?':
        markup = types.InlineKeyboardMarkup(row_width=2)

        button1 = types.InlineKeyboardButton('Good', callback_data='good')
        button2 = types.InlineKeyboardButton('Bad', callback_data='bad')

        markup.add(button1, button2)

        await message.answer("I'm okay. How are you?", reply_markup=markup)

    elif message.text == '🎲 Random number':
        await message.answer(str(random.randint(-999999999, 999999999)))

    else:
        await message.answer(message.text)


@dp.callback_query_handler()
async def callback_inline(call):
    try:
        if call.message:
            if call.data == 'good':
                await bot.send_message(call.message.chat.id, "Okay, that's good 😁")
            elif call.data == 'bad':
                await bot.send_message(call.message.chat.id, "That's bad, I'm sorry 😕")

                # remove inline buttons
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text="🤩 How are you?",
                                            reply_markup=None)

                # show alert
                await bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                                                text="THIS IS TEST NOTIFICATION!!!!")

    except Exception as exc:
        logging.info(exc)


# run long-polling
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
