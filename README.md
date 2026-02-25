# BIStream 🚀  
Secure Internal BI Data Pipeline Engine  

BIStream is a containerized ETL orchestration service that securely streams data 
from PostgreSQL into Google Sheets for real-time analytics consumption 
via Looker Studio — without exposing the production database.

It eliminates manual exports, copy-paste workflows, and insecure direct BI connections.

---

## 🧠 What BIStream Solves

Traditional workflow:
DB → Manual export → Copy → Google Sheets → Looker Studio

BIStream workflow:
DB → Secure Incremental ETL → Google Sheets → Looker Studio (Auto-refresh)

✔ No direct DB access for analysts  
✔ No manual extraction  
✔ No data duplication  
✔ No formula breakage  
✔ No hardcoded dates  
✔ Fully incremental updates  
✔ Scheduled orchestration  
✔ Containerized & production ready  

---

## 🏗 Architecture
PostgreSQL
↓
BIStream (Docker + APScheduler)
↓
Google Sheets (Service Account)
↓
Looker Studio Dashboards


---

## ⚙️ Core Features

- 🔁 Incremental loading (based on `updated_at`)
- 📅 Auto-filtered by `CURRENT_DATE`
- 🕒 Scheduled every 15 minutes
- ⏱ 2-minute spacing between report executions
- 🧠 Smart state tracking (`state.json`)
- 📊 Multi-sheet, multi-file support
- 🔒 No direct DB exposure to BI users
- 🧾 Formula-safe sheet writes
- 🚦 320k row safety cap
- 🗂 SQL-per-report architecture
# BIStream 🚀 — Beautiful, Secure BI Streaming

BIStream securely streams data from PostgreSQL into Google Sheets for fast,
formula-safe analytics in Looker Studio — without exposing your production DB.

Key goals: incremental, scheduled, containerized, and secure.

---

**Highlights**

- **Incremental ETL:** only new/updated rows (based on `updated_at`) are pulled.
- **Formula-safe writes:** updates append without breaking sheet formulas.
- **Scheduled & resilient:** APScheduler-driven runs with spacing safeguards.
- **Container-first:** runs in Docker for easy deployment.
- **Secure by design:** service account for Sheets, DB creds in `.env` only.

---

**Quick Start**

1. Clone the repo

```bash
git clone git@github.com:dericking01/Bi_Stream.git
cd Bi_Stream
```

2. Create `.env` with your DB credentials

```
DB_HOST=your_host
DB_PORT=5432
DB_NAME=your_db
DB_USER=your_user
DB_PASSWORD=your_password
```

3. Add `service-account.json` (Google service account) to project root

4. Build & run with Docker Compose

```bash
docker compose up -d --build
```

5. Watch the logs

```bash
docker logs -f bi_stream_engine
```

---

**Architecture (overview)**

PostgreSQL → BIStream (Docker + APScheduler) → Google Sheets → Looker Studio

---

**Core Features**

- Incremental loading using `updated_at`.
- Per-report SQL files (easy to extend).
- State tracking in `state.json` for safe, idempotent runs.
- Per-report throttling (min spacing between runs).
- Multi-sheet and multi-file reporting.
- Safety cap on writes to protect Sheets (320k row guard).

---

**How Incremental Loading Works**

1. Each report reads its last run timestamp from `state.json`.
2. `{{LAST_EXECUTION}}` is injected into the report SQL.
3. Only new/changed rows are pulled and appended safely.
4. `state.json` is updated with the latest execution timestamp.

---

**Files of Interest**

- `app/` — main application code and scheduler.
- `reports/` — SQL per-report files.
- `state.json` — stores last-execution timestamps.
- `service-account.json` — Google credentials (place in project root).

---

**Environment & Security**

- Keep DB credentials in `.env` (do not commit).
- `service-account.json` should be stored securely and given Editor
	access to target Sheets only.

---

**Deployment Tips**

- Use Docker Compose for production; the default schedule runs every 15 minutes.
- For cloud deployments, mount secure secrets and limit network access to the
	DB from the BIStream container only.

---

**Want to extend reports?**

1. Add a SQL file to `reports/`.
2. Configure any report-specific settings in `state.json`.
3. Restart the container or let the scheduler pick it up on the next run.

---

**Support & Contribution**

If you find issues or want to contribute, please open an issue or PR in the
original repository: git@github.com:dericking01/Bi_Stream.git

---

Made with ❤️ for safe, fast internal BI.