"""Aggregate the 38 unique Phase-3 builders by slug."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from catalog_car import (  # noqa: E402
    car_abha,
    car_dammam,
    car_jeddah,
    car_khobar,
    car_mecca,
    car_medina,
    car_riyadh,
    car_taif,
)
from catalog_hvac import (  # noqa: E402
    ac_abha,
    ac_dammam,
    ac_jeddah,
    ac_khobar,
    ac_mecca,
    ac_medina,
    ac_riyadh,
    ac_taif,
    duct_dammam,
    duct_jeddah,
    duct_khobar,
    duct_mecca,
    duct_medina,
    duct_riyadh,
    duct_taif,
)
from catalog_ship import (  # noqa: E402
    domestic_abha,
    domestic_dammam,
    domestic_jeddah,
    domestic_khobar,
    domestic_mecca,
    domestic_medina,
    domestic_riyadh,
    domestic_taif,
    furniture_abha,
    furniture_dammam,
    furniture_jeddah,
    furniture_khobar,
    furniture_medina,
    furniture_riyadh,
    furniture_taif,
)
from extras import EXTRAS  # noqa: E402
from fieldguide import GUIDE  # noqa: E402
from longform import LONG  # noqa: E402

BUILDERS = {
    "car-shipping-jeddah": car_jeddah,
    "car-shipping-riyadh": car_riyadh,
    "car-shipping-dammam": car_dammam,
    "car-shipping-khobar": car_khobar,
    "car-shipping-mecca": car_mecca,
    "car-shipping-medina": car_medina,
    "car-shipping-taif": car_taif,
    "car-shipping-abha": car_abha,
    "domestic-shipping-dammam": domestic_dammam,
    "domestic-shipping-khobar": domestic_khobar,
    "domestic-shipping-riyadh": domestic_riyadh,
    "domestic-shipping-jeddah": domestic_jeddah,
    "domestic-shipping-mecca": domestic_mecca,
    "domestic-shipping-medina": domestic_medina,
    "domestic-shipping-taif": domestic_taif,
    "domestic-shipping-abha": domestic_abha,
    "furniture-shipping-dammam": furniture_dammam,
    "furniture-shipping-khobar": furniture_khobar,
    "furniture-shipping-riyadh": furniture_riyadh,
    "furniture-shipping-jeddah": furniture_jeddah,
    "furniture-shipping-taif": furniture_taif,
    "furniture-shipping-abha": furniture_abha,
    "furniture-shipping-medina": furniture_medina,
    "duct-cleaning-dammam": duct_dammam,
    "duct-cleaning-khobar": duct_khobar,
    "duct-cleaning-riyadh": duct_riyadh,
    "duct-cleaning-jeddah": duct_jeddah,
    "duct-cleaning-mecca": duct_mecca,
    "duct-cleaning-medina": duct_medina,
    "duct-cleaning-taif": duct_taif,
    "ac-cleaning-washing-riyadh": ac_riyadh,
    "ac-cleaning-washing-jeddah": ac_jeddah,
    "ac-cleaning-washing-dammam": ac_dammam,
    "ac-cleaning-washing-khobar": ac_khobar,
    "ac-cleaning-washing-mecca": ac_mecca,
    "ac-cleaning-washing-medina": ac_medina,
    "ac-cleaning-washing-taif": ac_taif,
    "ac-cleaning-washing-abha": ac_abha,
}


def entry_for_slug(slug: str) -> dict:
    if slug not in BUILDERS:
        raise KeyError(slug)
    entry = BUILDERS[slug]()
    entry["slug"] = slug
    extra = EXTRAS.get(slug) or {}
    long_sections = list(LONG.get(slug) or []) + list(GUIDE.get(slug) or [])
    if extra.get("sections") or long_sections:
        entry["sections"] = (
            list(entry.get("sections") or [])
            + list(long_sections)
            + list(extra.get("sections") or [])
        )
    if extra.get("faqs"):
        entry["faqs"] = list(entry.get("faqs") or []) + list(extra["faqs"])
    if extra.get("added"):
        entry["added"] = list(entry.get("added") or []) + list(extra["added"])
    return entry


def all_entries() -> list[dict]:
    return [entry_for_slug(slug) for slug in BUILDERS]


def slugs() -> list[str]:
    return list(BUILDERS)
