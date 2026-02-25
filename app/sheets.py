import time
from datetime import datetime
from typing import List

import gspread
from google.oauth2.service_account import Credentials


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SERVICE_ACCOUNT_FILE = "service-account.json"


# ---------------------------------------------------
# AUTH
# ---------------------------------------------------

def get_client():
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
    )
    return gspread.authorize(creds)


def open_sheet_with_retry(client, spreadsheet_name, retries=3, delay=5):
    """
    Open spreadsheet with retry logic to handle transient network issues.
    """
    for attempt in range(retries):
        try:
            return client.open(spreadsheet_name)
        except Exception as e:
            if attempt == retries - 1:
                raise
            time.sleep(delay)


# ---------------------------------------------------
# UTILITIES
# ---------------------------------------------------

def col_letter(n: int) -> str:
    """
    Convert column number to Excel column letter.
    Example: 1 -> A, 4 -> D, 10 -> J
    """
    string = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string


# ---------------------------------------------------
# APPEND (INCREMENTAL MODE)
# ---------------------------------------------------

def append_data(
    spreadsheet: str,
    worksheet: str,
    data: List[List],
    data_columns: int,
    logger,
):
    """
    Append rows safely while:
    - Preserving header row
    - Preserving formula columns
    - Enforcing 320k row cap
    """

    if not data:
        logger.info("No rows to append.")
        return

    client = get_client()
    spread = open_sheet_with_retry(client, spreadsheet)
    sheet = spread.worksheet(worksheet)

    # Fast metadata row count (does NOT download whole sheet)
    current_rows = sheet.row_count

    # 320k safety limit
    if current_rows >= 320000:
        last_col_letter = col_letter(data_columns)
        logger.warning("Row cap reached (320k). Clearing data area only.")
        sheet.batch_clear([f"A2:{last_col_letter}"])

    # Append rows
    sheet.append_rows(
        data,
        value_input_option="USER_ENTERED",
    )

    logger.info(f"Appended {len(data)} rows to {spreadsheet} -> {worksheet}")


# ---------------------------------------------------
# REPLACE TODAY (ENGAGEMENT MODE)
# ---------------------------------------------------

def replace_today_data(
    spreadsheet: str,
    worksheet: str,
    data: List[List],
    data_columns: int,
    logger,
):
    """
    Replace ONLY today's rows (based on first column date).
    Keeps all historical data intact.
    """

    if not data:
        logger.info("No rows to write for replace_today.")
        return

    client = get_client()
    spread = open_sheet_with_retry(client, spreadsheet)
    sheet = spread.worksheet(worksheet)

    today_str = datetime.now().strftime("%Y-%m-%d")

    # Fetch only first column to reduce payload
    first_column = sheet.col_values(1)

    rows_to_delete = []

    # Skip header row (index 0)
    for idx, cell_value in enumerate(first_column[1:], start=2):
        if cell_value.startswith(today_str):
            rows_to_delete.append(idx)

    # Delete from bottom to top to avoid index shifting
    for row_index in reversed(rows_to_delete):
        sheet.delete_rows(row_index)

    if rows_to_delete:
        logger.info(f"Deleted {len(rows_to_delete)} existing rows for today.")

    # Append fresh rows
    sheet.append_rows(
        data,
        value_input_option="USER_ENTERED",
    )

    logger.info(
        f"Replaced today's data with {len(data)} rows in {spreadsheet} -> {worksheet}"
    )