"""
This module is used to connect to Google Sheets.
"""
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials
import httplib2

from cfg import *


credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPES)

httpAuth = credentials.authorize(httplib2.Http())
service = build("sheets", "v4", http=httpAuth)


def insert_values(data: list) -> int:
    """
    Inserts a row of data into the spreadsheet.

    :param data: A list of values to insert.
    :return: Integer indicating the status of the insert operation.
    """
    values = {"values": [data]}

    try:
        vals = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=SPREADSHEET_ID,
                range="A1:I1",
                valueInputOption="USER_ENTERED",
                body=values,
            )
            .execute()
        )
        print(vals.get("updates"))
        return 1
    except HttpError as e:
        print(e)
        return 0
