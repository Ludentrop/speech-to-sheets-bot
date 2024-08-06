import logging
import os
import subprocess

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
# from aiogram.types import ParseMode
# from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text

from google_speech import recognize_speech
from sheets_connection import insert_values
from data_handler import gov_number_former, date_former, cost_former
from cfg import TOKEN, TABLE_URL

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())


def execute_all(file_name: str) -> str:
    text = recognize_speech(convert_and_save(file_name))
    os.remove(file_name)
    os.remove(file_name + ".wav")
    return text


def convert_and_save(file_name: str):
    file_name_wav = file_name + ".wav"
    subprocess.call(
        ["ffmpeg", "-i", file_name, "-ar", "16000", "-ac", "1", file_name_wav]
    )
    return file_name_wav


class Form(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_auto = State()
    waiting_for_gov = State()
    waiting_for_service = State()
    waiting_for_receive = State()
    waiting_for_issue = State()
    waiting_for_payment = State()
    waiting_for_cost = State()
    confirm_data = State()


@dp.message_handler(commands=["start"])
async def start(message: types.Message) -> None:
    """
    Отправляет пользователю приветствие.

    :param message:
    :return:
    """
    await message.reply("Для записи данных введите команду /insert")


@dp.message_handler(commands=["help"])
async def command_help_handler(message: types.Message) -> None:
    """
    Отправляет пользователю справку по команде.

    :param message:
    :return:
    """
    await message.answer(
        f"Попробуйте произносить данные так:\n\n"
        f"8 987 654 32 10 (восемь девятьсот восемьдесят семь...тридцать два десять)\n\n"
        f"с 223 кн 177    (эс двести двадцать три ка эн...)\n\n"
        f"220824          (двадцать два ноль восемь двадцать четыре)\n\n"
        f"1000            (одна тысяча)\n\n"
    )


@dp.message_handler(commands=["table"])
async def command_table_handler(message: types.Message) -> None:
    """
    Отправляет пользователю ссылку на таблицу.

    :param message:
    :return:
    """
    await message.answer(f"Таблица:\n{TABLE_URL}")


@dp.message_handler(commands='cancel', state='*')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply("Ввод данных отменен.")


@dp.message_handler(commands=["insert"], state='*')
async def cmd_insert(message: types.Message):
    await Form.waiting_for_name.set()
    await message.reply("Запись данных производится голосовым сообщением")
    await bot.send_message(message.from_user.id, "Введите имя")


@dp.message_handler(content_types=types.ContentType.VOICE, state=Form.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    split_up = os.path.splitext(message.voice.file_id)
    file_name = f"{split_up[0]}_{message.from_user.first_name}{split_up[1]}"
    await bot.download_file_by_id(message.voice.file_id, file_name)

    name = execute_all(file_name).strip().title()
    if name == "Не удалось распознать речь":
        await state.finish()
        await message.reply("Не удалось распознать речь Попробуйте снова.")
    else:
        await state.update_data(name=name)
        await Form.next()
        await message.reply("Введите номер телефона")


@dp.message_handler(content_types=types.ContentType.VOICE, state=Form.waiting_for_phone)
async def process_age(message: types.Message, state: FSMContext):
    split_up = os.path.splitext(message.voice.file_id)
    file_name = f"{split_up[0]}_{message.from_user.first_name}{split_up[1]}"
    await bot.download_file_by_id(message.voice.file_id, file_name)

    phone = execute_all(file_name).replace(" ", "")
    if phone == "Не удалось распознать речь":
        await state.finish()
        await message.reply("Не удалось распознать речь Попробуйте снова.")
    else:
        await state.update_data(phone=phone)
        await Form.next()
        await message.reply("Введите модель авто")


@dp.message_handler(content_types=types.ContentType.VOICE, state=Form.waiting_for_auto)
async def process_age(message: types.Message, state: FSMContext):
    split_up = os.path.splitext(message.voice.file_id)
    file_name = f"{split_up[0]}_{message.from_user.first_name}{split_up[1]}"
    await bot.download_file_by_id(message.voice.file_id, file_name)

    auto = execute_all(file_name).strip().title()
    if auto == "Не удалось распознать речь":
        await state.finish()
        await message.reply("Не удалось распознать речь Попробуйте снова.")
    else:
        await state.update_data(auto=auto)
        await Form.next()
        await message.reply("Введите гос номер")


@dp.message_handler(content_types=types.ContentType.VOICE, state=Form.waiting_for_gov)
async def process_age(message: types.Message, state: FSMContext):
    split_up = os.path.splitext(message.voice.file_id)
    file_name = f"{split_up[0]}_{message.from_user.first_name}{split_up[1]}"
    await bot.download_file_by_id(message.voice.file_id, file_name)

    gov = gov_number_former(execute_all(file_name))
    if gov == "Не удалось распознать речь":
        await state.finish()
        await message.reply("Не удалось распознать речь Попробуйте снова.")
    else:
        await state.update_data(gov=gov)
        await Form.next()
        await message.reply("Введите название услуги")


@dp.message_handler(content_types=types.ContentType.VOICE, state=Form.waiting_for_service)
async def process_age(message: types.Message, state: FSMContext):
    split_up = os.path.splitext(message.voice.file_id)
    file_name = f"{split_up[0]}_{message.from_user.first_name}{split_up[1]}"
    await bot.download_file_by_id(message.voice.file_id, file_name)

    service = execute_all(file_name).strip().capitalize()
    if service == "Не удалось распознать речь":
        await state.finish()
        await message.reply("Не удалось распознать речь Попробуйте снова.")
    else:
        await state.update_data(service=service)
        await Form.next()
        await message.reply("Введите дату приёма")


@dp.message_handler(content_types=types.ContentType.VOICE, state=Form.waiting_for_receive)
async def process_age(message: types.Message, state: FSMContext):
    split_up = os.path.splitext(message.voice.file_id)
    file_name = f"{split_up[0]}_{message.from_user.first_name}{split_up[1]}"
    await bot.download_file_by_id(message.voice.file_id, file_name)

    receive = date_former(execute_all(file_name))
    if receive == "Не удалось распознать речь":
        await state.finish()
        await message.reply("Не удалось распознать речь Попробуйте снова.")
    else:
        await state.update_data(receive=receive)
        await Form.next()
        await message.reply("Введите дату выдачи")


@dp.message_handler(content_types=types.ContentType.VOICE, state=Form.waiting_for_issue)
async def process_age(message: types.Message, state: FSMContext):
    split_up = os.path.splitext(message.voice.file_id)
    file_name = f"{split_up[0]}_{message.from_user.first_name}{split_up[1]}"
    await bot.download_file_by_id(message.voice.file_id, file_name)

    issue = date_former(execute_all(file_name))
    if issue == "Не удалось распознать речь":
        await state.finish()
        await message.reply("Не удалось распознать речь Попробуйте снова.")
    else:
        await state.update_data(issue=issue)
        await Form.next()
        await message.reply("Введите способ оплаты")


# Прием голосового сообщения с возрастом
@dp.message_handler(content_types=types.ContentType.VOICE, state=Form.waiting_for_payment)
async def process_age(message: types.Message, state: FSMContext):
    split_up = os.path.splitext(message.voice.file_id)
    file_name = f"{split_up[0]}_{message.from_user.first_name}{split_up[1]}"
    await bot.download_file_by_id(message.voice.file_id, file_name)

    payment = execute_all(file_name).strip().capitalize()
    if payment == "Не удалось распознать речь":
        await state.finish()
        await message.reply("Не удалось распознать речь Попробуйте снова.")
    else:
        await state.update_data(payment=payment)
        await Form.next()
        await message.reply("Введите стоимость услуг")


@dp.message_handler(content_types=types.ContentType.VOICE, state=Form.waiting_for_cost)
async def process_phone(message: types.Message, state: FSMContext):
    split_up = os.path.splitext(message.voice.file_id)
    file_name = f"{split_up[0]}_{message.from_user.first_name}{split_up[1]}"
    await bot.download_file_by_id(message.voice.file_id, file_name)

    cost = cost_former(execute_all(file_name))
    if cost == "Не удалось распознать речь":
        await state.finish()
        await message.reply("Не удалось распознать речь Попробуйте снова.")
    else:
        await state.update_data(cost=cost)
        user_data = await state.get_data()
        await Form.next()
        await message.reply(f"Подтвердите данные:\n\n"
                            f"Имя: {user_data['name']}\n"
                            f"Номер телефона: {user_data['phone']}\n"
                            f"Модель авто: {user_data['auto']}\n"
                            f"Гос номер: {user_data['gov']}\n"
                            f"Услуга: {user_data['service']}\n"
                            f"Дата приёма: {user_data['receive']}\n"
                            f"Дата выдачи: {user_data['issue']}\n"
                            f"Способ оплаты: {user_data['payment']}\n"
                            f"Стоимость услуг: {user_data['cost']}\n\nЕсли все верно, введите 'Да', иначе 'Нет'")


@dp.message_handler(lambda message: message.text.lower() in ["да", "нет"], state=Form.confirm_data)
async def process_confirmation(message: types.Message, state: FSMContext):
    if message.text.lower() == "да":
        user_data = await state.get_data()

        insert_values(list(user_data.values()))
        await message.reply("Данные сохранены!")
        # Сброс состояния
        await state.finish()
    else:
        await Form.waiting_for_name.set()
        await message.reply("Введите имя")


if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
