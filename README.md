# Simple Budget App

A basic budget tracking application for managing daily finances.

## Development

This application was built using **quickapp**, a coding agent I built for DataTalksClub AI Dev Tools Zoomcamp module 4. The project evolved through several stages:
1.  **Initial State**: A minimal "barebone" application structure.
2.  **Iteration**: Successive prompts were used to build out the features.
3.  **Expansion**: CRUD actions for transactions and category management were added iteratively until the app was fully functional.

## Features

- **Transactions**: Add new records with amounts, dates, and descriptions.
- **Categories**: Organize spending into custom categories.
- **Summary**: View total spending per category on the main dashboard.
- **Management**: Delete transactions or move them between categories.

## Tech Stack

- **Framework**: FastAPI (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Templates**: Jinja2 HTML templates

## Running Locally

1. Install dependencies using `uv`:
   ```bash
   uv sync
   ```
2. Start the server:
   ```bash
   uv run main.py
   ```
3. Access the app at `http://localhost:8000`.
