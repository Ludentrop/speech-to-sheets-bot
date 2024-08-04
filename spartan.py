"""
This module implements the Telegram bot logic.
"""
import os
import subprocess

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from SpeechRecognition import recognize_speech
from sheets_connection import insert_values
from extraction import main
from cfg import TOKEN, TABLE_URL

bot = Bot(TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=["start"])
async def start(message: types.Message) -> None:
    """
    Отправляет пользователю приветствие.

    :param message:
    :return:
    """
    await message.reply("Все входящие сообщения будут записоваться в таблицу")


@dp.message_handler(commands=["help"])
async def command_help_handler(message: types.Message) -> None:
    """
    Отправляет пользователю справку по команде.

    :param message:
    :return:
    """
    await message.answer(
        f"Попробуйте произносить данные так:\n\n"
        f"[телефон] 8 987 654 32 10 (восемь девятьсот восемьдесят семь...тридцать два десять)\n\n"
        f"[госномер] с 223 кн 177   (эс двести двадцать три ка эн...)\n\n"
        f"[приём] 220824            (двадцать два ноль восемь двадцать четыре)\n\n"
        f"[сумма] 1000              (одна тысяча)\n\n"
    )


@dp.message_handler(commands=["table"])
async def command_table_handler(message: types.Message) -> None:
    """
    Отправляет пользователю ссылку на таблицу.

    :param message:
    :return:
    """
    await message.answer(f"Таблица:\n{TABLE_URL}")


@dp.message_handler(content_types=[types.ContentType.VOICE])
async def voice_message_handler(message: types.Message) -> None:
    """
    Записывает данные из голосового сообщения в таблицу.

    :param message:
    :return:
    """
    split_up = os.path.splitext(message.voice.file_id)
    file_name = f"{split_up[0]}_{message.from_user.first_name}{split_up[1]}"
    await bot.download_file_by_id(message.voice.file_id, file_name)

    file_name_wav = (
            f"{split_up[0]}_{message.from_user.first_name}{split_up[1]}" + ".wav"
    )
    subprocess.call(
        ["ffmpeg", "-i", file_name, "-ar", "16000", "-ac", "1", file_name_wav]
    )

    text = recognize_speech(file_name_wav)
    await bot.send_message(message.from_user.id, f"Следующие данные записаны:\n{text}")

    data = main(text)

    if data:
        values = {"values": [data]}
        status = insert_values(values)
        if not status:
            await bot.send_message(message.from_user.id,
                                   "Не удалось подключиться к Google Sheets\nПопробуйте повторить запись",
                                   )
    else:
        await bot.send_message(
            message.from_user.id,
            "Не удалось распознать данные" "\nПопробуйте повторить запись",
        )

    print(data)

    os.remove(file_name)
    os.remove(file_name_wav)


if __name__ == "__main__":
    from aiogram.utils import executor

    executor.start_polling(dp, skip_updates=True)
