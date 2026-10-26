"""ING-08 module: ``src.external`` turns one weather feed into context events.

The feed is the MeteoArchive daily export (``sources/external/weather/eu_meteoarchive/``), the
provider `generated/sources/external/weather/coverage_by_city.csv` names first for 17 of the 39
stores. One ``ContextEvent`` per city **episode**: a run of consecutive days whose daily
temperature departs from the same city's own previous month by at least ``anomaly_c``, so
``start``/``end`` are the cold or warm spell and not one noisy day. Weather is ``context_only``
by construction: an external feed never supplies a demand coefficient (RFC 4.5 and 4.9).

**No future weather is backdated.** The export is one bulk file downloaded today, so it holds
days after any replayed ``as_of``; they never reach the run. A day's value is a whole-day
aggregate, so it becomes available at the end of *that local day*: an evening run sees the days
that have ended, not the one in progress. The reference mean is computed from days that ended
before the analysed window, so a row can never leak into its own baseline.

Two traps of this feed are handled instead of guessed around. The provider changed schema
mid-period (v1 ``weathercode`` and ``windspeed_10m_max`` in km/h, v2 ``weather_code`` and m/s
plus ``temperature_2m_mean``), so only ``temperature_2m_min`` and ``temperature_2m_max`` are
read: present in both, in degrees Celsius, and their mid-range is one definition for the whole
series instead of a mix of the v2 mean and something else. And a file name is not a coverage
promise (``paris_2026-03-01_2026-10-21.json`` stops on the 20th): days come from the rows, never
from the name. A missing measurement stays missing, so a gap breaks an episode instead of being
filled with a neighbour or a zero.

A third trap: the provider echoes its own timezone back and it is not always right (London's
summer file says ``GMT`` with offset 0, across British Summer Time). A calendar date needs no
conversion, so a day is bounded by the store's timezone from ``erp/master_data/stores.csv``,
which owns the local day; a file whose echoed zone disagrees is reported, not trusted.

A temperature has no ``Unit`` member in the contracts, so ``magnitude`` is a vague quantity
carrying the source text and the description states the numbers. Adding a temperature unit is a
contract change (lane C), not something a connector invents.
"""

import csv
import hashlib
import json
import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from math import isfinite
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from tesseract.core.config import get_settings
from tesseract.core.contracts import ContextEvent, ModuleManifest, ModuleResult, Quantity, RunSpec

PROVIDER = "eu_meteoarchive"  # the folder coverage_by_city.csv names as this city's first
FOLDER = f"external/weather/{PROVIDER}"
COVERAGE = "external/weather/coverage_by_city.csv"
EVENT_VERSION = "v1"
COLD = "weather_cold"
WARM = "weather_warm"

# The previous month is the reference the RFC asks for: history that was already available.
REFERENCE_DAYS = 30
# A month with fewer usable days than this gives no trustworthy reference: the city abstains.
MIN_REFERENCE_DAYS = 20

DEFAULT_WINDOW_DAYS = 21
DEFAULT_ANOMALY_C = 4.0
DEFAULT_MIN_DAYS = 3

# The unit is two characters (a degree sign and a C) in both API versions. Anything else is
# refused, not converted: an unnoticed Fahrenheit is a 1.8x error in every deviation.
TEMPERATURE_UNIT = "\u00b0C"

# The dataset transliterates German umlauts as two letters (``zuerich``, ``muenchen``), which
# Unicode decomposition alone collapses to one (``zurich``): map those before folding.
_UMLAUTS = (
    ("\u00e4", "ae"),
    ("\u00f6", "oe"),
    ("\u00fc", "ue"),
    ("\u00c4", "AE"),
    ("\u00d6", "OE"),
    ("\u00dc", "UE"),
    ("\u00f8", "o"),
    ("\u00e5", "a"),
    ("\u00e6", "ae"),
    ("\u00df", "ss"),
)

