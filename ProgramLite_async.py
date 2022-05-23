from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
# from aiogram.utils.callback_data import CallbackData
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
# from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
import os
import dialogs
import vars
import commands
import logic
import logging


ROOT_DIR = os.path.abspath(os.curdir)
log_path = ROOT_DIR + '\\Logs\\telebot.log'
logging.basicConfig(
        filename=log_path, format='%(asctime)s:%(process)d:%(levelname)s:%(message)s',
        level=vars.log_level)

vars.userHistory = dict()  # история вводимых команд
vars.userMessage = dict()  # история event-ов
vars.userBotActions = dict()  # история event-ов бота

vars.bot = Bot(token=vars.TOKEN)

dp = Dispatcher(vars.bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


# States
class reg(StatesGroup):
    Neutral = State()
    NewReq = State()
    NewCom = State()
    NewInit = State()
    NewScore = State()


@dp.message_handler(content_types=types.message.ContentType.ANY, state=reg.NewScore)
async def second_test_state_case_met(message: types.Message):
    await logic.feedback(message)
    await reg.Neutral.set()


@dp.message_handler(content_types=types.message.ContentType.ANY, state=reg.NewReq)
async def add_message_chain1(message):
    await logic.NewReq(message)


@dp.message_handler(content_types=types.message.ContentType.ANY, state=reg.NewCom)
async def add_message_chain2(message):
    await logic.NewCom(message)


@dp.message_handler(commands=['start'], state='*')
async def process_start_command1(message: types.Message):
    await commands.start_command(message)


@dp.message_handler(commands=['clear'], state='*')
async def process_start_command6(message: types.Message):
    await commands.clear_command(message, reg, message.chat.id)

@dp.message_handler(commands=['help'], state='*')
async def process_start_command2(message: types.Message):
    await commands.help_command(message)

@dp.message_handler(commands=['com'], state='*')
async def process_start_command3(message: types.Message):
    await commands.com_command(message)

@dp.message_handler(commands=['hide'], state='*')
async def process_start_command3(message: types.Message):
    await commands.hide_command(message)

@dp.message_handler(commands=['show'], state='*')
async def process_start_command4(message: types.Message):
    await commands.show_command(message)


@dp.message_handler(commands=['list'], state='*')
async def process_start_command5(message: types.Message):
    await commands.list_command(message)


@dp.message_handler(state='NewInit')
async def new_init(message: types.Message):
    await logic.NewInit(message)
    await reg.Neutral.set()


@dp.message_handler(content_types=types.message.ContentType.ANY, state='*')
async def echo_message(message: types.Message):
    if (message.text == '1️⃣Создать заявку'):
        await reg.NewReq.set()
        await logic.Create_Callback(message)
    elif (message.text == '2️⃣Напомнить логин'):
        await logic.LoginBack(message)
    elif (message.text == '3️⃣Сбросить пароль'):
        await logic.PasswordBack(message)
    else:
        await logic.SimpleText(message)


@dp.callback_query_handler(text_contains='Create', state='*')
async def query_show_list(call: types.CallbackQuery):
    await logic.Create_Callback(call.message)
    await reg.NewReq.set()


@dp.callback_query_handler(text_contains='End', state=reg.NewReq)
async def query_end_show_list(call: types.CallbackQuery):
    await logic.End_Callback(call, reg)


@dp.callback_query_handler(text_contains='EndComment', state=reg.NewCom)
async def query_end_comment_show_list(call: types.CallbackQuery):
    await logic.EndComment_Callback(call, reg)


@dp.callback_query_handler(text_contains='LastCom', state='*')
async def query_lastcom_show_list(call: types.CallbackQuery):
    await logic.LastCom_Callback(call, reg)


@dp.callback_query_handler(text_contains='Answer', state='*')
async def query_answer_show_list(call: types.CallbackQuery):
    await logic.Answer_Callback(call)
    await reg.NewCom.set()


@dp.callback_query_handler(text_contains='Close', state='*')
async def query_close_show_list(call: types.CallbackQuery):
    await logic.Close_Callback(call)
    await reg.Neutral.set()


@dp.callback_query_handler(text_contains='feedback_no', state='*')
async def query_feedback_no_show_list(call: types.CallbackQuery):
    await logic.feedback_no_Callback(call)
    await reg.Neutral.set()


@dp.callback_query_handler(text_contains='oneStar', state='*')
async def query_1star_show_list(call: types.CallbackQuery):
    message_id = call.message.text[call.message.text.find("№") + 1:call.message.text.find(" ")]
    await logic.initScore(1, message_id, call.message.chat.id, reg)


@dp.callback_query_handler(text_contains='twoStar', state='*')
async def query_2star_show_list(call: types.CallbackQuery):
    message_id = call.message.text[call.message.text.find("№") + 1:call.message.text.find(" ")]
    await logic.initScore(2, message_id, call.message.chat.id, reg)


@dp.callback_query_handler(text_contains='threeStar', state='*')
async def query_3star_show_list(call: types.CallbackQuery):
    message_id = call.message.text[call.message.text.find("№") + 1:call.message.text.find(" ")]
    await logic.initScore(3, message_id, call.message.chat.id, reg)


@dp.callback_query_handler(text_contains='fourStar', state='*')
async def query_4star_show_list(call: types.CallbackQuery):
    message_id = call.message.text[call.message.text.find("№") + 1:call.message.text.find(" ")]
    await logic.initScore(4, message_id, call.message.chat.id, reg)


@dp.callback_query_handler(text_contains='fiveStar', state='*')
async def query_5star_show_list(call: types.CallbackQuery):
    message_id = call.message.text[call.message.text.find("№") + 1:call.message.text.find(" ")]
    await logic.initScore(5, message_id, call.message.chat.id, reg)


@dp.callback_query_handler(text_contains='feedback', state='*')
async def query_feedback_show_list(call: types.CallbackQuery):
    await vars.bot.send_message(call.message.chat.id, dialogs.feedback)
    await reg.NewScore.set()


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()

logging.info("--------------- ITL Helpdesk Bot started ---------------")
if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=shutdown)
