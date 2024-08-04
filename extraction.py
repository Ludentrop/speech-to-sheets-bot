"""
This module is used to extract and format data from the input text.
"""
import datetime as dt


def extract_data(input_text: str) -> list:
    """
    The function extract data from the input text by keywords.

    :param input_text: The input text.
    :return: List of extracted data.
    """
    keys = [
        "имя",
        "телефон",
        "авто",
        "госномер",
        "услуга",
        "приём",
        "выдача",
        "оплата",
        "сумма",
    ]

    for key in keys:
        input_text = " ".join(input_text.split(key))
    input_text = input_text.strip()

    return input_text.split("  ")


def form_data(text_list: list) -> list:
    """
    The function format data from the input text.

    :param text_list: The input list of data.
    :return: List of formatted data.
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

    try:
        name, phone, auto, gov_number, service, receive, issue, payment, cost = (
            text_list
        )
    except ValueError:
        print(text_list)
        return []

    name = name.title().strip()
    phone = phone.replace(" ", "").strip()
    auto = auto.title().strip()
    gov_number = gov_number.replace(" ", "").strip()
    for i in range(len(gov_number)):
        if gov_number[i] in letters:
            gov_number = gov_number.replace(gov_number[i], letters[gov_number[i]])
    service = service.strip().capitalize()

    if " " in service or " " in issue or " " in cost:
        receive = receive.replace(" ", "")
        issue = issue.replace(" ", "")
        cost = cost.replace(" ", "")
    elif "." in service or "." in issue or "." in cost:
        receive = receive.replace(".", "")
        issue = issue.replace(".", "")
        cost = cost.replace(".", "")
    else:
        receive = receive.strip()
        issue = issue.strip()
        cost = cost.strip()

    try:
        receive = (
            dt.datetime.strptime(receive, "%d%m%y")
            .date()
            .strftime("%d-%m-%Y")
            .replace("-", ".")
        )
        issue = (
            dt.datetime.strptime(issue, "%d%m%y")
            .date()
            .strftime("%d-%m-%Y")
            .replace("-", ".")
        )
    except ValueError as e:
        print("Date format error")
        print(e)
        return []
    payment = payment.strip().capitalize()
    cost = cost.strip()

    return [name, phone, auto, gov_number, service, receive, issue, payment, cost]


def main(text):
    """
    The function main.

    :param text: The input text.
    :return: List of extracted and formatted data.
    """
    text = extract_data(text)
    text = form_data(text)
    return text