MANIFEST = ModuleManifest(
    id="src.external",
    version="1",
    layer="sources",
    description="MeteoArchive daily weather as cold/warm context events for the run's store cities",
    requires=(),
    optional_inputs=(),
    produces=("ContextEvent",),
    enabled=True,
    mode="live",
    params_schema={
        "type": "object",
        "properties": {
            "window_days": {"type": "integer", "minimum": 1},
            "anomaly_c": {"type": "number", "exclusiveMinimum": 0},
            "min_days": {"type": "integer", "minimum": 1},
        },
        "additionalProperties": False,
    },
)


class FeedError(ValueError):
    """The file is readable but cannot be trusted as this feed: schema, units or duplicates."""


@dataclass(frozen=True)
class Day:
    day: date
    mid_c: float
    relative: str  # the file this row came from, for the locator and the content hash


@dataclass(frozen=True)
class FeedFile:
    relative: str
    content_hash: str
    timezone: str
    days: tuple[Day, ...]


@dataclass(frozen=True)
class CityFeed:
    city: str
    slug: str
    zones: Mapping[str, str]  # relative file -> the timezone the provider echoed
    hashes: Mapping[str, str]  # relative file -> sha256 of its bytes
    days: Mapping[date, Day]  # merged across the city's files, no duplicates


@dataclass(frozen=True)
class Episode:
    kind: str
    start: date
    end: date
    days: tuple[Day, ...]
    reference_mean: float
    reference_start: date
    reference_end: date
    truncated: bool  # the window opened inside the episode: its real start is earlier


def city_slug(city: str) -> str:
    """``Zuerich`` -> ``zuerich``, ``St. Moritz`` -> ``st_moritz``: the feed's file stem."""
    for letter, replacement in _UMLAUTS:
        city = city.replace(letter, replacement)
    folded = unicodedata.normalize("NFKD", city)
    ascii_text = "".join(char for char in folded if not unicodedata.combining(char))
    return (
        ascii_text.lower()
        .replace(".", "")
        .replace("'", "_")
        .replace("\u2019", "_")
        .replace("-", " ")
        .replace(" ", "_")
    )


def coverage(sources_dir: Path) -> dict[str, tuple[str, str]]:
    """Store -> (city, primary provider folder): the dataset's own crosswalk."""
    with (sources_dir / COVERAGE).open(encoding="utf-8", newline="") as stream:
        return {
            store_id: (row["city"], row["primary_provider_folder"])
            for row in csv.DictReader(stream)
            for store_id in row["stores"].split()
        }


def read_feed(path: Path, *, relative: str) -> FeedFile:
    """Read one location file, verifying its timezone, units and the two temperature series."""
    data = path.read_bytes()
    try:
        payload = json.loads(data)
    except json.JSONDecodeError as error:
        raise FeedError(f"not JSON ({error.msg})") from None
    if not isinstance(payload, dict):
        raise FeedError("the file is not one location object")
    timezone = payload.get("timezone")
    if not isinstance(timezone, str):
        raise FeedError("no timezone, so its days have no local boundary")
    try:
        ZoneInfo(timezone)
    except (ZoneInfoNotFoundError, ValueError):
        raise FeedError(f"unknown timezone {timezone!r}") from None
    daily = payload.get("daily")
    if not isinstance(daily, dict) or not isinstance(daily.get("time"), list):
        raise FeedError("no daily series")
    units = payload.get("daily_units")
    units = units if isinstance(units, dict) else {}
    for variable in ("temperature_2m_max", "temperature_2m_min"):
        if units.get(variable) != TEMPERATURE_UNIT:
            raise FeedError(f"{variable} is not in {TEMPERATURE_UNIT}, refusing to convert")
    return FeedFile(
        relative=relative,
        content_hash=hashlib.sha256(data).hexdigest(),
        timezone=timezone,
        days=tuple(Day(day, mid, relative) for day, mid in _rows(daily)),
    )


