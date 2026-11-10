"""A strict, composable English date grammar using only the standard library."""

import calendar
import re
from datetime import date, timedelta

_MONTHS = {
    name.lower(): i
    for i in range(1, 13)
    for name in (calendar.month_name[i], calendar.month_abbr[i])
}
_MONTHS["sept"] = 9
_WEEKDAYS = {
    name.lower(): i
    for i in range(7)
    for name in (calendar.day_name[i], calendar.day_abbr[i])
}
_WEEKDAYS.update(tues=1, weds=2, thurs=3, thur=3)
_SMALL = dict(
    zip(
        "zero one two three four five six seven eight nine ten eleven twelve "
        "thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split(),
        range(20),
        strict=True,
    )
)
_TENS = dict(
    zip(
        "twenty thirty forty fifty sixty seventy eighty ninety".split(),
        range(20, 100, 10),
        strict=True,
    )
)
_ORDINALS = dict(
    zip(
        "first second third fourth fifth sixth seventh eighth ninth tenth eleventh "
        "twelfth thirteenth fourteenth fifteenth sixteenth seventeenth eighteenth "
        "nineteenth twentieth".split(),
        range(1, 21),
        strict=True,
    )
)
_ORDINALS.update(thirtieth=30, fortieth=40, fiftieth=50)
_UNITS = r"business days?|weekdays?|days?|weeks?|fortnights?|months?|quarters?|years?|decades?"
_DURATION_PART = re.compile(rf"(.+?)\s+({_UNITS})(?=\s|,|$)")


def parse(s: str, today: date | None = None) -> date:
    """Return the date described by *s*, or raise ValueError.

    Missing years use the reference year. Numeric dates use month/day/year,
    except unambiguous day/month/year inputs. Next/last weekdays are strictly
    future/past; this weekday belongs to the reference Monday-based week.
    Month and year arithmetic clamps to the last valid day of the target month.
    """
    if not isinstance(s, str) or not s.strip():
        raise ValueError("Expected a nonempty date expression")
    reference = today if today is not None else date.today()
    text = " ".join(s.lower().strip().replace("’", "'").split())
    text = re.sub(r"\b([a-z]+)\.(?=\s|,|$)", r"\1", text).rstrip(".")
    text = re.sub(r"(?<=\d)(st|nd|rd|th)\b", "", text)
    text = re.sub(r"^(?:on|the date of)\s+", "", text)
    try:
        return _parse(text, reference, 0)
    except (ValueError, OverflowError, RecursionError) as exc:
        raise ValueError(f"Unrecognized or invalid date: {s!r}") from exc


def _number(text: str) -> int:
    text = text.strip().replace("-", " ")
    if text.isdecimal():
        return int(text)
    if text in {"a", "an"}:
        return 1
    if text in {"a couple of", "couple of", "a couple", "couple"}:
        return 2
    total = current = 0
    tokens = text.split()
    if not tokens:
        raise ValueError("Missing number")
    for token in tokens:
        if token in _SMALL:
            current += _SMALL[token]
        elif token in _TENS:
            current += _TENS[token]
        elif token in _ORDINALS:
            current += _ORDINALS[token]
        elif token == "hundred" and current:
            current *= 100
        elif token == "thousand" and current:
            total += current * 1000
            current = 0
        elif token == "and" and current:
            continue
        else:
            raise ValueError("Invalid number")
    return total + current


def _duration(text: str) -> list[tuple[int, str]]:
    parts = []
    end = 0
    for match in _DURATION_PART.finditer(text):
        if text[end : match.start()].strip(" ,"):
            raise ValueError("Invalid duration")
        count = match[1].strip(" ,")
        count = re.sub(r"^and\s+", "", count)
        parts.append((_number(count), match[2].rstrip("s")))
        end = match.end()
    if not parts or text[end:].strip():
        raise ValueError("Invalid duration")
    return parts


def _month_shift(base: date, months: int) -> date:
    year, month = divmod(base.year * 12 + base.month - 1 + months, 12)
    month += 1
    return date(year, month, min(base.day, calendar.monthrange(year, month)[1]))


def _shift(base: date, duration: str, sign: int) -> date:
    parts = _duration(duration)
    months = sum(
        n * {"month": 1, "quarter": 3, "year": 12, "decade": 120}.get(unit, 0)
        for n, unit in parts
    )
    result = _month_shift(base, sign * months)
    days = sum(
        n * {"day": 1, "week": 7, "fortnight": 14}.get(unit, 0) for n, unit in parts
    )
    result += timedelta(days=sign * days)
    business = sum(n for n, unit in parts if unit in {"business day", "weekday"})
    # Whole work weeks avoid iterating once per day for large offsets.
    while business and result.weekday() >= 5:
        result += timedelta(days=sign)
        business -= result.weekday() < 5
    weeks, business = divmod(business, 5)
    result += timedelta(days=sign * weeks * 7)
    while business:
        result += timedelta(days=sign)
        business -= result.weekday() < 5
    return result


