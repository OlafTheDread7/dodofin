# make_sample_data.py
# Builds a demo database full of made-up data, so you can try DoDoFin
# without your own bank export. Nothing in it is real.
#
#   python make_sample_data.py                 # sample/transactions.csv and demo.db
#   python make_sample_data.py --months 12 --seed 7 --db demo.db
#
# Then point the app at it:
#   DODOFIN_DB=demo.db python main.py           (PowerShell: $env:DODOFIN_DB = "demo.db"; python main.py)

import argparse
import csv
import datetime
import os
import random
import sys

# Recurring bills: (day of month, description, amount, category)
MONTHLY = [
    (1, "Maple Street Apartments", 1250.00, "Rent/Mortgage"),
    (5, "City Power & Light", None, "Utilities"),
    (8, "Riverbend Internet", 64.99, "Internet"),
    (12, "Sparrow Mobile", 45.00, "Mobile Phone"),
    (14, "Ironworks Gym", 29.99, "Gym"),
    (18, "Example Auto Insurance", 118.40, "Auto Insurance"),
    (21, "Streamly Subscription", 15.49, "Subscriptions"),
]

# Everyday spending: (description, low, high, category, visits per month)
EVERYDAY = [
    ("Corner Market", 18, 140, "Groceries", 6),
    ("Fresh Fields Grocery", 35, 190, "Groceries", 2),
    ("Blue Kettle Coffee", 4, 11, "Coffee Shops", 8),
    ("Northside Fuel", 28, 62, "Gas", 4),
    ("Lucky Noodle", 14, 48, "Restaurants", 3),
    ("Burger Barn", 8, 19, "Fast Food", 3),
    ("Bargain Mart", 12, 95, "Shopping", 2),
    ("Main St Pharmacy", 6, 40, "Pharmacy", 1),
    ("Paws & Claws Pet Supply", 20, 70, "Pets", 1),
    ("Cineplex 8", 12, 34, "Entertainment", 1),
]

# A few rows arrive with no category, so the categorize step has something to do.
UNCATEGORIZED = [
    ("POS PURCHASE 4471 HARDWARE", 9, 85),
    ("ONLINE TRANSFER REF 20931", 50, 300),
    ("SQ *FARMERS MARKET", 7, 30),
]

DEBTS = [
    # name, lender, balance, APR, minimum payment
    ("Rewards Visa", "Example Bank", "3850.00", "24.99", "95.00"),
    ("Car loan", "Example Credit Union", "11200.00", "6.90", "285.00"),
    ("Furniture loan", "Example Home Store", "900.00", "9.99", "45.00"),
]


def month_starts(months, today):
    first = today.replace(day=1)
    out = []
    for i in range(months, 0, -1):
        y, m = first.year, first.month - i
        while m <= 0:
            m += 12
            y -= 1
        out.append(datetime.date(y, m, 1))
    return out


def build_rows(months, seed, today=None):
    rng = random.Random(seed)
    today = today or datetime.date.today()
    rows = []
    for start in month_starts(months, today):
        # Paid twice a month
        for day in (1, 15):
            rows.append((start.replace(day=day), "Paycheck - Example Employer Inc", 2140.00, "Paycheck"))
        for day, desc, amount, cat in MONTHLY:
            if amount is None:  # power bill moves with the season
                amount = round(rng.uniform(70, 185), 2)
            rows.append((start.replace(day=day), desc, -amount, cat))
        for desc, low, high, cat, visits in EVERYDAY:
            for _ in range(visits):
                day = rng.randint(1, 28)
                rows.append((start.replace(day=day), desc, -round(rng.uniform(low, high), 2), cat))
        for desc, low, high in UNCATEGORIZED:
            if rng.random() < 0.6:
                rows.append((start.replace(day=rng.randint(1, 28)), desc, -round(rng.uniform(low, high), 2), ""))
    rows.sort(key=lambda r: (r[0], r[1]))
    return rows


def write_csv(rows, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["Date", "Description", "Amount", "Category"])
        for date, desc, amount, cat in rows:
            w.writerow([date.isoformat(), desc, f"{amount:.2f}", cat])


def build_database(db_path, csv_path):
    # The app's modules read DODOFIN_DB when they're imported, so set it first.
    os.environ["DODOFIN_DB"] = db_path
    import database_setup
    import db_utils
    from csv_importer import import_csv
    from decimal import Decimal

    database_setup.main()
    conn = db_utils.create_connection(db_path)
    import_csv(conn, csv_path)
    existing = {d["name"] for d in db_utils.get_debts(conn)}
    for name, lender, bal, apr, minimum in DEBTS:
        if name not in existing:
            db_utils.add_debt(conn, name, lender, Decimal(bal), Decimal(apr), Decimal(minimum))
    conn.close()


def main(argv=None):
    ap = argparse.ArgumentParser(description="Make a demo DoDoFin database from made-up data.")
    ap.add_argument("--months", type=int, default=6)
    ap.add_argument("--seed", type=int, default=2025)
    ap.add_argument("--csv", default=os.path.join("sample", "transactions.csv"))
    ap.add_argument("--db", default="demo.db", help="database to create (never your finance.db by default)")
    ap.add_argument("--csv-only", action="store_true", help="write the CSV and stop")
    args = ap.parse_args(argv)

    rows = build_rows(args.months, args.seed)
    write_csv(rows, args.csv)
    print(f"Wrote {len(rows)} made-up transactions to {args.csv}")
    if args.csv_only:
        return 0
    if os.path.basename(args.db) == "finance.db" and os.path.exists(args.db):
        print("Refusing to add demo data to an existing finance.db. Pick another --db.")
        return 1
    build_database(args.db, args.csv)
    print(f"\nDemo database ready: {args.db}")
    print(f"Run the app on it with DODOFIN_DB={args.db} python main.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
