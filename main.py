import logging
import os
import subprocess

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
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
    choose_format = State()
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
    await message.reply("Для записи данных введите команду /insert")


@dp.message_handler(commands=["help"])
async def command_help_handler(message: types.Message) -> None:
    await message.answer(
        f"Попробуйте произносить данные так:\n\n"
        f"[8 987 654 32 10]\n(восемь девятьсот восемьдесят семь...тридцать два десять)\n\n"
        f"[с223кн177]\n(эс двести двадцать три ка эн...)\n\n"
        f"[220824]\n(двадцать два ноль восемь двадцать четыре)\n\n"
        f"[1000]\n(одна тысяча рублей)\n\n"
    )


@dp.message_handler(commands=["table"])
async def command_table_handler(message: types.Message) -> None:
    await message.answer(f"Таблица:\n{TABLE_URL}")


async def start_insert(message: types.Message, state: FSMContext):
    await Form.waiting_for_name.set()
    format_type = await state.get_data("format_type")
    format_type = format_type.get("format_type", None)
    if format_type == "voice":
        await message.reply("Введите имя (голосовым сообщением)")
    else:
        await message.reply("Введите имя (текстовым сообщением)")


@dp.message_handler(commands=["insert"], state="*")
async def cmd_insert(message: types.Message):
    await Form.choose_format.set()
    await message.reply("Выберите формат ввода: голосом или текстом. Напишите 'голос' или 'текст'.")


@dp.message_handler(state=Form.choose_format)
async def process_format_choice(message: types.Message, state: FSMContext):
    if message.text.lower() in ["голос", "текст"]:
        await state.update_data(format_type="voice" if message.text.lower() == "голос" else "text")
        await start_insert(message, state)
    else:
        await message.reply("Неверный формат. Пожалуйста, выберите 'голос' или 'текст'.")


@dp.message_handler(commands=["cancel"], state="*")
@dp.message_handler(Text(equals="cancel", ignore_case=True), state="*")
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply("Ввод данных отменен.")


