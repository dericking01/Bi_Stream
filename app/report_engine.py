import time
from app.db import execute_query
from app.sheets import upsert_rows
from app.state_manager import get_last_execution, update_last_execution
from app.logger import get_logger

logger = get_logger()

def run_report(report):
    logger.info(f"Starting {report['name']}")

    last_exec = get_last_execution(report["name"])

    with open(report["sql_file"], "r") as f:
        sql = f.read()

    sql = sql.replace("{{LAST_EXECUTION}}", last_exec)

    rows = execute_query(sql)

    if not rows:
        logger.info("No new data. Skipping.")
        return

    if report["mode"] == "upsert":
        upsert_rows(
            report["spreadsheet"],
            report["worksheet"],
            rows,
            report["data_columns"],
            report["key_columns"],
            logger
        )
    else:
        raise ValueError(f"Unsupported report mode: {report['mode']}")

    update_last_execution(report["name"])
    logger.info(f"{report['name']} completed")

def run_all(reports):
    for idx, report in enumerate(reports):
        if idx > 0:
            logger.info("Sleeping 120 seconds...")
            time.sleep(120)

        try:
            run_report(report)
        except Exception as e:
            logger.error(f"{report['name']} failed: {e}")