def _parse(text: str, today: date, depth: int) -> date:
    if depth > 30:
        raise ValueError("Date expression is too deeply nested")
    aliases = {
        "today": 0,
        "now": 0,
        "tomorrow": 1,
        "yesterday": -1,
        "day after tomorrow": 2,
        "the day after tomorrow": 2,
        "day before yesterday": -2,
        "the day before yesterday": -2,
    }
    if text in aliases:
        return today + timedelta(days=aliases[text])

    text = re.sub(r"\bprior to\b", "before", text)
    text = re.sub(r"\bfollowing\b", "after", text)
    match = re.fullmatch(r"([a-z]+) (after|before) next", text)
    if match and match[1] in _WEEKDAYS:
        anchor = _parse("next " + match[1], today, depth + 1)
        return anchor + timedelta(days=7 if match[2] == "after" else -7)
    match = re.fullmatch(r"(?:the )?(next|last|this) ([a-z]+)", text)
    if match and match[2] in _MONTHS:
        month = _MONTHS[match[2]]
        year = today.year
        if match[1] == "next" and month <= today.month:
            year += 1
        elif match[1] == "last" and month >= today.month:
            year -= 1
        return date(year, month, 1)
    match = re.fullmatch(r"(.+) (this|next|last) year", text)
    if match:
        year = today.year + {"this": 0, "next": 1, "last": -1}[match[2]]
        return _parse(match[1] + " " + str(year), today, depth + 1)
    match = re.fullmatch(
        r"(?:the )?(\d+|[a-z]+(?:-[a-z]+)?) of (this|next|last) month", text
    )
    if match and match[1] not in {"start", "end", "beginning", "middle"}:
        base = _month_shift(
            today.replace(day=1), {"this": 0, "next": 1, "last": -1}[match[2]]
        )
        return base.replace(day=_number(match[1]))

    # Offsets can contain any supported date expression as their anchor.
    match = re.fullmatch(r"(.+?)\s+(before|after|from)\s+(.+)", text)
    if match:
        amount = match[1]
        if amount in {"day", "the day", "week", "month", "year"}:
            amount = "1 " + amount.removeprefix("the ")
        anchor = _parse(match[3], today, depth + 1)
        return _shift(anchor, amount, -1 if match[2] == "before" else 1)
    match = re.fullmatch(r"(.+?)\s+(ago|earlier|later|hence)", text)
    if match:
        return _shift(today, match[1], -1 if match[2] in {"ago", "earlier"} else 1)
    if text.startswith("in "):
        return _shift(today, text[3:], 1)
    match = re.fullmatch(r"(.+?)\s+back", text)
    if match:
        return _shift(today, match[1], -1)
    match = re.fullmatch(
        r"(next|last|this|previous|coming)\s+(day|week|fortnight|month|quarter|year|decade)",
        text,
    )
    if match:
        sign = {"next": 1, "coming": 1, "last": -1, "previous": -1, "this": 0}[match[1]]
        return _shift(today, "1 " + match[2], sign)
    if text in {"a fortnight", "fortnight"}:
        return today + timedelta(days=14)

    result = _weekday(text, today)
    if result is not None:
        return result

    match = re.fullmatch(
        r"(?:the )?(start|beginning|end|first day|last day|middle)(?: of)? (.+)", text
    )
    if match:
        start, end = _period(match[2], today, depth + 1)
        if match[1] in {"end", "last day"}:
            return end
        if match[1] == "middle":
            return start + (end - start) // 2
        return start

    match = re.fullmatch(
        r"(?:the )?(last|first|second|third|fourth|fifth|\d+) ([a-z]+) (?:of|in) (.+)",
        text,
    )
    if match and match[2] in _WEEKDAYS:
        start, end = _period(match[3], today, depth + 1)
        weekday = _WEEKDAYS[match[2]]
        if match[1] == "last":
            return end - timedelta(days=(end.weekday() - weekday) % 7)
        result = start + timedelta(
            days=(weekday - start.weekday()) % 7 + 7 * (_number(match[1]) - 1)
        )
        if result > end or result < start:
            raise ValueError("Weekday does not occur in that period")
        return result

    result = _holiday(text, today)
    if result is not None:
        return result
    return _absolute(text, today)


def _weekday(text: str, today: date) -> date | None:
    match = re.fullmatch(r"([a-z]+) (this|next|last|previous) week", text)
    if match and match[1] in _WEEKDAYS:
        weeks = {"this": 0, "next": 1, "last": -1, "previous": -1}[match[2]]
        return today + timedelta(days=7 * weeks + _WEEKDAYS[match[1]] - today.weekday())
    match = re.fullmatch(
        r"(?:(next|last|this|previous|coming|this coming) )?([a-z]+)", text
    )
    if not match or match[2] not in _WEEKDAYS:
        return None
    delta = _WEEKDAYS[match[2]] - today.weekday()
    if match[1] in {"last", "previous"}:
        delta = -((-delta) % 7 or 7)
    elif match[1] != "this":
        delta %= 7
        if match[1] is not None and delta == 0:
            delta = 7
    return today + timedelta(days=delta)


