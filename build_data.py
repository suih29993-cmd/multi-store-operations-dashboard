# -*- coding: utf-8 -*-
"""Build a validated dashboard payload from synthetic channel snapshots."""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT_DIR = ROOT / "demo_input"
OUTPUT = ROOT / "data.json"

BASE_METRICS = [
    "channel_a_goods_sat", "channel_a_pack_sat", "channel_a_repeat_score", "channel_a_food_safe",
    "channel_a_reply_score", "channel_a_service_fb", "channel_a_repeat", "channel_a_reply",
    "channel_b_taste_sat", "channel_b_pack_sat", "channel_b_repeat_score", "channel_b_food_safe",
    "channel_b_reply_score", "channel_b_service_fb", "channel_b_reply", "channel_b_cancel",
]
REQUIRED_FIELDS = [
    "period_id", "period_start", "period_end", "store_id", "store_name",
    "region", "province", "city", "supervisor", "store_type", "status",
] + BASE_METRICS + [f"{name}_prev" for name in BASE_METRICS]
ALL_METRICS = BASE_METRICS + [
    "channel_a_quality", "channel_a_service", "channel_a_score",
    "channel_b_quality", "channel_b_service", "channel_b_score",
]


def _number(value: str, field: str, row_no: int) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"row {row_no}: {field} must be numeric") from exc
    if not math.isfinite(number):
        raise ValueError(f"row {row_no}: {field} must be finite")
    return number


def _metric(current: float, previous: float) -> dict:
    current, previous = round(current, 4), round(previous, 4)
    return {"cur": current, "prev": previous, "delta": round(current - previous, 4)}


def _derive_row(raw: dict, row_no: int) -> dict:
    values = {name: _number(raw[name], name, row_no) for name in BASE_METRICS}
    previous = {name: _number(raw[f"{name}_prev"], f"{name}_prev", row_no) for name in BASE_METRICS}

    def quality(prefix: str, taste: str, source: dict) -> float:
        return round((
            source[taste] * 0.30 + source[f"{prefix}_pack_sat"] * 0.10
            + source[f"{prefix}_repeat_score"] * 0.20 + source[f"{prefix}_food_safe"] * 0.20
        ) / 0.80, 4)

    def service(prefix: str, source: dict) -> float:
        return round((
            source[f"{prefix}_reply_score"] * 0.10 + source[f"{prefix}_service_fb"] * 0.10
        ) / 0.20, 4)

    for source in (values, previous):
        a_quality = quality("channel_a", "channel_a_goods_sat", source)
        a_service = service("channel_a", source)
        b_quality = quality("channel_b", "channel_b_taste_sat", source)
        b_service = service("channel_b", source)
        source["channel_a_quality"] = a_quality
        source["channel_a_service"] = a_service
        source["channel_a_score"] = round(a_quality * 0.8 + a_service * 0.2, 4)
        source["channel_b_quality"] = b_quality
        source["channel_b_service"] = b_service
        source["channel_b_score"] = round(b_quality * 0.8 + b_service * 0.2, 4)

    return {
        "id": raw["store_id"].strip(),
        "name": raw["store_name"].strip(),
        "region": raw["region"].strip(),
        "province": raw["province"].strip(),
        "city": raw["city"].strip(),
        "supervisor": raw["supervisor"].strip(),
        "type": raw["store_type"].strip(),
        "status": "Open" if raw["status"].strip().lower() == "open" else raw["status"].strip(),
        "metrics": {name: _metric(values[name], previous[name]) for name in ALL_METRICS},
    }


def _aggregate(stores: list[dict]) -> dict:
    result = {}
    for name in ALL_METRICS:
        current = [store["metrics"][name]["cur"] for store in stores]
        previous = [store["metrics"][name]["prev"] for store in stores]
        if not current:
            result[name] = {"cur": None, "prev": None, "delta": None}
            continue
        cur = round(sum(current) / len(current), 4)
        prev = round(sum(previous) / len(previous), 4)
        result[name] = {"cur": cur, "prev": prev, "delta": round(cur - prev, 4)}
    return result


