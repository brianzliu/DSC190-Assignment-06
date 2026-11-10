# nldate

`nldate.parse()` turns English date expressions into `datetime.date` objects.
It uses only the Python standard library and requires Python 3.10 or newer.

```python
from datetime import date
from nldate import parse

parse("5 days before December 1st, 2025")  # date(2025, 11, 26)
parse("next Tuesday", today=date(2025, 3, 12))  # date(2025, 3, 18)
parse("two weeks from tomorrow", today=date(2025, 3, 12))  # date(2025, 3, 27)
parse("1 year and 2 months after yesterday", today=date(2025, 3, 12))
# date(2026, 5, 11)
```

Omitting `today` uses the current local date. Empty, unrecognized, impossible,
and out-of-range dates raise `ValueError`.

## Supported expressions

- Numeric dates such as `2025-12-01`, `12/1/2025`, and `12/1`.
- Month names and abbreviations such as `December 1st, 2025`, `1 Dec 2025`,
  `the first of December`, and `December twenty-fifth 2025`.
- `today`, `tomorrow`, `yesterday`, `the day after tomorrow`, and
  `the day before yesterday`.
- `in 3 days`, `two weeks ago`, `a month from now`, `next year`, and `last month`.
- Compound offsets such as `1 year, 2 months and 3 days after next Tuesday`.
  Anchors may themselves be relative expressions.
- Weekdays such as `next Tuesday`, `last Friday`, `this Monday`, and
  `Monday next week`.
- Month and year references such as `next January`, `May 5 next year`, and
  `the first of next month`.
- Period boundaries such as `end of next month`, `first day of this year`,
  and `start of next quarter`.
- Weekday occurrences such as `second Tuesday of April 2025` and
  `last Friday of next month`.
- Business days such as `in 3 business days` and `5 weekdays ago`.
- Common US holidays including `Christmas`, `Thanksgiving 2025`,
  `Memorial day`, and `last Halloween`.

Input is case insensitive and tolerates extra whitespace, ordinal suffixes,
and periods in month abbreviations. Counts may be digits or English words.
Supported duration units are days, weeks, fortnights, months, quarters, years,
decades, and business days.

## Date conventions

- Missing years use the reference year. A month without a day means its first day.
- Ambiguous numeric dates use US month/day order. If the first number exceeds 12,
  day/month order applies. Two-digit years 00 through 68 mean 2000 through 2068;
  69 through 99 mean 1969 through 1999.
- `next Tuesday` is strictly in the future, even on Tuesday. `last Tuesday` is
  strictly in the past. A bare weekday means its next occurrence, including today.
- `this Monday` means Monday in the current Monday-through-Sunday week.
- `next week`, `next month`, and `next year` shift the reference date by that
  amount. `start of next week` means the following Monday.
- Month and year arithmetic clamps the day to the target month's last valid day.
  January 31 plus one month is February 28, or February 29 in a leap year.
  Compound offsets apply the combined years and months first, then calendar days,
  then business days. Subtraction uses the same order with negative offsets.
- Business days exclude Saturdays and Sundays. They do not exclude holidays.
- Holiday names use US calendar conventions. Without a modifier or year, a holiday
  refers to the reference year. `next` and `last` select strictly future or past
  occurrences.

## Development

The project was created with `uv init --package nldate`. Its source lives in
`src/nldate/`. Install the package and development dependencies with:

```sh
uv sync
```

Run the required checks:

```sh
uv run pytest
uv run mypy src/
uv run ruff check
uv run ruff format --check
```

The tests cover date formats, nested offsets, leap years, month-end clamping,
invalid input, all weekday transitions across a leap year, and business-day
arithmetic checked against daily counting.
