# Paros Front Desk Manager

A beginner-friendly Python + Streamlit demo project for hotel front-desk operations.

## Features
- Dashboard with arrivals, departures, occupancy and upcoming reservations
- Add reservations and check for overlapping room dates
- Room inventory and room status updates
- Guest directory
- Payment records (record-keeping only; no payment processing)
- Reports and CSV exports
- Local SQLite database created automatically

## Run on Windows

1. Install Python 3.11 or newer.
2. Extract this ZIP file.
3. Open the extracted `paros_front_desk_manager_blue` folder in VS Code.
4. Open Terminal > New Terminal.
5. Run:

   ```powershell
   python -m pip install -r requirements.txt
   ```

6. Then run:

   ```powershell
   python -m streamlit run app.py
   ```

7. Open the local address shown in the terminal (usually http://localhost:8501).

Keep the terminal open while using the app. Press `Ctrl+C` in the terminal to stop it.

## Important
This is an educational portfolio project, not a production PMS. It uses fictional sample data. Do not enter real guest personal data, passport details, or payment-card information. Payments are only recorded; they are not processed.