def build_period(rows: list[dict], meta: dict) -> dict:
    stores = [_derive_row(row, index + 2) for index, row in enumerate(rows)]
    if len({store["id"] for store in stores}) != len(stores):
        raise ValueError(f"{meta['period']}: duplicate store_id")
    regions = sorted({store["region"] for store in stores})
    supervisors = sorted({store["supervisor"] for store in stores})
    cities = sorted({store["city"] for store in stores})
    region_summary = [{"name": "All_Regions", "metrics": _aggregate(stores)}]
    region_summary += [
        {"name": region, "metrics": _aggregate([s for s in stores if s["region"] == region])}
        for region in regions
    ]
    supervisor_summary = [
        {
            "name": supervisor,
            "region": next(s["region"] for s in stores if s["supervisor"] == supervisor),
            "metrics": _aggregate([s for s in stores if s["supervisor"] == supervisor]),
        }
        for supervisor in supervisors
    ]
    city_summary = [
        {
            "region": next(s["region"] for s in stores if s["city"] == city),
            "city": city,
            "storeCount": sum(1 for s in stores if s["city"] == city),
            "metrics": _aggregate([s for s in stores if s["city"] == city]),
        }
        for city in cities
    ]
    return {
        "meta": {
            "period": f"{meta['period_start']} ~ {meta['period_end']}",
            "prevPeriod": meta["prev_period"],
            "dataSource": "Synthetic demo data (seed 20261020)",
            "storeTotal": len(stores),
            "openTotal": sum(1 for store in stores if store["status"] == "Open"),
            "matchedStores": len(stores),
        },
        "region_summary": region_summary,
        "supervisor_summary": supervisor_summary,
        "city_summary": city_summary,
        "stores": stores,
    }


def load_inputs() -> dict:
    paths = sorted(INPUT_DIR.glob("period_*.csv"))
    if not paths:
        raise SystemExit("No demo_input/period_*.csv files found.")
    periods = []
    for path in paths:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            missing = [field for field in REQUIRED_FIELDS if field not in (reader.fieldnames or [])]
            if missing:
                raise ValueError(f"{path.name}: missing columns: {', '.join(missing)}")
            rows = list(reader)
        if not rows:
            raise ValueError(f"{path.name}: empty input")
        period_id = rows[0]["period_id"].strip()
        if any(row["period_id"].strip() != period_id for row in rows):
            raise ValueError(f"{path.name}: mixed period_id values")
        periods.append({
            "id": period_id, "start": rows[0]["period_start"].strip(),
            "end": rows[0]["period_end"].strip(), "rows": rows,
        })
    periods.sort(key=lambda item: item["start"])
    result = {}
    for index, period in enumerate(periods):
        previous = periods[index - 1] if index else None
        result[period["id"]] = build_period(period["rows"], {
            "period": period["id"], "period_start": period["start"],
            "period_end": period["end"], "prev_period": previous["id"] if previous else "N/A",
        })
    return {
        "defaultPeriod": periods[-1]["id"],
        "_order": [period["id"] for period in periods],
        "periods": result,
    }


def validate(payload: dict) -> None:
    if not payload["periods"]:
        raise ValueError("payload has no periods")
    for key, period in payload["periods"].items():
        if not period["stores"]:
            raise ValueError(f"{key}: no stores")
        for store in period["stores"]:
            missing = [name for name in ALL_METRICS if name not in store["metrics"]]
            if missing:
                raise ValueError(f"{key}/{store['id']}: missing metrics {missing}")
            for score in ("channel_a_score", "channel_b_score"):
                if not 1.0 <= store["metrics"][score]["cur"] <= 5.0:
                    raise ValueError(f"{key}/{store['id']}: {score} outside 1-5")
            for rate in ("channel_a_repeat", "channel_a_reply", "channel_b_reply", "channel_b_cancel"):
                if not 0.0 <= store["metrics"][rate]["cur"] <= 1.0:
                    raise ValueError(f"{key}/{store['id']}: {rate} outside 0-1")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build synthetic dashboard data")
    parser.add_argument("--check", action="store_true", help="validate only")
    args = parser.parse_args()
    payload = load_inputs()
    validate(payload)
    if args.check:
        print("validation passed")
        return
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {OUTPUT} ({len(payload['periods'])} periods)")


if __name__ == "__main__":
    main()
