import config
import logging
from aiogram import Bot, Dispatcher, executor, types
import subprocess


logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)


async def start_script(message) -> str:
    answ = subprocess.Popen(args=['python', message], stdout=subprocess.PIPE, stdin=subprocess.PIPE, encoding='utf-8')
    answ.stdin.write('ok')
    result = answ.communicate()
    with open('logs.txt', 'w') as f:
        f.write(result[0])
    answ.wait(timeout=None)
    #await message.answer(start_script('C:/Users/rodin/Desktop/tg_return_bot/telegram_success_bot/some_prog.py'))
    await bot.send_document(message.from_user.id, types.InputFile('logs.txt'))
    await message.answer("SUCCESS")


@dp.message_handler(commands=['start_script'], commands_prefix='!/')
async def echo(message: types.Message) -> None:
    send = bot.send_message(message.chat.id, 'Введи город')
    bot. next_step_handler(send, start_script)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

