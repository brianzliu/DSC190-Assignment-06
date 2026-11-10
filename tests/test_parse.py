"""Behavioral tests with fixed reference dates and explicit expected results."""

from datetime import date, timedelta

import pytest

from nldate import parse

TODAY = date(2025, 3, 12)  # Wednesday


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("today", date(2025, 3, 12)),
        ("now", date(2025, 3, 12)),
        ("tomorrow", date(2025, 3, 13)),
        ("yesterday", date(2025, 3, 11)),
        ("the day after tomorrow", date(2025, 3, 14)),
        ("day before yesterday", date(2025, 3, 10)),
        ("in 3 days", date(2025, 3, 15)),
        ("three days ago", date(2025, 3, 9)),
        ("in twenty-one days", date(2025, 4, 2)),
        ("in one hundred and two days", date(2025, 6, 22)),
        ("a week from now", date(2025, 3, 19)),
        ("two weeks from tomorrow", date(2025, 3, 27)),
        ("5 days before December 1st, 2025", date(2025, 11, 26)),
        ("1 year and 2 months after yesterday", date(2026, 5, 11)),
        ("2 weeks and 3 days ago", date(2025, 2, 23)),
        ("1 month, 2 weeks and 3 days after today", date(2025, 4, 29)),
        ("1 day before 2 weeks after tomorrow", date(2025, 3, 26)),
        ("the day after next Tuesday", date(2025, 3, 19)),
        ("in a fortnight", date(2025, 3, 26)),
        ("in a couple of days", date(2025, 3, 14)),
        ("next week", date(2025, 3, 19)),
        ("last month", date(2025, 2, 12)),
        ("next year", date(2026, 3, 12)),
        ("this month", date(2025, 3, 12)),
        ("a decade ago", date(2015, 3, 12)),
        ("next Tuesday", date(2025, 3, 18)),
        ("next Wednesday", date(2025, 3, 19)),
        ("last Wednesday", date(2025, 3, 5)),
        ("last Friday", date(2025, 3, 7)),
        ("this Monday", date(2025, 3, 10)),
        ("this Sunday", date(2025, 3, 16)),
        ("Friday", date(2025, 3, 14)),
        ("Wednesday", date(2025, 3, 12)),
        ("Mon next week", date(2025, 3, 17)),
        ("Friday last week", date(2025, 3, 7)),
        ("2025-12-01", date(2025, 12, 1)),
        ("2025/12/1", date(2025, 12, 1)),
        ("12/01/2025", date(2025, 12, 1)),
        ("31/12/2025", date(2025, 12, 31)),
        ("12-1-25", date(2025, 12, 1)),
        ("12/1", date(2025, 12, 1)),
        ("December 1st, 2025", date(2025, 12, 1)),
        ("Dec. 1, 2025", date(2025, 12, 1)),
        ("1 December 2025", date(2025, 12, 1)),
        ("the first of December 2025", date(2025, 12, 1)),
        ("December twenty-fifth 2025", date(2025, 12, 25)),
        ("December the first", date(2025, 12, 1)),
        ("Monday, December 1st, 2025", date(2025, 12, 1)),
        ("on December 1", date(2025, 12, 1)),
        ("  NEXT   tUeSdAy  ", date(2025, 3, 18)),
        ("December 2026", date(2026, 12, 1)),
        ("September", date(2025, 9, 1)),
        ("end of this month", date(2025, 3, 31)),
        ("the first day of next month", date(2025, 4, 1)),
        ("beginning of next year", date(2026, 1, 1)),
        ("last day of February 2024", date(2024, 2, 29)),
        ("end of this week", date(2025, 3, 16)),
        ("start of next quarter", date(2025, 4, 1)),
        ("second Tuesday of April 2025", date(2025, 4, 8)),
        ("last Friday of next month", date(2025, 4, 25)),
        ("3rd Monday in January 2026", date(2026, 1, 19)),
        ("Christmas", date(2025, 12, 25)),
        ("Christmas eve 2026", date(2026, 12, 24)),
        ("Thanksgiving 2025", date(2025, 11, 27)),
        ("Memorial day", date(2025, 5, 26)),
        ("last Halloween", date(2024, 10, 31)),
        ("in 3 business days", date(2025, 3, 17)),
        ("5 weekdays ago", date(2025, 3, 5)),
        ("2 days before end of next month", date(2025, 4, 28)),
        ("May 5 next year", date(2026, 5, 5)),
        ("May 5 last year", date(2024, 5, 5)),
        ("next January", date(2026, 1, 1)),
        ("last January", date(2025, 1, 1)),
        ("the first of next month", date(2025, 4, 1)),
        ("the twenty-first of this month", date(2025, 3, 21)),
        ("2 days prior to April 1", date(2025, 3, 30)),
        ("2 weeks following May 1", date(2025, 5, 15)),
        ("Tuesday after next", date(2025, 3, 25)),
        ("Jan., 5, 2026.", date(2026, 1, 5)),
    ],
)
def test_common_expressions(text: str, expected: date) -> None:
    assert parse(text, today=TODAY) == expected


