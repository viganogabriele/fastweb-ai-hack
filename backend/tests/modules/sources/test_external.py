"""src.external: weather days become context spells, and no day after as_of reaches a run."""

import hashlib
import json
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from tesseract.core.contracts import ContextEvent, ModuleSnapshot, RunSpec
from tesseract.core.db import connect
from tesseract.core.orchestrator import run as orchestrate
from tesseract.core.registry import RegisteredModule, Registry
from tesseract.core.run_repo import repo_session
from tesseract.modules.sources import external
from tesseract.modules.sources.external import MANIFEST, city_slug, load_city

ROOT = Path(__file__).resolve().parents[4]
SOURCES = ROOT / "generated" / "sources"
FEED = "external/weather/eu_meteoarchive"
COVERAGE = "external/weather/coverage_by_city.csv"
ROME = ZoneInfo("Europe/Rome")
DEGREE = "\u00b0C"

# Evening of 2026-10-22 in Milan: the last day whose aggregate exists is the 21st.
AS_OF = datetime(2026, 10, 22, 3, 0, tzinfo=UTC)


def spec(stores, as_of=AS_OF, params=None, run_id="external-run"):
    return RunSpec(
        run_id=run_id,
        scenario_id="historical",
        as_of=as_of,
        stores=tuple(stores),
        source_manifest_hash="sources",
        config_hash="config",
        code_version="test",
        mode="live",
        modules=(ModuleSnapshot(manifest=MANIFEST, params=params or {}),),
        prompt_versions={},
        model_versions={},
        authorized_fixture_refs=(),
    )


def execute(tmp_path, request, sources_dir=SOURCES):
    engine = connect(f"sqlite:///{tmp_path / 'external.db'}")
    registry = Registry(
        (RegisteredModule(MANIFEST, lambda ctx: external.run(ctx, sources_dir=sources_dir)),)
    )
    statuses = orchestrate(request, engine=engine, registry=registry, clients={})
    return engine, statuses[0]


def days(start, end):
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    return [first + timedelta(days=offset) for offset in range((last - first).days + 1)]


def reference_weather(**overrides):
    """Seven months flat at 20 C with the named days replaced: a readable reference month."""
    series = {day: 20.0 for day in days("2026-07-01", "2026-10-25")}
    series.update({date.fromisoformat(day): value for day, value in overrides.items()})
    return series


def write_feed(root, city, series, *, name=None, timezone="Europe/Rome", units=DEGREE):
    """One MeteoArchive file. One value per day: min = max, so mid-range is that value."""
    folder = root / FEED
    folder.mkdir(parents=True, exist_ok=True)
    ordered = sorted(series)
    payload = {
        "latitude": 45.4,
        "longitude": 9.1,
        "timezone": timezone,
        "api_version": "v2",
        "daily_units": {
            "time": "iso8601",
            "temperature_2m_max": units,
            "temperature_2m_min": units,
        },
        "daily": {
            "time": [day.isoformat() for day in ordered],
            "temperature_2m_max": [series[day] for day in ordered],
            "temperature_2m_min": [series[day] for day in ordered],
        },
    }
    stem = name or f"{city_slug(city)}_2024-09-01_2026-10-21.json"
    (folder / stem).write_text(json.dumps(payload))
    return folder / stem


def write_sources(root, cities, *, units=DEGREE, timezone="Europe/Rome"):
    """A tiny dataset: coverage, feed files and the master data that owns the local day."""
    coverage = root / COVERAGE
    coverage.parent.mkdir(parents=True, exist_ok=True)
    rows = ["city,stores,primary_provider_folder"]
    master = root / "erp" / "master_data" / "stores.csv"
    master.parent.mkdir(parents=True, exist_ok=True)
    stores = ["store_id,timezone"]
    for city, store_ids in cities.items():
        rows.append(f"{city},{' '.join(store_ids)},eu_meteoarchive")
        stores.extend(f"{store_id},{timezone}" for store_id in store_ids)
        write_feed(root, city, reference_weather(), units=units)
    coverage.write_text("\n".join(rows) + "\n", encoding="utf-8")
    master.write_text("\n".join(stores) + "\n", encoding="utf-8")
    return root


def events_of(tmp_path, request, sources_dir=SOURCES):
    engine, status = execute(tmp_path, request, sources_dir)
    with repo_session(engine, request) as repo:
        found = repo.list(ContextEvent)
        published = repo.run_state()["published"]
    engine.dispose()
    return found, status, published


def test_registry_discovers_src_external():
    assert MANIFEST in Registry.discover().manifests()


