import gspread
import os
from google.oauth2.service_account import Credentials
from datetime import datetime

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

import time
import gspread

def open_sheet_with_retry(client, spreadsheet, retries=3):
    for attempt in range(retries):
        try:
            return client.open(spreadsheet)
        except Exception as e:
            if attempt == retries - 1:
                raise
            time.sleep(5)
            
def get_client():
    creds = Credentials.from_service_account_file(
        "service-account.json",
        scopes=SCOPES
    )
    return gspread.authorize(creds)

def col_letter(n):
    string = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string

def append_data(spreadsheet, worksheet, data, data_columns, logger):
    client = get_client()
    sheet = client.open(spreadsheet).worksheet(worksheet)

    row_count = len(sheet.get_all_values())

    if row_count >= 320000:
        last_col = col_letter(data_columns)
        logger.warning("Row cap reached. Clearing data area.")
        sheet.batch_clear([f"A2:{last_col}"])

    sheet.append_rows(data)

def replace_today_data(spreadsheet, worksheet, data, data_columns, logger):
    client = get_client()
    sheet = client.open(spreadsheet).worksheet(worksheet)

    today = datetime.now().date().isoformat()
    all_values = sheet.get_all_values()

    rows_to_delete = []
    for idx, row in enumerate(all_values[1:], start=2):
        if row and row[0].startswith(today):
            rows_to_delete.append(idx)

    for row_idx in reversed(rows_to_delete):
        sheet.delete_rows(row_idx)

    sheet.append_rows(data)