def _rows(daily: dict[str, Any]) -> list[tuple[date, float]]:
    times = daily["time"]
    highs, lows = daily.get("temperature_2m_max"), daily.get("temperature_2m_min")
    if not isinstance(highs, list) or not isinstance(lows, list):
        raise FeedError("temperature series are not lists")
    if len(highs) != len(times) or len(lows) != len(times):
        raise FeedError("temperature series are shorter than the days")
    rows: list[tuple[date, float]] = []
    for day_text, high, low in zip(times, highs, lows, strict=True):
        if high is None or low is None:
            continue  # a missing measurement stays missing: no zero, no neighbour's value
        try:
            top, bottom = float(high), float(low)
        except (TypeError, ValueError):
            raise FeedError(f"unreadable temperatures on {day_text!r}") from None
        if not (isfinite(top) and isfinite(bottom)):
            continue  # a non-finite value would poison the whole reference mean
        try:
            rows.append((date.fromisoformat(day_text), (top + bottom) / 2))
        except (TypeError, ValueError):
            raise FeedError(f"unreadable row {day_text!r}") from None
    return rows


def load_city(root: Path, city: str) -> CityFeed:
    """Merge the city's files row by row, refusing a conflicting duplicate of the same day.

    The timezone each file echoes is kept per file: the provider is not consistent (London's
    summer file says ``GMT`` during BST), and only the store's own zone may bound its days.
    """
    slug = city_slug(city)
    paths = sorted((root / FOLDER).glob(f"{slug}_*.json"))
    if not paths:
        raise FeedError(f"no {FOLDER}/{slug}_*.json in the dataset")
    hashes: dict[str, str] = {}
    zones: dict[str, str] = {}
    days: dict[date, Day] = {}
    for path in paths:
        relative = f"{FOLDER}/{path.name}"
        feed = read_feed(path, relative=relative)
        zones[relative] = feed.timezone
        hashes[relative] = feed.content_hash
        for day in feed.days:
            seen = days.get(day.day)
            if seen is None:
                days[day.day] = day
            elif seen.mid_c != day.mid_c:
                raise FeedError(f"two values for {day.day}: {seen.mid_c} and {day.mid_c}")
    return CityFeed(
        city=city,
        slug=slug,
        zones=zones,
        hashes=hashes,
        days=dict(sorted(days.items())),
    )


def store_timezones(sources_dir: Path) -> dict[str, str]:
    """Store id -> timezone from the ERP master data, which owns the local day (AGENTS.md)."""
    path = sources_dir / "erp" / "master_data" / "stores.csv"
    with path.open(encoding="utf-8", newline="") as stream:
        return {row["store_id"]: row["timezone"] for row in csv.DictReader(stream)}


def completed_day(as_of: datetime, timezone: ZoneInfo) -> date:
    """The last local day whose whole-day aggregate already exists at ``as_of``."""
    local = as_of.astimezone(timezone).date()
    return local if _end_of(local, timezone) <= as_of else local - timedelta(days=1)


def _start_of(day: date, timezone: ZoneInfo) -> datetime:
    return datetime.combine(day, time(0, 0), tzinfo=timezone)


def _end_of(day: date, timezone: ZoneInfo) -> datetime:
    return datetime.combine(day, time(23, 59, 59), tzinfo=timezone)


