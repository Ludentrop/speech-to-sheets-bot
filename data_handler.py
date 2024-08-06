"""
This module is used to extract and format data from the input text.
"""
import datetime as dt
import subprocess
import os

from cfg import TABLE_COLS
from google_speech import recognize_speech


def gov_number_former(gov_number: str) -> str:
    """
    The function formats the government number.

    :param gov_number: The government number.
    :return gov_number: The formatted government number.
    """
    letters = {
        "a": "а",
        "v": "в",
        "e": "е",
        "k": "к",
        "m": "м",
        "n": "н",
        "o": "о",
        "r": "р",
        "s": "с",
        "t": "т",
        "h": "х",
    }
    gov_number = gov_number.replace(" ", "").strip().lower()

    for i in range(len(gov_number)):
        if gov_number[i] in letters:
            gov_number = gov_number.replace(gov_number[i], letters[gov_number[i]])

    return gov_number


def date_former(date: str) -> str:
    """
    The function format date from the input text.

    :param date: The input date.
    :return date: Formatted date.
    """
    if " " in date:
        date = date.replace(" ", "")
    if "." in date:
        date = date.replace(".", "")

    try:
        date = (((dt.datetime.strptime(date, "%d%m%y")
                .date())
                .strftime("%d-%m-%Y"))
                .replace("-", "."))
    except ValueError as e:
        print("Date format error")
        print(e)
        return ''

    return date


def cost_former(cost: str) -> str:
    """
    The function formats the cost input text.

    :param cost: The cost.
    :return cost: The formatted cost.
    """
    if ' ' in cost:
        cost = cost.replace(" ", "")
    if "." in cost:
        cost = cost.replace(".", "")

    return cost


def convert_and_save(file_name: str) -> str:
    """
    Преобразует сообщение в текст и сохраняет его в файл.

    :param file_name: Input file name.
    :return file_name: Output file name.
    """
    file_name_wav = file_name+'.wav'
    subprocess.call(
        ["ffmpeg", "-i", file_name, "-ar", "16000", "-ac", "1", file_name_wav]
    )

    return file_name_wav


# def extract_data(col: str, converter: callable, transcriber: callable, file_name: str) -> str:
#     """
#     The function extract data from the input text by keywords.
#
#     :param converter: The function to convert and save the input file.
#     :param file_name: Input file name.
#     :param transcriber: The function to transcribe the input file.
#     :param col: The name of the column.
#     :return data: List of extracted data.
#     """
#     file_name_wav = converter(file_name)
#     text = transcriber(file_name_wav)
#     match col:
#         case "name":
#             text = text.strip().title()
#         case "phone":
#             text = text.replace(" ", "")
#         case "auto":
#             text = text.strip().title()
#         case "gov_number":
#             text = gov_number_former(text)
#         case "service":
#             text = text.strip().capitalize()
#         case "receive":
#             text = date_former(text)
#         case "issue":
#             text = date_former(text)
#         case "payment":
#             text = text.strip().capitalize()
#         case "cost":
#             text = cost_former(text)
#
#     os.remove(file_name)
#     os.remove(file_name+'.wav')
#
#     return text


# def main(col: str, file_name: str) -> list:
#     data = extract_data(
#         col,
#         convert_and_save,
#         recognize_speech,
#         file_name
#     )
#     return data
