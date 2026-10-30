# DoDoFin

I built DoDoFin in 2025 to track spending and debt. It's a small personal finance app that runs in the terminal with Python and SQLite. It supports CSV import from a bank export, categorizing transactions, setting a budget from actual spending, and planning debt payoff with the snowball or avalanche method.

This is a clean copy of the 2025 project. The included generator builds a demo database out of made-up data, so you can try everything without a bank export.

## Try it on made-up data

```bash
pip install -r requirements.txt
python make_sample_data.py
```

This writes six months of fake bank transactions to `sample/transactions.csv`: rent, bills, groceries, coffee, two paychecks a month, and a few rows with no category. It also builds `demo.db` with those transactions and three fake debts. Run the app against that database:

```bash
DODOFIN_DB=demo.db python main.py                  # macOS / Linux
$env:DODOFIN_DB = "demo.db"; python main.py        # Windows PowerShell
```

With $700 a month going toward the demo debts, the payoff planner shows avalanche saving about $105 in interest compared with snowball. That's $1,656 against $1,761, with both taking 26 months.

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

`list_transactions.py` shows recent transactions and their IDs. `python delete_transactions.py 12 13` asks before removing specific transactions.

The app uses `finance.db` in the current folder unless you set `DODOFIN_DB` to something else. `.gitignore` keeps every `.db` and `.csv` out of git.

## Tests

```bash
python -m unittest discover -s tests -v
```

The tests build the demo database in a temp folder. They check that every imported row lands, importing again adds nothing, and dollar-sign amounts parse. They also check the uncategorized count, that the generator is repeatable, that avalanche never costs more interest than snowball, and that the generator refuses to write into a real `finance.db`.

## Notes

- Transactions store amounts as floats. Debts store them as text, and the payoff math runs in `Decimal`. I'd use integer cents everywhere in a rewrite.
- There was an early Tkinter dashboard. I never finished it, so it isn't in this copy.

## License

MIT. See `LICENSE`.