def episodes(
    series: Mapping[date, Day],
    *,
    window_start: date,
    window_end: date,
    anomaly_c: float = DEFAULT_ANOMALY_C,
    min_days: int = DEFAULT_MIN_DAYS,
    reference_days: int = REFERENCE_DAYS,
    min_reference_days: int = MIN_REFERENCE_DAYS,
) -> tuple[list[Episode], str | None]:
    """Cold and warm spells in the window, or the reason the city cannot be scored."""
    reference_start = window_start - timedelta(days=reference_days)
    reference_end = window_start - timedelta(days=1)
    reference = [
        series[day].mid_c for day in _days(reference_start, reference_end) if day in series
    ]
    if len(reference) < min_reference_days:
        return [], (
            f"{reference_start.isoformat()}..{reference_end.isoformat()} has "
            f"{len(reference)} usable days of {reference_days}: no reference to score against"
        )
    reference_mean = sum(reference) / len(reference)
    found: list[Episode] = []
    run: list[Day] = []
    sign = ""

    def flush() -> None:
        if len(run) < min_days:
            return
        found.append(
            Episode(
                kind=COLD if sign == "cold" else WARM,
                start=run[0].day,
                end=run[-1].day,
                days=tuple(run),
                reference_mean=reference_mean,
                reference_start=reference_start,
                reference_end=reference_end,
                truncated=_truncated(series, run[0], reference_mean, anomaly_c, sign),
            )
        )

    for day in _days(window_start, window_end):
        observation = series.get(day)
        direction = ""
        if observation is not None:
            deviation = observation.mid_c - reference_mean
            if deviation <= -anomaly_c:
                direction = "cold"
            elif deviation >= anomaly_c:
                direction = "warm"
        if direction and direction == sign:
            run.append(observation)
            continue
        flush()
        run = [observation] if observation is not None and direction else []
        sign = direction
    flush()
    return found, None


def _days(start: date, end: date) -> list[date]:
    return [start + timedelta(days=offset) for offset in range((end - start).days + 1)]


def _truncated(
    series: Mapping[date, Day], first: Day, reference_mean: float, anomaly_c: float, sign: str
) -> bool:
    """True when the day before the window qualifies too: the spell began earlier."""
    earlier = series.get(first.day - timedelta(days=1))
    if earlier is None:
        return False
    deviation = earlier.mid_c - reference_mean
    return (sign == "cold" and deviation <= -anomaly_c) or (
        sign == "warm" and deviation >= anomaly_c
    )


def build_event(
    episode: Episode,
    *,
    city: str,
    store_ids: tuple[str, ...],
    hashes: Mapping[str, str],
    timezone: ZoneInfo,
    spec: RunSpec,
) -> ContextEvent:
    """One stored ``ContextEvent`` for the spell, available once its last day has ended."""
    start = _start_of(episode.start, timezone)
    end = _end_of(episode.end, timezone)
    mean_mid = sum(day.mid_c for day in episode.days) / len(episode.days)
    deviation = mean_mid - episode.reference_mean
    phase = "cold" if episode.kind == COLD else "warm"
    extreme = (min if episode.kind == COLD else max)(episode.days, key=lambda day: day.mid_c)
    reference = (
        f"{episode.reference_start.isoformat()}..{episode.reference_end.isoformat()} "
        f"reference mean {episode.reference_mean:.1f} {TEMPERATURE_UNIT}"
    )
    description = (
        f"{city}: {len(episode.days)} consecutive days of {phase} weather "
        f"{episode.start.isoformat()}..{episode.end.isoformat()}, daily mid temperature mean "
        f"{mean_mid:.1f} {TEMPERATURE_UNIT}, {deviation:+.1f} {TEMPERATURE_UNIT} against the "
        f"{reference}; {'coldest' if episode.kind == COLD else 'warmest'} day "
        f"{extreme.mid_c:.1f} {TEMPERATURE_UNIT} on {extreme.day.isoformat()}."
    )
    if episode.truncated:
        description += (
            " The spell was already running before the window opened, so its start is the"
            " window's first day, not its real beginning."
        )
    return ContextEvent(
        id=f"ctx-{city_slug(city)}-{phase}-{episode.start:%Y%m%d}",
        version=EVENT_VERSION,
        available_at=end,
        availability_basis="weather_observation_day_end",
        source_refs=_source_refs(episode, hashes=hashes),
        run_id=spec.run_id,
        scenario_id=spec.scenario_id,
        computed_at=spec.as_of,
        input_refs=(),
        producer=MANIFEST.id,
        producer_version=MANIFEST.version,
        kind=episode.kind,
        store_ids=store_ids,
        start=start,
        end=end,
        issued_at=None,
        magnitude=Quantity(
            kind="vague", raw=f"{deviation:+.1f} {TEMPERATURE_UNIT} vs the {reference}"
        ),
        description=description,
        role="context_only",
    )