@dp.message_handler(content_types=[types.ContentType.VOICE, types.ContentType.TEXT], state=Form.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    format_type = await state.get_data("format_type")
    format_type = format_type.get("format_type", None)
    if format_type == "voice":
        if message.voice:
            split_up = os.path.splitext(message.voice.file_id)
            file_name = f"{split_up[0]}_{message.from_user.first_name}{split_up[1]}"
            await bot.download_file_by_id(message.voice.file_id, file_name)

            name = execute_all(file_name).strip().title()

            await state.update_data(name=name)
            await continue_to_phone(message, state)
        else:
            return await message.reply("Пожалуйста, отправьте имя в виде голосового сообщения.")
    else:
        await state.update_data(name=message.text)
        await continue_to_phone(message, state)


async def continue_to_phone(message: types.Message, state: FSMContext):
    await Form.next()
    format_type = await state.get_data("format_type")
    format_type = format_type.get("format_type", None)
    if format_type == "voice":
        await message.reply("Введите телефон (голосовым сообщением)")
    else:
        await message.reply("Введите телефон (текстовым сообщением)")


@dp.message_handler(content_types=[types.ContentType.VOICE, types.ContentType.TEXT], state=Form.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    format_type = await state.get_data("format_type")
    format_type = format_type.get("format_type", None)
    if format_type == "voice":
        if message.voice:
            split_up = os.path.splitext(message.voice.file_id)
            file_name = f"{split_up[0]}_{message.from_user.first_name}{split_up[1]}"
            await bot.download_file_by_id(message.voice.file_id, file_name)

            phone = execute_all(file_name).replace(" ", "")

            await state.update_data(phone=phone)
            await continue_to_auto(message, state)
        else:
            return await message.reply("Пожалуйста, отправьте телефон в виде голосового сообщения.")
    else:
        await state.update_data(phone=message.text)
        await continue_to_auto(message, state)


async def continue_to_auto(message: types.Message, state: FSMContext):
    await Form.next()
    format_type = await state.get_data("format_type")
    format_type = format_type.get("format_type", None)
    if format_type == "voice":
        await message.reply("Введите модель авто (голосовым сообщением)")
    else:
        await message.reply("Введите модель авто (текстовым сообщением)")


@dp.message_handler(content_types=[types.ContentType.VOICE, types.ContentType.TEXT], state=Form.waiting_for_auto)
async def process_auto(message: types.Message, state: FSMContext):
    format_type = await state.get_data("format_type")
    format_type = format_type.get("format_type", None)
    if format_type == "voice":
        if message.voice:
            split_up = os.path.splitext(message.voice.file_id)
            file_name = f"{split_up[0]}_{message.from_user.first_name}{split_up[1]}"
            await bot.download_file_by_id(message.voice.file_id, file_name)

            auto = execute_all(file_name).strip().title()

            await state.update_data(auto=auto)
            await continue_to_gov(message, state)
        else:
            return await message.reply("Пожалуйста, отправьте модель авто в виде голосового сообщения.")
    else:
        await state.update_data(auto=message.text)
        await continue_to_gov(message, state)


async def continue_to_gov(message: types.Message, state: FSMContext):
    await Form.next()
    format_type = await state.get_data("format_type")
    format_type = format_type.get("format_type", None)
    if format_type == "voice":
        await message.reply("Введите гос номер (голосовым сообщением)")
    else:
        await message.reply("Введите гос номер (текстовым сообщением)")


@dp.message_handler(content_types=[types.ContentType.VOICE, types.ContentType.TEXT], state=Form.waiting_for_gov)
async def process_gov(message: types.Message, state: FSMContext):
    format_type = await state.get_data("format_type")
    format_type = format_type.get("format_type", None)
    if format_type == "voice":
        if message.voice:
            split_up = os.path.splitext(message.voice.file_id)
            file_name = f"{split_up[0]}_{message.from_user.first_name}{split_up[1]}"
            await bot.download_file_by_id(message.voice.file_id, file_name)

            gov = gov_number_former(execute_all(file_name))

            await state.update_data(gov=gov)
            await continue_to_service(message, state)
        else:
            return await message.reply("Пожалуйста, отправьте гос номер в виде голосового сообщения.")
    else:
        await state.update_data(gov=message.text)
        await continue_to_service(message, state)


async def continue_to_service(message: types.Message, state: FSMContext):
    await Form.next()
    format_type = await state.get_data("format_type")
    format_type = format_type.get("format_type", None)
    if format_type == "voice":
        await message.reply("Введите услугу (голосовым сообщением)")
    else:
        await message.reply("Введите услугу (текстовым сообщением)")


@dp.message_handler(content_types=[types.ContentType.VOICE, types.ContentType.TEXT], state=Form.waiting_for_service)
async def process_service(message: types.Message, state: FSMContext):
    format_type = await state.get_data("format_type")
    format_type = format_type.get("format_type", None)
    if format_type == "voice":
        if message.voice:
            split_up = os.path.splitext(message.voice.file_id)
            file_name = f"{split_up[0]}_{message.from_user.first_name}{split_up[1]}"
            await bot.download_file_by_id(message.voice.file_id, file_name)

            service = execute_all(file_name).strip().capitalize()

            await state.update_data(service=service)
            await continue_to_receive(message, state)
        else:
            return await message.reply("Пожалуйста, отправьте услугу в виде голосового сообщения.")
    else:
        await state.update_data(service=message.text)
        await continue_to_receive(message, state)


async def continue_to_receive(message: types.Message, state: FSMContext):
    await Form.next()
    format_type = await state.get_data("format_type")
    format_type = format_type.get("format_type", None)
    if format_type == "voice":
        await message.reply("Введите дату приёма (голосовым сообщением)")
    else:
        await message.reply("Введите дату приёма (текстовым сообщением)")


@dp.message_handler(content_types=[types.ContentType.VOICE, types.ContentType.TEXT], state=Form.waiting_for_receive)
async def process_receive(message: types.Message, state: FSMContext):
    format_type = await state.get_data("format_type")
    format_type = format_type.get("format_type", None)
    if format_type == "voice":
        if message.voice:
            split_up = os.path.splitext(message.voice.file_id)
            file_name = f"{split_up[0]}_{message.from_user.first_name}{split_up[1]}"
            await bot.download_file_by_id(message.voice.file_id, file_name)

            receive = date_former(execute_all(file_name))

            await state.update_data(receive=receive)
            await continue_to_issue(message, state)
        else:
            return await message.reply("Пожалуйста, отправьте дату приёма в виде голосового сообщения.")
    else:
        await state.update_data(receive=message.text)
        await continue_to_issue(message, state)


async def continue_to_issue(message: types.Message, state: FSMContext):
    await Form.next()
    format_type = await state.get_data("format_type")
    format_type = format_type.get("format_type", None)
    if format_type == "voice":
        await message.reply("Введите дату выдачи (голосовым сообщением)")
    else:
        await message.reply("Введите дату выдачи (текстовым сообщением)")


@dp.message_handler(content_types=[types.ContentType.VOICE, types.ContentType.TEXT], state=Form.waiting_for_issue)
async def process_issue(message: types.Message, state: FSMContext):
    format_type = await state.get_data("format_type")
    format_type = format_type.get("format_type", None)
    if format_type == "voice":
        if message.voice:
            split_up = os.path.splitext(message.voice.file_id)
            file_name = f"{split_up[0]}_{message.from_user.first_name}{split_up[1]}"
            await bot.download_file_by_id(message.voice.file_id, file_name)

            issue = date_former(execute_all(file_name))

            await state.update_data(issue=issue)
            await continue_to_payment(message, state)
        else:
            return await message.reply("Пожалуйста, отправьте дату выдачи в виде голосового сообщения.")
    else:
        await state.update_data(issue=message.text)
        await continue_to_payment(message, state)


async def continue_to_payment(message: types.Message, state: FSMContext):
    await Form.next()
    format_type = await state.get_data("format_type")
    format_type = format_type.get("format_type", None)
    if format_type == "voice":
        await message.reply("Введите способ оплаты (голосовым сообщением)")
    else:
        await message.reply("Введите способ оплаты (текстовым сообщением)")


@dp.message_handler(content_types=[types.ContentType.VOICE, types.ContentType.TEXT], state=Form.waiting_for_payment)
async def process_payment(message: types.Message, state: FSMContext):
    format_type = await state.get_data("format_type")
    format_type = format_type.get("format_type", None)
    if format_type == "voice":
        if message.voice:
            split_up = os.path.splitext(message.voice.file_id)
            file_name = f"{split_up[0]}_{message.from_user.first_name}{split_up[1]}"
            await bot.download_file_by_id(message.voice.file_id, file_name)

            payment = execute_all(file_name).strip().capitalize()

            await state.update_data(payment=payment)
            await continue_to_cost(message, state)
        else:
            return await message.reply("Пожалуйста, отправьте способ оплаты в виде голосового сообщения.")
    else:
        await state.update_data(payment=message.text)
        await continue_to_cost(message, state)


async def continue_to_cost(message: types.Message, state: FSMContext):
    await Form.next()
    format_type = await state.get_data("format_type")
    format_type = format_type.get("format_type", None)
    if format_type == "voice":
        await message.reply("Введите стоимость услуг (голосовым сообщением)")
    else:
        await message.reply("Введите стоимость услуг (текстовым сообщением)")


@dp.message_handler(content_types=[types.ContentType.VOICE, types.ContentType.TEXT], state=Form.waiting_for_cost)
async def process_cost(message: types.Message, state: FSMContext):
    format_type = await state.get_data("format_type")
    format_type = format_type.get("format_type", None)
    if format_type == "voice":
        if message.voice:
            split_up = os.path.splitext(message.voice.file_id)
            file_name = f"{split_up[0]}_{message.from_user.first_name}{split_up[1]}"
            await bot.download_file_by_id(message.voice.file_id, file_name)

            cost = cost_former(execute_all(file_name))

            await state.update_data(cost=cost)
            await confirm_data(message, state)
        else:
            return await message.reply("Пожалуйста, отправьте стоимость услуг в виде голосового сообщения.")
    else:
        await state.update_data(cost=message.text)
        await confirm_data(message, state)


async def confirm_data(message: types.Message, state: FSMContext):
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
                        f"Стоимость услуг: {user_data['cost']}\n\nЕсли всё верно, введите 'Да', иначе 'Нет'")


@dp.message_handler(lambda message: message.text.lower() in ["да", "нет"], state=Form.confirm_data)
async def process_confirmation(message: types.Message, state: FSMContext):
    if message.text.lower() == "да":
        user_data = await state.get_data()
        insert_values(list(user_data.values()))
        await message.reply("Данные сохранены!")
        await state.finish()
    else:
        await start_insert(message, state)


if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
