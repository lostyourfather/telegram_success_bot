import config
import logging
import asyncio
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import subprocess


NAMES_SCRIPTS = {
    'SBIS': 'parsers/hr_sbis_parser.py',
    'HH parser': 'parsers/hh_api_parser.py',
    'id parser': 'parsers/id_parser.py',
    'HH api parser': 'parsers/vac_from_api_hh.py',
    'Processing': 'processing/filedata_processing.py',
    'Catalog': 'postdata/get_info_organization/get_info.py',
    'Graph': 'postdata/postdata/vacancies_array_to_frontend.py',
}


class ChooseScript(StatesGroup):
    waiting_for_script_name = State()
    waiting_for_region_number = State()
    waiting_for_region_name = State()
    waiting_for_script_work = State()


async def script_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in NAMES_SCRIPTS.keys():
        keyboard.add(name)
    await message.answer("Choose a script: ", reply_markup=keyboard)
    await ChooseScript.waiting_for_script_name.set()


async def script_chosen(message: types.Message, state: FSMContext):
    if message.text not in NAMES_SCRIPTS.keys():
        await message.answer("Incorrect script's name, please use keyboard")
        return
    await state.update_data(chosen_script=message.text)
    if message.text == "SBIS":
        await ChooseScript.waiting_for_region_number.set()
        await message.answer('Type a region number: ', reply_markup=types.ReplyKeyboardRemove())
    else:
        await ChooseScript.waiting_for_region_name.set()
        await message.answer('Type a region name: ', reply_markup=types.ReplyKeyboardRemove())


async def region_number_chosen(message: types.Message, state: FSMContext):
    await state.update_data(chosen_region_number=message.text)
    await ChooseScript.waiting_for_region_name.set()
    await message.answer('Type a region name: ', reply_markup=types.ReplyKeyboardRemove())


async def region_chosen(message: types.Message, state: FSMContext):
    await state.update_data(chosen_region_name=message.text)
    user_data = await state.get_data()
    if user_data['chosen_script'] == 'SBIS':
        await message.answer(f'Script: {user_data["chosen_script"]}, region: {message.text}, region number: {user_data["chosen_region_number"]}')
    else:
        await message.answer(f'Script: {user_data["chosen_script"]}, region: {message.text}')
    await ChooseScript.waiting_for_script_work.set()
    await message.answer("It's ok?")


async def chosen_script_run(message: types.Message, state: FSMContext):
    if message.text == 'no':
        await ChooseScript.waiting_for_script_name.set()
        return
    user_data = await state.get_data()
    proc = subprocess.Popen(args=['python', NAMES_SCRIPTS[user_data['chosen_script']]], stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                            stderr=subprocess.PIPE, encoding='utf-8')
    proc.stdin.write(user_data['chosen_region_name'])
    result, error = proc.communicate()
    with open('logs.txt', 'w') as f:
        f.write(result[0])
    proc.wait(timeout=None)
    await bot.send_document(message.from_user.id, types.InputFile('logs.txt'))
    if error == '\n':
        await message.answer("SUCCESS")
    else:
        await message.answer(f'Error\n{error}')
    await state.finish()


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(script_start, commands='start_script', state="*")
    dp.register_message_handler(script_chosen, state=ChooseScript.waiting_for_script_name)
    dp.register_message_handler(region_number_chosen, state=ChooseScript.waiting_for_region_number)
    dp.register_message_handler(region_chosen, state=ChooseScript.waiting_for_region_name)
    dp.register_message_handler(chosen_script_run, state=ChooseScript.waiting_for_script_work)


logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    commands = [
        types.bot_command.BotCommand(command="/start_script", description="Start a script"),
    ]
    await bot.set_my_commands(commands)


async def main():
    global bot
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.info("Starting bot")
    bot = Bot(token=config.API_TOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())
    register_handlers(dp)
    await set_commands(bot)
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
'''
async def start_script(message) -> str:
    answ = subprocess.Popen(args=['python', message], stdout=subprocess.PIPE, stdin=subprocess.PIPE, encoding='utf-8')
    answ.stdin.write('ok')
    result = answ.communicate()
    with open('logs.txt', 'w') as f:
        f.write(result[0])
    answ.wait(timeout=None)
    #await message.answer(start_script('C:/Users/rodin/Desktop/tg_return_bot/telegram_success_bot/hr_sbis_parser.py'))
    await bot.send_document(message.from_user.id, types.InputFile('logs.txt'))
    await message.answer("SUCCESS")




@dp.message_handler(commands=['start_script'], commands_prefix='!/')
async def echo(message: types.Message) -> None:
    send = bot.send_message(message.chat.id, 'Введи город')
    bot. next_step_handler(send, start_script)
'''

'''if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)'''

