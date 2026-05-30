# WineShop Demo

A small Flask website for a wineshop with owner and worker roles and a PostgreSQL backend.

## Features
- Login page with role-based access
- Owner dashboard with wine creation and price management
- Worker dashboard with shop and wine pricing view
- Multiple shops with different prices per wine

## Setup
1. Install Python dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
2. Create a PostgreSQL database and update `DATABASE_URL` if needed.
   Copy the example file to `.env`:
   ```powershell
   copy .env.example .env
   ```
   Then edit `.env` to set your connection and secret:
   ```text
   DATABASE_URL=postgresql+pg8000://postgres:your_password@localhost:5432/wineshop
   SECRET_KEY=your-secret-key
   ```
3. Initialize database and sample data:
   ```bash
   python setup_db.py
   ```
4. Run the app:
   ```bash
   python app.py
   ```
5. Open `http://127.0.0.1:5000` in your browser.

## Default accounts
- `owner` / `ownerpass`
- `worker` / `workerpass`

## Notes
- The app uses Flask templates for support pages.
- Owners can update prices, add wines, and add shops.
- Workers can view shops and pricing only.
