# DoDoFin

A small personal finance app I built in 2025 to get a handle on my own spending and debt. It runs in the terminal on Python and SQLite: import a bank CSV, categorize what came in, set budgets from what you actually spend, and plan paying off debt with the snowball or avalanche method.

This is a clean copy of the 2025 project. It ships with a generator that builds a demo database out of made-up data, so you can try everything without a bank export.

## Try it on made-up data

```bash
pip install -r requirements.txt
python make_sample_data.py
```

That writes six months of fake bank transactions to `sample/transactions.csv` (rent, bills, groceries, coffee, two paychecks a month, and a few rows with no category) and builds `demo.db` with them plus three fake debts. Then run the app on it:

```bash
DODOFIN_DB=demo.db python main.py                  # macOS / Linux
$env:DODOFIN_DB = "demo.db"; python main.py        # Windows PowerShell
```

With $700 a month toward the demo debts, the payoff planner shows the avalanche order saving about $105 in interest over the snowball order ($1,656 against $1,761, 26 months either way).

## Use it for real

```bash
python database_setup.py      # creates finance.db with the default categories
python main.py
```

The menu:

| Option | What it does |
|---|---|
| 1 Import CSV | Reads a bank export with `Date`, `Description`, `Amount` and an optional `Category` column. Negative amounts are spending, positive are income. Text amounts like `-$1,234.56` work. Importing the same file twice updates rows instead of duplicating them. |
| 2 Categorize | Walks through anything without a category, one transaction at a time. You can add a category on the spot. Each one you file earns a point. |
| 3 Manage Budget | Set or remove a monthly limit per category. |
| 4 View Summary | This month's spending against each budget. |
| 5 Auto-Budget | Sets every budget to your average monthly spend in that category, leaving out income, transfers, card payments and gifts. |
| 6 Tighten Budget | Sets the discretionary budgets (eating out, coffee, shopping, entertainment and the like) to the least you've spent on each in a month, for when money is tight. |
| 7 Manage Debts | Track balances, rates and minimums, and simulate payoff month by month with either strategy. |
| 8 Debt Affordability | Takes your monthly income, subtracts budgets and minimum payments (without counting a card payment twice), and tells you what's left for paying debt down faster. |

`list_transactions.py` shows recent transactions with their IDs, and `python delete_transactions.py 12 13` removes specific ones after asking.

The database is `finance.db` in the current folder unless `DODOFIN_DB` says otherwise. `.gitignore` keeps every `.db` and `.csv` out of git.

## Tests

```bash
python -m unittest discover -s tests -v
```

They build the demo database in a temp folder and check the import (every row lands, re-importing adds nothing, dollar-sign amounts parse), the uncategorized count, that the generator is repeatable, that avalanche never costs more interest than snowball, and that the generator refuses to write into a real `finance.db`.

## Notes

- Amounts are stored as floats for transactions and as text for debts, and the payoff math runs in `Decimal`. A rewrite would use integer cents everywhere.
- There was an early Tkinter dashboard. It was never finished, so it isn't in this copy.

## License

MIT. See `LICENSE`.