def test_every_city_of_this_provider_has_files():
    """The dataset's crosswalk and the file stems must agree, umlauts included."""
    covered = {
        city
        for city, provider in external.coverage(SOURCES).values()
        if provider == external.PROVIDER
    }
    assert len(covered) == 16
    for city in sorted(covered):
        assert load_city(SOURCES, city).days, city
    assert city_slug("Z\u00fcrich") == "zuerich"
    assert city_slug("M\u00fcnchen") == "muenchen"
    assert city_slug("K\u00f8benhavn") == "kobenhavn"
    assert city_slug("St. Moritz") == "st_moritz"
    assert city_slug("Cortina d'Ampezzo") == "cortina_d_ampezzo"
    assert city_slug("Gen\u00e8ve") == "geneve"


def master_data(root, stores):
    """The ERP rows the module reads to know each store's local day."""
    path = root / "erp" / "master_data" / "stores.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "store_id,timezone\n" + "".join(f"{store_id},Europe/Rome\n" for store_id in stores),
        encoding="utf-8",
    )
    return root


def test_real_cold_spell_in_zurich_is_one_context_event(tmp_path):
    request = spec(["ZRH01"])
    found, status, published = events_of(tmp_path, request)
    assert published and status.status == "succeeded"
    assert status.result.counts == {"cities": 1, "events": 1}
    (event,) = found
    assert event.id == "ctx-zuerich-cold-20261011"
    assert event.kind == "weather_cold"
    assert event.role == "context_only"
    assert event.store_ids == ("ZRH01",)
    assert event.start.astimezone(ROME).date() == date(2026, 10, 11)
    assert event.end.astimezone(ROME).date() == date(2026, 10, 21)
    assert event.available_at == datetime(2026, 10, 21, 21, 59, 59, tzinfo=UTC)
    assert event.availability_basis == "weather_observation_day_end"
    assert event.issued_at is None
    assert event.magnitude.kind == "vague" and event.magnitude.value is None
    assert "vs the 2026-09-01..2026-09-30 reference mean 13.2" in event.magnitude.raw
    assert "11 consecutive days of cold weather 2026-10-11..2026-10-21" in event.description
    assert "coldest day 1.2" in event.description
    (ref,) = event.source_refs
    source = SOURCES / ref.uri.removeprefix("dataset://")
    assert ref.content_hash == f"sha256:{hashlib.sha256(source.read_bytes()).hexdigest()}"
    assert ref.locator == "daily[2026-10-11..2026-10-21]"


def test_file_name_is_not_a_coverage_promise():
    """`paris_..._2026-10-21.json` stops on the 20th: rows decide, never the name."""
    assert max(load_city(SOURCES, "Paris").days) == date(2026, 10, 20)


def test_no_day_after_as_of_is_backdated(tmp_path):
    """The export is a bulk download: days after as_of are in it and must not be emitted."""
    root = write_sources(tmp_path / "sources", {"Milano": ["MIL01"]})
    write_feed(
        root,
        "Milano",
        reference_weather(
            **{
                "2026-10-01": 5.0,
                "2026-10-02": 5.0,
                "2026-10-03": 5.0,
                "2026-10-04": 5.0,
                "2026-10-05": -12.0,  # after as_of: a leak would lengthen the spell
                "2026-10-06": -12.0,
            }
        ),
    )
    as_of = datetime(2026, 10, 4, 22, 0, tzinfo=UTC)  # 00:00 on the 5th in Milan
    request = spec(["MIL01"], as_of)
    found, status, _ = events_of(tmp_path, request, root)
    assert status.result.counts["events"] == 1
    (event,) = found
    assert event.end.astimezone(ROME).date() == date(2026, 10, 4)
    assert event.available_at <= as_of
    assert "2026-10-05" not in event.description
    assert "2026-10-05" not in (event.magnitude.raw or "")


def test_a_day_is_available_only_once_its_local_day_has_ended():
    morning = datetime(2026, 10, 20, 9, 59, tzinfo=UTC)  # 11:59 in Milan
    evening = datetime(2026, 10, 20, 21, 59, 59, tzinfo=UTC)  # 23:59:59 in Milan
    assert external.completed_day(morning, ROME) == date(2026, 10, 19)
    assert external.completed_day(evening, ROME) == date(2026, 10, 20)


def test_reference_is_the_month_before_the_window(tmp_path):
    root = write_sources(tmp_path / "sources", {"Milano": ["MIL01"]})
    write_feed(
        root,
        "Milano",
        reference_weather(**{day.isoformat(): 10.0 for day in days("2026-10-01", "2026-10-21")}),
    )
    found, _, _ = events_of(tmp_path, spec(["MIL01"]), root)
    (event,) = found
    assert event.kind == "weather_cold"
    assert "reference mean 20.0" in event.description