def _source_refs(episode: Episode, *, hashes: Mapping[str, str]) -> tuple[dict[str, Any], ...]:
    """One ref per file the spell used, with the span of local days taken from it."""
    spans: dict[str, tuple[date, date]] = {}
    for day in episode.days:
        first, last = spans.get(day.relative, (day.day, day.day))
        spans[day.relative] = (min(first, day.day), max(last, day.day))
    return tuple(
        {
            "uri": f"dataset://{relative}",
            "content_hash": f"sha256:{hashes[relative]}",
            "locator": f"daily[{first.isoformat()}..{last.isoformat()}]",
        }
        for relative, (first, last) in sorted(spans.items())
    )


def run(ctx, *, sources_dir: Path | None = None) -> ModuleResult:
    """Read the feed for the run's store cities and publish the spells available at ``as_of``."""
    root = sources_dir or get_settings().sources_dir
    window_days = int(ctx.params.get("window_days", DEFAULT_WINDOW_DAYS))
    anomaly_c = float(ctx.params.get("anomaly_c", DEFAULT_ANOMALY_C))
    min_days = int(ctx.params.get("min_days", DEFAULT_MIN_DAYS))
    crosswalk = coverage(root)
    by_city: dict[str, list[str]] = {}
    abstentions: list[str] = []
    errors: list[str] = []
    for store_id in ctx.spec.stores:
        entry = crosswalk.get(store_id)
        if entry is None:
            abstentions.append(f"{store_id}: no entry in {COVERAGE}")
            continue
        city, provider = entry
        if provider != PROVIDER:
            abstentions.append(f"{store_id}: {city} is covered by {provider}, not by this feed")
            continue
        by_city.setdefault(city, []).append(store_id)
    events: list[ContextEvent] = []
    master_timezones = store_timezones(root)
    timezone_warnings = []
    for city in sorted(by_city):
        try:
            feed = load_city(root, city)
        except (FeedError, OSError) as error:
            errors.append(f"{city}: {error}")
            continue
        stores = by_city[city]
        unknown = [store_id for store_id in stores if store_id not in master_timezones]
        if unknown:
            errors.append(
                f"{city}: no timezone in the ERP master data for {', '.join(sorted(unknown))}"
            )
            continue
        if len({master_timezones[store_id] for store_id in stores}) != 1:
            errors.append(f"{city}: the stores of this city disagree on the timezone")
            continue
        store_zone = master_timezones[stores[0]]
        timezone = ZoneInfo(store_zone)
        for relative, echoed in sorted(feed.zones.items()):
            if echoed != timezone.key:
                # A calendar date needs no conversion; the store's zone is the master key. The
                # feed's own timestamp is still wrong and the run says so instead of hiding it.
                timezone_warnings.append(
                    f"{city}: {relative} says {echoed} while the store's timezone is "
                    f"{timezone.key}; its days are bounded by the store's timezone"
                )
        window_end = completed_day(ctx.spec.as_of, timezone)
        window_start = window_end - timedelta(days=window_days - 1)
        found, reason = episodes(
            feed.days,
            window_start=window_start,
            window_end=window_end,
            anomaly_c=anomaly_c,
            min_days=min_days,
        )
        if reason is not None:
            abstentions.append(f"{city}: {reason}")
        for episode in found:
            events.append(
                build_event(
                    episode,
                    city=city,
                    store_ids=tuple(sorted(stores)),
                    hashes=feed.hashes,
                    timezone=timezone,
                    spec=ctx.spec,
                )
            )
    if events:
        ctx.repo.put(*events)
    return ModuleResult(
        module_id=MANIFEST.id,
        module_version=MANIFEST.version,
        status="degraded" if errors or timezone_warnings else "succeeded",
        counts={"cities": len(by_city), "events": len(events)},
        errors=tuple(errors),
        abstentions=tuple([*abstentions, *timezone_warnings]),
    )
