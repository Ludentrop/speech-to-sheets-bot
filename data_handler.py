"""
This module is used to extract and format data from the input text.
"""
import datetime as dt
import subprocess


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
    if "руб" in cost:
        cost = cost.replace("руб", "")
    if "рублей" in cost:
        cost = cost.replace("рублей", "")

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