def test_a_gap_breaks_the_spell_in_two(tmp_path):
    series = reference_weather(**{day.isoformat(): 5.0 for day in days("2026-10-05", "2026-10-12")})
    del series[date(2026, 10, 8)]  # no measurement: not a cold day, not a 20 C day
    root = write_sources(tmp_path / "sources", {"Milano": ["MIL01"]})
    write_feed(root, "Milano", series)
    found, status, _ = events_of(tmp_path, spec(["MIL01"]), root)
    assert status.result.counts["events"] == 2
    assert [
        (event.id, event.start.astimezone(ROME).date(), event.end.astimezone(ROME).date())
        for event in found
    ] == [
        ("ctx-milano-cold-20261005", date(2026, 10, 5), date(2026, 10, 7)),
        ("ctx-milano-cold-20261009", date(2026, 10, 9), date(2026, 10, 12)),
    ]


def test_a_short_dip_is_not_an_event(tmp_path):
    series = reference_weather(
        **{"2026-10-05": 5.0, "2026-10-06": 5.0, "2026-10-07": 19.0, "2026-10-08": 5.0}
    )
    root = write_sources(tmp_path / "sources", {"Milano": ["MIL01"]})
    write_feed(root, "Milano", series)
    found, status, _ = events_of(tmp_path, spec(["MIL01"]), root)
    assert found == [] and status.status == "succeeded"
    assert status.result.counts["events"] == 0


def test_warm_spell_is_its_own_kind(tmp_path):
    series = reference_weather(
        **{day.isoformat(): 34.0 for day in days("2026-10-10", "2026-10-13")}
    )
    root = write_sources(tmp_path / "sources", {"Milano": ["MIL01"]})
    write_feed(root, "Milano", series)
    found, _, _ = events_of(tmp_path, spec(["MIL01"]), root)
    (event,) = found
    assert event.kind == "weather_warm"
    assert "warmest day 34.0" in event.description
    assert (event.magnitude.raw or "").startswith("+")


def test_a_fahrenheit_feed_is_refused_not_converted(tmp_path):
    series = reference_weather(**{day.isoformat(): 5.0 for day in days("2026-10-05", "2026-10-10")})
    root = write_sources(tmp_path / "sources", {"Milano": ["MIL01"]}, units="\u00b0F")
    write_feed(root, "Milano", series, units="\u00b0F")
    found, status, _ = events_of(tmp_path, spec(["MIL01"]), root)
    assert found == []
    assert status.status == "degraded"
    assert status.result.counts["events"] == 0
    assert status.result.errors and "refusing to convert" in status.result.errors[0]


def test_old_and_new_schema_are_one_series(tmp_path):
    """v1 has no `temperature_2m_mean`: the mid-range keeps one definition across the change."""
    root = tmp_path / "sources"
    series = reference_weather(**{day.isoformat(): 5.0 for day in days("2026-09-28", "2026-10-06")})
    split = date(2026, 10, 1)
    for name, rows, version in (
        ("milano_2024-09-01_2026-02-28.json", [d for d in sorted(series) if d < split], "v1"),
        ("milano_2026-03-01_2026-10-21.json", [d for d in sorted(series) if d >= split], "v2"),
    ):
        payload = {
            "timezone": "Europe/Rome",
            "api_version": version,
            "daily_units": {"temperature_2m_max": DEGREE, "temperature_2m_min": DEGREE},
            "daily": {
                "time": [d.isoformat() for d in rows],
                "temperature_2m_max": [series[d] for d in rows],
                "temperature_2m_min": [series[d] for d in rows],
            },
        }
        (root / FEED).mkdir(parents=True, exist_ok=True)
        (root / FEED / name).write_text(json.dumps(payload))
    (root / COVERAGE).write_text(
        "city,stores,primary_provider_folder\nMilano,MIL01,eu_meteoarchive\n", encoding="utf-8"
    )
    master_data(root, ["MIL01"])
    params = {"window_days": 30}  # wide enough to hold the whole spell
    found, status, _ = events_of(tmp_path, spec(["MIL01"], params=params), root)
    assert status.status == "succeeded", status.result.errors
    (event,) = found
    assert event.start.astimezone(ROME).date() == date(2026, 9, 28)
    assert event.end.astimezone(ROME).date() == date(2026, 10, 6)
    assert len(event.source_refs) == 2