def _period(text: str, today: date, depth: int) -> tuple[date, date]:
    text = text.removeprefix("the ")
    match = re.fullmatch(
        r"(?:(this|next|last|previous) )?(week|month|quarter|year)", text
    )
    if match:
        sign = {None: 0, "this": 0, "next": 1, "last": -1, "previous": -1}[match[1]]
        unit = match[2]
        if unit == "week":
            start = today + timedelta(days=sign * 7 - today.weekday())
            return start, start + timedelta(days=6)
        if unit == "year":
            return date(today.year + sign, 1, 1), date(today.year + sign, 12, 31)
        if unit == "quarter":
            start = _month_shift(
                date(today.year, (today.month - 1) // 3 * 3 + 1, 1), sign * 3
            )
            return start, _month_shift(start, 3) - timedelta(days=1)
        base = _month_shift(today.replace(day=1), sign)
    elif re.fullmatch(r"\d{4}", text):
        return date(int(text), 1, 1), date(int(text), 12, 31)
    else:
        base = _parse(text, today, depth)
    return base.replace(day=1), base.replace(
        day=calendar.monthrange(base.year, base.month)[1]
    )


def _year(text: str) -> int:
    value = int(text)
    return value + (2000 if value <= 68 else 1900) if len(text) == 2 else value


def _absolute(text: str, today: date) -> date:
    text = re.sub(r"^(?:" + "|".join(_WEEKDAYS) + r")(?:,?\s+)", "", text)
    text = text.replace(",", " ")
    text = " ".join(text.split())
    match = re.fullmatch(r"(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})", text)
    if match:
        return date(int(match[1]), int(match[2]), int(match[3]))
    match = re.fullmatch(r"(\d{1,2})([-/.])(\d{1,2})(?:\2(\d{2}|\d{4}))?", text)
    if match:
        first, second = int(match[1]), int(match[3])
        month, day = (second, first) if first > 12 else (first, second)
        return date(_year(match[4]) if match[4] else today.year, month, day)
    text = text.replace("-", " ")
    month_pattern = "|".join(_MONTHS)
    match = re.fullmatch(rf"({month_pattern})(?: (?:the )?(.+?))?(?: (\d{{4}}))?", text)
    if match:
        day_text = match[2]
        year = int(match[3]) if match[3] else today.year
        if day_text and re.fullmatch(r"\d{4}", day_text) and not match[3]:
            return date(int(day_text), _MONTHS[match[1]], 1)
        return date(year, _MONTHS[match[1]], _number(day_text) if day_text else 1)
    match = re.fullmatch(
        rf"(?:the )?(.+?)(?: of)? ({month_pattern})(?: (\d{{2}}|\d{{4}}))?", text
    )
    if match:
        return date(
            _year(match[3]) if match[3] else today.year,
            _MONTHS[match[2]],
            _number(match[1]),
        )
    match = re.fullmatch(rf"(\d{{4}}) ({month_pattern}) (.+)", text)
    if match:
        return date(int(match[1]), _MONTHS[match[2]], _number(match[3]))
    raise ValueError("No matching date format")


def _holiday(text: str, today: date) -> date | None:
    fixed = {
        "christmas": (12, 25),
        "christmas day": (12, 25),
        "christmas eve": (12, 24),
        "new year": (1, 1),
        "new year's day": (1, 1),
        "new years day": (1, 1),
        "new year's eve": (12, 31),
        "halloween": (10, 31),
        "valentine's day": (2, 14),
        "valentines day": (2, 14),
        "independence day": (7, 4),
        "fourth of july": (7, 4),
        "veterans day": (11, 11),
        "juneteenth": (6, 19),
    }
    floating = {
        "thanksgiving": (11, 3, 4),
        "thanksgiving day": (11, 3, 4),
        "labor day": (9, 0, 1),
        "memorial day": (5, 0, -1),
        "mother's day": (5, 6, 2),
        "father's day": (6, 6, 3),
        "mlk day": (1, 0, 3),
    }
    match = re.fullmatch(r"(?:(next|last|this) )?(.+?)(?: (\d{4}))?", text)
    if not match or match[2] not in fixed.keys() | floating.keys():
        return None
    name = match[2]

    def occurrence(year: int) -> date:
        if name in fixed:
            return date(year, *fixed[name])
        month, weekday, n = floating[name]
        if n == -1:
            end = date(year, month, calendar.monthrange(year, month)[1])
            return end - timedelta(days=(end.weekday() - weekday) % 7)
        start = date(year, month, 1)
        return start + timedelta(days=(weekday - start.weekday()) % 7 + 7 * (n - 1))

    result = occurrence(int(match[3]) if match[3] else today.year)
    if not match[3]:
        if match[1] == "next" and result <= today:
            result = occurrence(today.year + 1)
        elif match[1] == "last" and result >= today:
            result = occurrence(today.year - 1)
    return result
