# -*- coding: utf-8 -*-
"""Generate deterministic synthetic inputs for the public dashboard demo."""
from __future__ import annotations

import csv
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "demo_input"

PERIODS = [
    ("Period_01", "2026-07-01", "2026-07-14"),
    ("Period_02", "2026-07-15", "2026-07-28"),
    ("Period_03", "2026-07-29", "2026-08-11"),
]

BASE_METRICS = [
    "channel_a_goods_sat", "channel_a_pack_sat", "channel_a_repeat_score", "channel_a_food_safe",
    "channel_a_reply_score", "channel_a_service_fb", "channel_a_repeat", "channel_a_reply",
    "channel_b_taste_sat", "channel_b_pack_sat", "channel_b_repeat_score", "channel_b_food_safe",
    "channel_b_reply_score", "channel_b_service_fb", "channel_b_reply", "channel_b_cancel",
]

FIELDS = [
    "period_id", "period_start", "period_end", "store_id", "store_name",
    "region", "province", "city", "supervisor", "store_type", "status",
] + BASE_METRICS + [f"{name}_prev" for name in BASE_METRICS]


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def build_row(period_idx: int, period: tuple[str, str, str], store_idx: int) -> dict:
    period_id, start, end = period
    region = "Region_A" if store_idx <= 30 else "Region_B"
    letter = region[-1]
    local_idx = store_idx if region == "Region_A" else store_idx - 30
    supervisor_no = (local_idx - 1) // 8 + 1
    city_no = (local_idx - 1) // 10 + 1
    rng = random.Random(20261020 + period_idx * 1000 + store_idx * 17)

    store_effect = ((store_idx * 37) % 23 - 11) / 100.0
    period_effect = [0.00, 0.04, 0.08][period_idx]
    region_effect = 0.05 if region == "Region_A" else 0.0
    center = 4.45 + store_effect + period_effect + region_effect

    def score() -> tuple[float, float]:
        current = clamp(center + rng.uniform(-0.18, 0.18), 3.55, 4.95)
        previous = clamp(current - rng.uniform(-0.12, 0.16), 3.55, 4.95)
        return round(current, 4), round(previous, 4)

    values: dict[str, float] = {}
    for metric in [
        "channel_a_goods_sat", "channel_a_pack_sat", "channel_a_repeat_score", "channel_a_food_safe",
        "channel_a_reply_score", "channel_a_service_fb", "channel_b_taste_sat", "channel_b_pack_sat",
        "channel_b_repeat_score", "channel_b_food_safe", "channel_b_reply_score", "channel_b_service_fb",
    ]:
        values[metric], values[f"{metric}_prev"] = score()

    values["channel_a_repeat"] = round(clamp(0.24 + (center - 4.2) * 0.12 + rng.uniform(-0.04, 0.04), 0.12, 0.52), 4)
    values["channel_a_repeat_prev"] = round(clamp(0.23 + (center - 4.2) * 0.10 + rng.uniform(-0.04, 0.04), 0.12, 0.52), 4)
    values["channel_a_reply"] = round(clamp(0.84 + (center - 4.2) * 0.06 + rng.uniform(-0.03, 0.03), 0.68, 0.995), 4)
    values["channel_a_reply_prev"] = round(clamp(0.83 + (center - 4.2) * 0.05 + rng.uniform(-0.03, 0.03), 0.68, 0.995), 4)
    values["channel_b_reply"] = round(clamp(0.88 + (center - 4.2) * 0.05 + rng.uniform(-0.025, 0.025), 0.72, 0.999), 4)
    values["channel_b_reply_prev"] = round(clamp(0.87 + (center - 4.2) * 0.04 + rng.uniform(-0.025, 0.025), 0.72, 0.999), 4)
    values["channel_b_cancel"] = round(clamp(0.0042 - (center - 4.2) * 0.0014 + rng.uniform(-0.0012, 0.0012), 0.0002, 0.012), 4)
    values["channel_b_cancel_prev"] = round(clamp(0.0046 - (center - 4.2) * 0.0012 + rng.uniform(-0.0012, 0.0012), 0.0002, 0.012), 4)

    return {
        "period_id": period_id, "period_start": start, "period_end": end,
        "store_id": f"Store_{letter}{local_idx:03d}",
        "store_name": f"Demo Store {letter}{local_idx:03d}",
        "region": region, "province": f"Demo Province {letter}",
        "city": f"Demo City {letter}{city_no}",
        "supervisor": f"Supervisor_{letter}{supervisor_no}",
        "store_type": ["standard", "compact", "flagship"][store_idx % 3],
        "status": "Open" if store_idx not in {7, 46} else "Preparing",
        **values,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for period_idx, period in enumerate(PERIODS):
        path = OUT / f"period_{period_idx + 1:02d}.csv"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
            writer.writeheader()
            for store_idx in range(1, 61):
                writer.writerow(build_row(period_idx, period, store_idx))
        print(f"wrote {path} (60 rows)")


if __name__ == "__main__":
    main()
