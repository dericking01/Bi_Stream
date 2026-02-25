from apscheduler.schedulers.blocking import BlockingScheduler
from app.report_engine import run_all
from app.config import REPORTS

def start():
    scheduler = BlockingScheduler(timezone="Africa/Dar_es_Salaam")

    scheduler.add_job(
        lambda: run_all(REPORTS),
        "cron",
        minute="*/15",  # Every 15 minutes
    )

    scheduler.start()