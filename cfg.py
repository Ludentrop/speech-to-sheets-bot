"""
The configuration file.
"""
# TOKEN = 'Telegram Token'
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
TABLE_COLS = ['Имя', 'Телефон', 'Авто', 'Госномер', 'Услуга', 'Дата приема', 'Дата выдачи', 'Способ оплаты', 'Сумма']
CREDENTIALS_FILE = "creds.json"  # Path to the Google credentials file
# SPREADSHEET_ID = "ID of the Google spreadsheet"
# TABLE_URL = "URL of the table"

TOKEN = '7247769396:AAEuGg7pZjYuHIddcKy2E8JVWvb2nthg-Q0'
SPREADSHEET_ID = "1hC5iWOeeHKIFbAWV375CyK7J8bZKY7nATVnJQRiHEhQ"
TABLE_URL = "https://docs.google.com/spreadsheets/d/1hC5iWOeeHKIFbAWV375CyK7J8bZKY7nATVnJQRiHEhQ/edit?gid=0#gid=0"