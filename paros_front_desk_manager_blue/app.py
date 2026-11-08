import sqlite3
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / "paros_front_desk.db"

st.set_page_config(
    page_title="Paros Front Desk Manager",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Database ----------
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_number TEXT UNIQUE NOT NULL,
                room_type TEXT NOT NULL,
                capacity INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'Available'
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guest_name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                room_number TEXT NOT NULL,
                check_in TEXT NOT NULL,
                check_out TEXT NOT NULL,
                guests INTEGER NOT NULL,
                total_price REAL NOT NULL DEFAULT 0,
                paid REAL NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'Confirmed'
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guest_name TEXT NOT NULL,
                amount REAL NOT NULL,
                payment_date TEXT NOT NULL,
                method TEXT NOT NULL,
                note TEXT
            )
        """)
        room_count = conn.execute("SELECT COUNT(*) FROM rooms").fetchone()[0]
        if room_count == 0:
            rooms = []
            for floor in range(1, 4):
                for number in range(1, 9):
                    room_no = f"{floor}{number:02d}"
                    room_type = "Double" if number <= 5 else ("Suite" if number in (6, 7) else "Family")
                    capacity = 2 if room_type == "Double" else (3 if room_type == "Suite" else 4)
                    rooms.append((room_no, room_type, capacity, "Available"))
            conn.executemany(
                "INSERT INTO rooms (room_number, room_type, capacity, status) VALUES (?, ?, ?, ?)",
                rooms,
            )
        reservation_count = conn.execute("SELECT COUNT(*) FROM reservations").fetchone()[0]
        if reservation_count == 0:
            today = date.today()
            demo = [
                ("Maria Papadopoulou", "maria@example.com", "", "101",
                 (today + timedelta(days=1)).isoformat(), (today + timedelta(days=4)).isoformat(),
                 2, 420.0, 200.0, "Confirmed"),
                ("John Smith", "john@example.com", "", "202",
                 (today + timedelta(days=2)).isoformat(), (today + timedelta(days=5)).isoformat(),
                 2, 310.0, 310.0, "Confirmed"),
                ("Anna Rossi", "anna@example.com", "", "103",
                 (today + timedelta(days=3)).isoformat(), (today + timedelta(days=6)).isoformat(),
                 2, 290.0, 100.0, "Pending"),
                ("David Wilson", "david@example.com", "", "201",
                 (today + timedelta(days=4)).isoformat(), (today + timedelta(days=7)).isoformat(),
                 1, 360.0, 360.0, "Confirmed"),
            ]
            conn.executemany("""
                INSERT INTO reservations
                (guest_name,email,phone,room_number,check_in,check_out,guests,total_price,paid,status)
                VALUES (?,?,?,?,?,?,?,?,?,?)
            """, demo)
            conn.executemany("""
                INSERT INTO payments (guest_name,amount,payment_date,method,note)
                VALUES (?,?,?,?,?)
            """, [
                ("Maria Papadopoulou", 200.0, today.isoformat(), "Card", "Deposit"),
                ("John Smith", 310.0, today.isoformat(), "Cash", "Full payment"),
                ("Anna Rossi", 100.0, today.isoformat(), "Card", "Deposit"),
            ])

def query_df(sql, params=()):
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn, params=params)

def execute(sql, params=()):
    with get_connection() as conn:
        conn.execute(sql, params)
        conn.commit()

init_db()

# ---------- Styling ----------
st.markdown("""
<style>
    :root { --navy: #183653; --blue: #2f80d5; --pale: #e8f3ff; --line: #d7e7f8; }
    .stApp { background: #f7fbff; color: #183653; }
    [data-testid="stSidebar"] { background: #183653; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .block-container { padding-top: 1.6rem; padding-bottom: 2rem; }
    h1, h2, h3, h4 { color: #183653 !important; }
    div[data-testid="stMetric"] {
        background: #ffffff; border: 1px solid #d7e7f8; border-radius: 15px;
        padding: 16px 18px; box-shadow: 0 2px 8px rgba(24,54,83,.04);
    }
    div[data-testid="stMetric"] label { color: #496782 !important; }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #183653 !important; }
    div[data-testid="stForm"] { background: #ffffff; border: 1px solid #d7e7f8; padding: 18px; border-radius: 14px; }
    .welcome {
        background: linear-gradient(110deg, #e8f3ff, #ffffff);
        border: 1px solid #d7e7f8; border-radius: 16px; padding: 22px;
        color: #183653; min-height: 140px;
    }
    .small-muted { color: #617b94; font-size: .92rem; }
    .stButton button, .stFormSubmitButton button {
        background: #2f80d5; color: white; border: 0; border-radius: 9px;
    }
    .stButton button:hover, .stFormSubmitButton button:hover {
        background: #183653; color: white; border: 0;
    }
    div[data-baseweb="tab-list"] { gap: 8px; }
    div[data-baseweb="tab"] { color: #183653; }
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar navigation ----------
with st.sidebar:
    st.markdown("<div style='text-align:center;padding:12px 0 24px'>"
                "<div style='font-size:42px'>⌂</div>"
                "<div style='font-family:Georgia,serif;font-size:29px;letter-spacing:3px'>PAROS</div>"
                "<div style='font-size:12px;letter-spacing:1px'>FRONT DESK MANAGER</div>"
                "</div>", unsafe_allow_html=True)
    page = st.radio(
        "Navigation",
        ["Dashboard", "Reservations", "Rooms", "Guests", "Payments", "Reports", "Settings"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption("Paros, Greece")

# ---------- Shared data ----------
today = date.today()
rooms_df = query_df("SELECT * FROM rooms ORDER BY room_number")
reservations_df = query_df("SELECT * FROM reservations ORDER BY check_in")
payments_df = query_df("SELECT * FROM payments ORDER BY payment_date DESC, id DESC")

def money(value):
    return f"€{float(value):,.2f}"

def page_title(title, subtitle=None):
    st.title(title)
    if subtitle:
        st.markdown(f"<div class='small-muted'>{subtitle}</div>", unsafe_allow_html=True)

def reservation_table(df):
    if df.empty:
        st.info("No reservations found.")
        return
    display = df.copy()
    display["total_price"] = display["total_price"].map(money)
    display["paid"] = display["paid"].map(money)
    display = display.rename(columns={
        "guest_name": "Guest", "room_number": "Room", "check_in": "Check-in",
        "check_out": "Check-out", "guests": "Guests", "total_price": "Total",
        "paid": "Paid", "status": "Status"
    })
    keep = [c for c in ["Guest", "Room", "Check-in", "Check-out", "Guests", "Total", "Paid", "Status"] if c in display.columns]
    st.dataframe(display[keep], use_container_width=True, hide_index=True)

# ---------- Dashboard ----------
if page == "Dashboard":
    page_title("Paros Front Desk Manager", "Manage • Organize • Welcome")
    active_today = reservations_df[
        (reservations_df["check_in"] <= today.isoformat()) &
        (reservations_df["check_out"] > today.isoformat()) &
        (reservations_df["status"] != "Cancelled")
    ] if not reservations_df.empty else reservations_df
    arrivals = reservations_df[reservations_df["check_in"] == today.isoformat()] if not reservations_df.empty else reservations_df
    departures = reservations_df[reservations_df["check_out"] == today.isoformat()] if not reservations_df.empty else reservations_df
    occupied = len(active_today)
    total_rooms = len(rooms_df)
    occupancy = (occupied / total_rooms * 100) if total_rooms else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Rooms", total_rooms)
    c2.metric("Today's Arrivals", len(arrivals))
    c3.metric("Today's Departures", len(departures))
    c4.metric("Occupancy Rate", f"{occupancy:.0f}%")

    left, right = st.columns([1.6, 1])
    with left:
        st.subheader("Occupancy Overview")
        if not reservations_df.empty:
            chart_data = []
            for offset in range(7):
                day = today + timedelta(days=offset)
                count = reservations_df[
                    (reservations_df["check_in"] <= day.isoformat()) &
                    (reservations_df["check_out"] > day.isoformat()) &
                    (reservations_df["status"] != "Cancelled")
                ].shape[0]
                chart_data.append({"Date": day.strftime("%a %d"), "Occupancy": round(count / total_rooms * 100) if total_rooms else 0})
            st.line_chart(pd.DataFrame(chart_data).set_index("Date"), y="Occupancy", color="#2f80d5")
        else:
            st.info("Add reservations to see occupancy.")
    with right:
        st.subheader("Upcoming Reservations")
        upcoming = reservations_df[reservations_df["check_in"] >= today.isoformat()].head(5)
        if upcoming.empty:
            st.info("No upcoming reservations.")
        else:
            for _, row in upcoming.iterrows():
                st.markdown(
                    f"**{row['guest_name']}**  ·  Room {row['room_number']}  \n"
                    f"<span class='small-muted'>{row['check_in']} → {row['check_out']}</span>",
                    unsafe_allow_html=True,
                )
                st.divider()

    a, b, c = st.columns([1, 1.2, 1.2])
    with a:
        st.subheader("Rooms Status")
        room_counts = rooms_df["status"].value_counts() if not rooms_df.empty else pd.Series(dtype=int)
        st.metric("Available", int(room_counts.get("Available", 0)))
        st.metric("Occupied", occupied)
        st.metric("Out of Order", int(room_counts.get("Out of Order", 0)))
    with b:
        st.subheader("Recent Payments")
        if payments_df.empty:
            st.info("No payments recorded.")
        else:
            for _, row in payments_df.head(4).iterrows():
                st.write(f"**{row['guest_name']}**")
                st.caption(f"{money(row['amount'])} · {row['payment_date']} · {row['method']}")
    with c:
        st.markdown("<div class='welcome'><h3>Welcome to Paros!</h3>"
                    "<p>Calm, clear and organized front desk operations.</p>"
                    "<span class='small-muted'>Smooth operations. Happy guests.</span></div>",
                    unsafe_allow_html=True)

# ---------- Reservations ----------
elif page == "Reservations":
    page_title("Reservations", "Create and manage guest bookings.")
    with st.expander("＋ Add a reservation", expanded=False):
        with st.form("add_reservation", clear_on_submit=True):
            col1, col2 = st.columns(2)
            guest = col1.text_input("Guest full name")
            email = col1.text_input("Email")
            phone = col1.text_input("Phone")
            room_options = rooms_df["room_number"].tolist()
            room = col2.selectbox("Room", room_options if room_options else ["No rooms"])
            check_in = col2.date_input("Check-in", value=today + timedelta(days=1))
            check_out = col2.date_input("Check-out", value=today + timedelta(days=3))
            guests = col2.number_input("Number of guests", min_value=1, max_value=10, value=2)
            total = col1.number_input("Total price (€)", min_value=0.0, step=10.0)
            paid = col1.number_input("Amount paid (€)", min_value=0.0, step=10.0)
            submitted = st.form_submit_button("Save reservation")
            if submitted:
                if not guest.strip():
                    st.error("Please enter the guest's name.")
                elif check_out <= check_in:
                    st.error("Check-out must be after check-in.")
                elif paid > total:
                    st.error("The paid amount cannot exceed the total price.")
                else:
                    conflict = query_df("""
                        SELECT COUNT(*) AS n FROM reservations
                        WHERE room_number = ? AND status != 'Cancelled'
                        AND check_in < ? AND check_out > ?
                    """, (room, check_out.isoformat(), check_in.isoformat())).iloc[0]["n"]
                    if conflict:
                        st.error("This room already has a reservation during those dates.")
                    else:
                        execute("""
                            INSERT INTO reservations
                            (guest_name,email,phone,room_number,check_in,check_out,guests,total_price,paid,status)
                            VALUES (?,?,?,?,?,?,?,?,?,'Confirmed')
                        """, (guest.strip(), email, phone, room, check_in.isoformat(),
                              check_out.isoformat(), int(guests), total, paid))
                        st.success("Reservation saved.")
                        st.rerun()

    st.subheader("All Reservations")
    status_filter = st.selectbox("Filter by status", ["All", "Confirmed", "Pending", "Cancelled"])
    view = query_df("SELECT * FROM reservations ORDER BY check_in")
    if status_filter != "All":
        view = view[view["status"] == status_filter]
    reservation_table(view)

    if not view.empty:
        st.subheader("Update reservation status")
        selected_id = st.selectbox("Reservation ID", view["id"].tolist())
        new_status = st.selectbox("New status", ["Confirmed", "Pending", "Cancelled"])
        if st.button("Update status"):
            execute("UPDATE reservations SET status=? WHERE id=?", (new_status, int(selected_id)))
            st.success("Reservation updated.")
            st.rerun()

# ---------- Rooms ----------
elif page == "Rooms":
    page_title("Rooms", "Room inventory and housekeeping status.")
    st.dataframe(rooms_df.rename(columns={
        "room_number": "Room", "room_type": "Type", "capacity": "Capacity", "status": "Status"
    })[["Room", "Type", "Capacity", "Status"]], use_container_width=True, hide_index=True)
    st.subheader("Change room status")
    if not rooms_df.empty:
        selected_room = st.selectbox("Room number", rooms_df["room_number"].tolist())
        selected_status = st.selectbox("Status", ["Available", "Occupied", "Cleaning", "Out of Order"])
        if st.button("Save room status"):
            execute("UPDATE rooms SET status=? WHERE room_number=?", (selected_status, selected_room))
            st.success(f"Room {selected_room} updated.")
            st.rerun()

# ---------- Guests ----------
elif page == "Guests":
    page_title("Guests", "Guest directory based on reservation records.")
    guests_df = query_df("""
        SELECT guest_name, email, phone, COUNT(*) AS bookings,
               SUM(total_price) AS total_spend
        FROM reservations GROUP BY guest_name, email, phone ORDER BY guest_name
    """)
    if guests_df.empty:
        st.info("Guest records will appear when reservations are added.")
    else:
        guests_df["total_spend"] = guests_df["total_spend"].map(money)
        guests_df = guests_df.rename(columns={
            "guest_name": "Guest", "email": "Email", "phone": "Phone",
            "bookings": "Bookings", "total_spend": "Booking Value"
        })
        st.dataframe(guests_df, use_container_width=True, hide_index=True)

# ---------- Payments ----------
elif page == "Payments":
    page_title("Payments", "Record and review payments. This app does not process card payments.")
    with st.expander("＋ Record a payment"):
        with st.form("add_payment", clear_on_submit=True):
            guest_names = reservations_df["guest_name"].dropna().unique().tolist()
            guest_name = st.selectbox("Guest", guest_names if guest_names else ["Other"])
            amount = st.number_input("Amount (€)", min_value=0.01, step=10.0)
            payment_date = st.date_input("Payment date", value=today)
            method = st.selectbox("Method", ["Cash", "Card", "Bank Transfer", "Other"])
            note = st.text_input("Note")
            submitted = st.form_submit_button("Save payment")
            if submitted:
                execute("INSERT INTO payments (guest_name,amount,payment_date,method,note) VALUES (?,?,?,?,?)",
                        (guest_name, amount, payment_date.isoformat(), method, note))
                st.success("Payment recorded.")
                st.rerun()
    current_payments = query_df("SELECT * FROM payments ORDER BY payment_date DESC, id DESC")
    if not current_payments.empty:
        current_payments["amount"] = current_payments["amount"].map(money)
        current_payments = current_payments.rename(columns={
            "guest_name": "Guest", "amount": "Amount", "payment_date": "Date",
            "method": "Method", "note": "Note", "id": "ID"
        })
        st.dataframe(current_payments[["Date", "Guest", "Amount", "Method", "Note"]], use_container_width=True, hide_index=True)
    else:
        st.info("No payments recorded.")

# ---------- Reports ----------
elif page == "Reports":
    page_title("Reports", "Simple operational summaries and CSV exports.")
    all_res = query_df("SELECT * FROM reservations")
    col1, col2, col3 = st.columns(3)
    col1.metric("Reservations", len(all_res))
    col2.metric("Booking revenue", money(all_res["total_price"].sum()) if not all_res.empty else "€0.00")
    col3.metric("Recorded payments", money(payments_df["amount"].sum()) if not payments_df.empty else "€0.00")
    if not all_res.empty:
        st.subheader("Reservations report")
        st.dataframe(all_res, use_container_width=True, hide_index=True)
        st.download_button("Download reservations CSV", all_res.to_csv(index=False).encode("utf-8-sig"),
                           "reservations_report.csv", "text/csv")
    if not payments_df.empty:
        st.subheader("Payments report")
        st.download_button("Download payments CSV", payments_df.to_csv(index=False).encode("utf-8-sig"),
                           "payments_report.csv", "text/csv")

# ---------- Settings ----------
elif page == "Settings":
    page_title("Settings", "Basic information about this demo application.")
    st.markdown("""
    **Paros Front Desk Manager**

    - Application type: Educational hotel front-desk management demo
    - Database: Local SQLite file (`paros_front_desk.db`)
    - Currency: Euro (€)
    - Sample data: Fictional demonstration records
    """)
    st.warning("Use fictional guest data only. Do not store passport numbers, payment-card details, or other sensitive personal information.")
    st.info("This is a learning project, not a production hotel PMS. It does not process payments or synchronize with booking platforms.")
