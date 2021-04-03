import config
import logging
from aiogram import Bot, Dispatcher, executor, types
import subprocess


logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)


def start_script(path_to_script: str) -> str:
    answ = subprocess.Popen(args=['python', 'some_prog.py'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, encoding='utf-8')
    answ.stdin.write('ok')
    result = answ.communicate()
    print(result[0])
    answ.wait(timeout=None)
    return 'SUCCESS'


@dp.message_handler(commands=['start_script'], commands_prefix='!/')
async def echo(message: types.Message) -> None:
    await message.answer(message.from_user.id)#start_script('a'))

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

