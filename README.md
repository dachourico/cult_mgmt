# Cultivation Management Suite

A PostgreSQL-backed desktop application for tracking cannabis plant batches from
clone through harvest. The interface provides a facility dashboard, room and
strain management, batch movement, and actionable cultivation tasks.

## Features

- Live dashboard with active batches, plant count, rooms, and open tasks
- Clone, veg, flower, and dry room management
- Batch creation, editing, movement, harvest, completion, and history
- Phase-day calculation for every active batch
- Reusable strain library
- Dated room/batch tasks with overdue and completion states
- Facility phase-duration settings
- Validated forms, friendly database errors, and protected destructive actions

## Run the desktop app

1. Create `.env` in the project root and set your PostgreSQL connection string:

   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/database_name
   ```

2. Activate the existing virtual environment (or create one) and install the
   database dependencies:

   ```bash
   python -m venv .venv
   .venv/bin/pip install psycopg python-dotenv
   ```

3. Launch the GUI:

   ```bash
   .venv/bin/python run_gui.py
   ```

The desktop interface uses the official PySide6 bindings for Qt. Install the
dependencies with `.venv/bin/pip install psycopg python-dotenv PySide6`. If
PostgreSQL is offline, the app opens to a retry screen rather than crashing.

## Project structure

- `src/cult_mgmt/qt_gui.py` — modern Qt desktop views, forms, and navigation
- `src/cult_mgmt/app_data.py` — GUI-safe PostgreSQL operations
- `src/cult_mgmt/repositories/` — original repository layer
- `src/cult_mgmt/services/` — cultivation scheduling logic
- `run_gui.py` — development launcher
