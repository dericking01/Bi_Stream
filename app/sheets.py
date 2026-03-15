import time
from datetime import date, datetime, timedelta
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


def _format_cell_value(value):
    """
    Normalize date-like values to mm/dd/yy and remove timestamp components.
    """
    if isinstance(value, datetime):
        return value.strftime("%m/%d/%y")

    if isinstance(value, date):
        return value.strftime("%m/%d/%y")

    if isinstance(value, str):
        text = value.strip()
        if not text:
            return ""

        candidates = [
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%m/%d/%Y",
            "%m/%d/%y",
            "%d/%m/%Y",
            "%d/%m/%y",
            "%m/%d/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%d-%b",
            "%d-%b-%Y",
            "%d-%b-%y",
            "%d-%B",
            "%d-%B-%Y",
            "%d-%B-%y",
        ]

        normalized = text.replace("Z", "")
        for fmt in candidates:
            try:
                parsed = datetime.strptime(normalized, fmt)
                if "%Y" not in fmt and "%y" not in fmt:
                    parsed = parsed.replace(year=datetime.now().year)
                return parsed.strftime("%m/%d/%y")
            except ValueError:
                continue

        return text

    return value


def _normalize_row(row: List, data_columns: int) -> List:
    values = list(row[:data_columns])
    if len(values) < data_columns:
        values.extend([""] * (data_columns - len(values)))
    return [_format_cell_value(cell) for cell in values]


def _key_for_row(row: List, key_columns: int):
    def canonical_key_cell(cell):
        if isinstance(cell, datetime):
            return cell.date().isoformat()

        if isinstance(cell, date):
            return cell.isoformat()

        if isinstance(cell, (int, float)) and cell > 25000:
            # Google Sheets serial date (days since 1899-12-30).
            serial_date = (datetime(1899, 12, 30) + timedelta(days=float(cell))).date()
            return serial_date.isoformat()

        if isinstance(cell, str):
            text = cell.strip()
            if not text:
                return ""

            patterns = [
                "%Y-%m-%d",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%m/%d/%Y",
                "%m/%d/%y",
                "%d/%m/%Y",
                "%d/%m/%y",
                "%m/%d/%Y %H:%M:%S",
                "%d/%m/%Y %H:%M:%S",
                "%d-%b",
                "%d-%b-%Y",
                "%d-%b-%y",
                "%d-%B",
                "%d-%B-%Y",
                "%d-%B-%y",
            ]

            normalized = text.replace("Z", "")
            for fmt in patterns:
                try:
                    parsed = datetime.strptime(normalized, fmt)
                    if "%Y" not in fmt and "%y" not in fmt:
                        parsed = parsed.replace(year=datetime.now().year)
                    return parsed.date().isoformat()
                except ValueError:
                    continue

            return text.lower()

        return str(cell).strip().lower()

    return tuple(canonical_key_cell(cell) for cell in row[:key_columns])

def upsert_rows(
    spreadsheet: str,
    worksheet: str,
    data: List[List],
    data_columns: int,
    key_columns: int,
    logger,
):
    """
    Upsert rows by key (first N columns):
    - matching key -> overwrite the existing row in place
    - missing key -> append as a new row
    """

    if not data:
        logger.info("No rows to upsert.")
        return

    if key_columns < 1 or key_columns > data_columns:
        raise ValueError("key_columns must be between 1 and data_columns")

    client = get_client()
    spread = open_sheet_with_retry(client, spreadsheet)
    sheet = spread.worksheet(worksheet)

    last_col_letter = col_letter(data_columns)
    data_range = f"A2:{last_col_letter}"
    
    existing_values = sheet.get(data_range)
    if not existing_values:
        existing_values = []
    
    existing_formulas = sheet.get(data_range, value_render_option="FORMULA")
    if not existing_formulas:
        existing_formulas = []

    existing_key_to_row = {}
    reusable_empty_rows = []

    logger.info(f"Existing rows in sheet: {len(existing_values)}")
    
    for idx, row in enumerate(existing_values, start=2):
        normalized_existing = _normalize_row(row, data_columns)
        key = _key_for_row(normalized_existing, key_columns)
        if any(key):
            existing_key_to_row[key] = idx
        else:
            reusable_empty_rows.append(idx)

    logger.info(f"Loaded {len(existing_key_to_row)} existing keys for matching")
    
    updates = []
    pending_new = {}
    pending_order = []
    update_count = 0

    for row_idx, row in enumerate(data):
        normalized_row = _normalize_row(row, data_columns)
        key = _key_for_row(normalized_row, key_columns)
        if row_idx < 3:
            logger.info(
                f"Incoming key sample {row_idx + 1}: raw={row[:key_columns]} normalized={normalized_row[:key_columns]} canonical={key}"
            )

        if not any(key):
            logger.warning(f"Skipping row with empty upsert key: {normalized_row}")
            continue

        target_row = existing_key_to_row.get(key)
        if target_row:
            formula_row = []
            formula_idx = target_row - 2
            if formula_idx >= 0 and formula_idx < len(existing_formulas):
                formula_row = _normalize_row(existing_formulas[formula_idx], data_columns)

            merged_row = []
            for col_idx in range(data_columns):
                formula_cell = formula_row[col_idx] if col_idx < len(formula_row) else ""
                if isinstance(formula_cell, str) and formula_cell.startswith("="):
                    merged_row.append(formula_cell)
                else:
                    merged_row.append(normalized_row[col_idx])

            updates.append(
                {
                    "range": f"A{target_row}:{last_col_letter}{target_row}",
                    "values": [merged_row],
                }
            )
            update_count += 1
            continue

        if key not in pending_new:
            pending_order.append(key)
        pending_new[key] = normalized_row

    next_new_row = len(existing_values) + 2
    inserted_count = 0

    for key in pending_order:
        normalized_row = pending_new[key]

        if reusable_empty_rows:
            target_row = reusable_empty_rows.pop(0)
        else:
            target_row = next_new_row
            next_new_row += 1

        formula_row = []
        formula_idx = target_row - 2
        if formula_idx >= 0 and formula_idx < len(existing_formulas):
            formula_row = _normalize_row(existing_formulas[formula_idx], data_columns)

        merged_row = []
        for col_idx in range(data_columns):
            formula_cell = formula_row[col_idx] if col_idx < len(formula_row) else ""
            if isinstance(formula_cell, str) and formula_cell.startswith("="):
                merged_row.append(formula_cell)
            else:
                merged_row.append(normalized_row[col_idx])

        updates.append(
            {
                "range": f"A{target_row}:{last_col_letter}{target_row}",
                "values": [merged_row],
            }
        )
        inserted_count += 1

    if updates:
        max_target_row = 1
        for item in updates:
            row_part = item["range"].split(":")[0][1:]
            max_target_row = max(max_target_row, int(row_part))

        if max_target_row > 320000:
            raise ValueError("Upsert would exceed 320k row safety limit")

        logger.info(f"Sending {len(updates)} batch updates to sheet")
        sheet.batch_update(
            updates,
            value_input_option="USER_ENTERED",
        )

    logger.info(
        f"Upsert complete for {spreadsheet} -> {worksheet}: "
        f"updated={update_count}, inserted={inserted_count}"
    )