def test_conflicting_duplicate_day_is_refused(tmp_path):
    root = write_sources(tmp_path / "sources", {"Milano": ["MIL01"]})
    second = {
        "timezone": "Europe/Rome",
        "daily_units": {"temperature_2m_max": DEGREE, "temperature_2m_min": DEGREE},
        "daily": {
            "time": ["2026-10-06"],
            "temperature_2m_max": [30.0],
            "temperature_2m_min": [30.0],
        },
    }
    (root / FEED / "milano_2026-03-01_2026-10-21.json").write_text(json.dumps(second))
    found, status, _ = events_of(tmp_path, spec(["MIL01"]), root)
    assert found == [] and status.status == "degraded"
    assert status.result.errors and "two values for 2026-10-06" in status.result.errors[0]


def test_thin_reference_abstains(tmp_path):
    """Only the window and two days before it: no baseline, so no claim."""
    root = tmp_path / "sources"
    series = {date(2026, 9, 29): 20.0, date(2026, 9, 30): 20.0}
    series.update({day: 20.0 for day in days("2026-10-01", "2026-10-21")})
    (root / FEED).mkdir(parents=True, exist_ok=True)
    write_feed(root, "Milano", series)
    (root / COVERAGE).write_text(
        "city,stores,primary_provider_folder\nMilano,MIL01,eu_meteoarchive\n", encoding="utf-8"
    )
    master_data(root, ["MIL01"])
    found, status, _ = events_of(tmp_path, spec(["MIL01"]), root)
    assert found == [] and status.status == "succeeded"
    assert (
        status.result.abstentions
        and "no reference to score against" in (status.result.abstentions[0])
    )


def test_stores_with_this_provider_are_the_only_cities_read(tmp_path):
    request = spec(["MIL01", "NYC01"])
    found, status, _ = events_of(tmp_path, request)
    assert status.result.counts == {"cities": 1, "events": 1}
    assert {event.store_ids for event in found} == {("MIL01",)}
    assert any("New York is covered by us_ncei_ghcnd" in text for text in status.result.abstentions)


def test_spell_cut_by_the_window_says_so(tmp_path):
    series = reference_weather(**{day.isoformat(): 5.0 for day in days("2026-09-25", "2026-10-21")})
    root = write_sources(tmp_path / "sources", {"Milano": ["MIL01"]})
    write_feed(root, "Milano", series)
    request = spec(["MIL01"], params={"window_days": 7})
    found, _, _ = events_of(tmp_path, request, root)
    (event,) = found
    # Window 2026-10-15..2026-10-21: the spell began on 09-25, long before it.
    assert event.start.astimezone(ROME).date() == date(2026, 10, 15)
    assert event.id == "ctx-milano-cold-20261015"
    assert "already running before the window opened" in event.description


def test_feed_timezone_contradicting_the_master_data_is_reported(tmp_path):
    """London's summer file says GMT across BST: the store's zone bounds the day, and we say so."""
    found, status, published = events_of(tmp_path, spec(["LON01", "LON02"]))
    assert published
    assert status.status == "degraded"
    assert status.result.errors == (
        "London: external/weather/eu_meteoarchive/london_2026-03-01_2026-10-21.json says GMT "
        "while the store's timezone is Europe/London; its days are bounded by the store's"
        " timezone",
    )
    (event,) = found
    assert event.store_ids == ("LON01", "LON02")
    assert event.end.astimezone(ZoneInfo("Europe/London")).date() == date(2026, 10, 19)


def test_run_publishes_events_scoped_to_its_stores(tmp_path):
    request = spec(["MIL01", "ZRH01", "PAR01"], run_id="scope-run")
    engine, status = execute(tmp_path, request)
    with repo_session(engine, request) as repo:
        found = repo.list(ContextEvent)
        by_store = {
            store_id: [event.id for event in repo.list(ContextEvent, store_id=store_id)]
            for store_id in ("ZRH01", "PAR01")
        }
        assert repo.run_state()["published"]
    engine.dispose()
    assert status.status == "succeeded"
    assert status.result.counts == {"cities": 3, "events": 4}  # Paris has two spells
    assert {event.store_ids for event in found} == {("MIL01",), ("ZRH01",), ("PAR01",)}
    assert by_store == {
        "ZRH01": ["ctx-zuerich-cold-20261011"],
        "PAR01": ["ctx-paris-cold-20261003", "ctx-paris-cold-20261013"],
    }
    assert all(event.available_at <= request.as_of for event in found)
    assert [event.id for event in found] == sorted(event.id for event in found)
