from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import vars
import logic

vars.bot = Bot(token=vars.TOKENnotice)

dp = Dispatcher(vars.bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

@dp.callback_query_handler(text_contains='claim', state='*')
async def query_answer_show_list(call: types.CallbackQuery):
    await logic.Claim_Callback(call)

async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()

if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=shutdown)