@pytest.mark.parametrize(
    ("text", "reference", "expected"),
    [
        ("tomorrow", date(2025, 12, 31), date(2026, 1, 1)),
        ("yesterday", date(2025, 1, 1), date(2024, 12, 31)),
        ("tomorrow", date(2024, 2, 28), date(2024, 2, 29)),
        ("next month", date(2025, 1, 31), date(2025, 2, 28)),
        ("next month", date(2024, 1, 31), date(2024, 2, 29)),
        ("next year", date(2024, 2, 29), date(2025, 2, 28)),
        ("1 month ago", date(2025, 3, 31), date(2025, 2, 28)),
        ("1 year and 1 day after today", date(2024, 2, 29), date(2025, 3, 1)),
        ("next Monday", date(2025, 3, 17), date(2025, 3, 24)),
        ("last Monday", date(2025, 3, 17), date(2025, 3, 10)),
        ("in 1 business day", date(2025, 3, 15), date(2025, 3, 17)),
        ("5 business days ago", date(2025, 3, 16), date(2025, 3, 10)),
        ("next Christmas", date(2025, 12, 25), date(2026, 12, 25)),
        ("last Christmas", date(2025, 12, 25), date(2024, 12, 25)),
    ],
)
def test_calendar_boundaries(text: str, reference: date, expected: date) -> None:
    assert parse(text, reference) == expected


@pytest.mark.parametrize(
    "text",
    [
        "",
        "   ",
        "not a date",
        "banana",
        "in many days",
        "in -3 days",
        "2025-02-29",
        "April 31 2025",
        "2024-13-01",
        "13/32/2025",
        "December 0",
        "next Blursday",
        "5 days before",
        "in 3 days junk",
        "tomorrow junk",
        "February 29 2025",
        "February 30 2024",
        "fifth Monday of February 2025",
        "zero Monday of March 2025",
        "99999999999999 years ago",
        "1 day before 0001-01-01",
        "1 day after 9999-12-31",
        "0/1/2025",
    ],
)
def test_invalid_input(text: str) -> None:
    with pytest.raises(ValueError):
        parse(text, TODAY)


def test_default_reference_is_current_date() -> None:
    before = date.today()
    actual = parse("today")
    after = date.today()
    assert before <= actual <= after
    assert type(actual) is date


def test_weekday_offsets_across_a_year() -> None:
    for offset in range(366):
        reference = date(2024, 1, 1) + timedelta(days=offset)
        for weekday, name in enumerate(
            [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
        ):
            future = parse("next " + name, reference)
            past = parse("last " + name, reference)
            assert future.weekday() == past.weekday() == weekday
            assert 1 <= (future - reference).days <= 7
            assert 1 <= (reference - past).days <= 7


def test_business_days_against_daily_counting() -> None:
    for offset in range(7):
        reference = date(2025, 3, 10) + timedelta(days=offset)
        for sign in (-1, 1):
            for count in (0, 1, 4, 5, 6, 10, 20):
                expected = reference
                remaining = count
                while remaining:
                    expected += timedelta(days=sign)
                    remaining -= expected.weekday() < 5
                suffix = "ago" if sign < 0 else "from now"
                assert parse(f"{count} business days {suffix}", reference) == expected
