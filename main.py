import telebot
from telebot import types

from telegram_bot import config as cfg
from telegram_bot import exceptions as ex
from telegram_bot.database import Planner

bot = telebot.TeleBot(cfg.TOKEN)
planner = Planner()


@bot.message_handler(commands=['start'])
def send_keyboard(message: types.Message, text: str = 'Hello!can I help you?'):
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    add_button = types.KeyboardButton(cfg.ADD_BUTTON)
    show_button = types.KeyboardButton(cfg.SHOW_BUTTON)
    delete_button = types.KeyboardButton(cfg.DELETE_BUTTON)
    delete_all_button = types.KeyboardButton(cfg.DELETE_ALL_BUTTON)
    keyboard.row(add_button, show_button)
    keyboard.row(delete_button, delete_all_button)

    message = bot.send_message(
        chat_id=message.chat.id,
        text=text,
        reply_markup=keyboard
    )

    bot.register_next_step_handler(message, callback_worker)


def callback_worker(message):
    if message.text == cfg.ADD_BUTTON:
        message = bot.send_message(
            message.chat.id,
            text="Let's add task. Write it to chat"
        )
        bot.register_next_step_handler(message, add)

    elif message.text == cfg.SHOW_BUTTON:
        show(message=message)

    elif message.text == cfg.DELETE_BUTTON:
        try:
            tasks = planner.get_tasks(message=message)
            markup = types.ReplyKeyboardMarkup(row_width=2)
            for task in tasks:
                task_button = types.KeyboardButton(task)
                markup.add(task_button)
            message = bot.send_message(
                message.chat.id,
                text='Choose one task from list',
                reply_markup=markup
            )

            bot.register_next_step_handler(message, delete)
        except ex.TaskNotExists:
            bot.send_message(message.chat.id, text='You have not tasks')
            send_keyboard(message=message, text='Can I help you with another actions?')

    elif message.text == cfg.DELETE_ALL_BUTTON:
        delete_all(message=message)


@bot.message_handler(content_types=['text'])
def handle_docs_audio(message: types.Message):
    send_keyboard(message, text="I don't understand. Choose one of these actions:")


def add(message):
    planner.add(message=message)
    bot.send_message(message.chat.id, 'Task is added')
    send_keyboard(message=message, text="Can I help you?")


def show(message):
    try:
        tasks = planner.show(message=message)
        bot.send_message(message.chat.id, tasks)
    except ex.TaskNotExists:
        bot.send_message(message.chat.id, 'You did not have tasks yet')
    finally:
        send_keyboard(message=message, text='Can I help you with another tasks')


def delete(message):
    planner.delete(message=message)
    bot.send_message(message.chat.id, f"Task {message.text} is deleted")
    send_keyboard(message=message, text='Can I help with another tasks?')


def delete_all(message):
    planner.delete_all(message)
    bot.send_message(message.chat.id, 'All tasks are deleted')
    send_keyboard(message=message, text='Can I help with another tasks?')


if __name__ == '__main__':
    bot.infinity_polling()
