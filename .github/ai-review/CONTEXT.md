# dodofin: notes for the reviewer

Public repo. A terminal personal finance app on Python and SQLite. Nothing here deploys.

- `finance.db` (or `DODOFIN_DB`) is the user's local database; every `.db` and `.csv` is gitignored. `make_sample_data.py` builds a demo database from made-up data and refuses to write into an existing `finance.db`.
- SQL takes values through placeholders. A couple of queries build an `IN (?, ?, ...)` list from a count of placeholders, which is intended.

What matters most: real financial data getting committed, and SQL built from input.
