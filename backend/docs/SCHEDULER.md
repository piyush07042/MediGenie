Scheduler integration options for MediGenie

1) In-app scheduler (APScheduler)
- Controlled via environment variables or .env using `app/core/config.py` settings:
  - `SCHEDULER_ENABLED=true`
  - `SCHEDULER_INTERVAL_SECONDS=3600`  # run every hour
  - `SCHEDULER_OUT_DIR=temp_reports`
  - `SCHEDULER_DRY_RUN=true`
  - `SCHEDULER_PATIENT_ID` optional single patient id

Start the FastAPI app normally. If enabled, APScheduler will start at app startup and schedule `run_reports()`.

2) Windows Task Scheduler (schtasks)
- One-off scheduling via `schtasks`:

```powershell
schtasks /Create /SC HOURLY /MO 1 /TN "MediGenie Reports" /TR "\"C:\Path\To\Python.exe\" -m app.cli.generate_reports --out-dir C:\Path\to\project\temp_reports"
```

- Or use Task Scheduler UI to point at the command:

```powershell
C:\Path\To\Python.exe -m app.cli.generate_reports --out-dir C:\Path\to\project\temp_reports
```

3) systemd timer (Linux)
- Create `/etc/systemd/system/medigenie-report.service`:

```ini
[Unit]
Description=MediGenie Report Generator

[Service]
Type=oneshot
WorkingDirectory=/opt/medigenie/backend
ExecStart=/usr/bin/python3 -m app.cli.generate_reports --out-dir /opt/medigenie/backend/temp_reports
```

- Create `/etc/systemd/system/medigenie-report.timer`:

```ini
[Unit]
Description=Run MediGenie report generator hourly

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now medigenie-report.timer
```

Notes
- In-app APScheduler is cross-platform and suitable for containers; OS schedulers are better for single-machine system-level control and restarts.
- Ensure the Python environment used by the scheduler has the same dependencies and access to the database and application configuration.
