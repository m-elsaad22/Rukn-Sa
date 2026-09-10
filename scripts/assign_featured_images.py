#!/usr/bin/env python3
"""Assign featured images by service family instead of leftover sewer/pool photos."""
from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rewrite_unique_articles import parse_title
from service_packs import family_of
from wp_client import get_paged, put

ROOT = Path(__file__).resolve().parents[1]

# Real media IDs currently in the SA library (names from REST, not invented photos).
FAM_MEDIA = {
    "leak": 10623,
    "insul_water": 11080,
    "insul_thermal": 11080,
    "insul_sound": 2881,  # wall insulation
    "insul_kitchen": 11080,
    "insul_bath": 2879,
    "tank": 2689,
    "plumb": 2824,
    "ac": 2702,
    "pest": 2788,
    "pest_bedbug": 2788,
    "pest_gecko": 2788,
    "pest_scorpion": 2788,
    "pest_birds": 2788,
    "pest_fly": 2788,
    "pest_ant": 2788,
    "pest_flea": 2788,
    "pest_snake": 2788,
    "clean": 2684,
    "clean_tank": 2689,
    "clean_diesel": 2689,
    "clean_facade": 2684,
    "clean_upholstery": 2684,
    "pool": 2896,
    "garden": 2706,
    "paint": 2881,
    "gypsum": 2733,
    "floor": 2600,
    "tile": 2600,
    "stone": 2600,
    "move": 2733,
    "elec": 2689,
    "restore": 2733,
    "humidity": 2879,
    "inspect": 2688,
    "appliance": 2733,
    "carpenter": 2600,
    "blacksmith": 2733,
    "maint": 2733,
    "install": 2733,
    "default": 2733,
}

SERVICE_MEDIA = {
    1866: 2733,   # buildings / general maintenance toolbox
    1868: 2896,   # pools
    1870: 2706,   # landscaping
    1872: 2600,   # parquet
    1874: 2733,   # gypsum
    1876: 2881,   # sound insulation
    1877: 10623,  # leak
    1879: 11080,  # roof/tank insulation
    1881: 2824,   # sewer
    1883: 2702,   # AC
    1885: 2684,   # cleaning
    1887: 2788,   # pest
}

SKIP_IDS = {10603, 10604, 10274, 9333, 9287, 10293, 10292}


def media_for(title: str) -> int:
    city, svc = parse_title(title)
    fam = family_of(svc)
    return FAM_MEDIA.get(fam, FAM_MEDIA["default"])


def update_one(item: dict) -> dict:
    pid = item["id"]
    title = item["title"]
    current = int(item.get("featured_media") or 0)
    wanted = media_for(title)
    if pid in SKIP_IDS:
        return {"id": pid, "skipped": "protected", "current": current}
    if current == wanted:
        return {"id": pid, "skipped": "already", "current": current}
    put(f"/wp/v2/posts/{pid}", {"featured_media": wanted})
    return {"id": pid, "from": current, "to": wanted, "title": title}


def main() -> None:
    posts = get_paged(
        "/wp/v2/posts",
        extra="&status=publish&_fields=id,title,featured_media",
    )
    rows = []
    for p in posts:
        title = (p.get("title") or {}).get("rendered") or ""
        rows.append({"id": p["id"], "title": title, "featured_media": p.get("featured_media") or 0})

    changed = []
    skipped = 0
    errors = []
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = [ex.submit(update_one, r) for r in rows]
        for fut in as_completed(futs):
            try:
                res = fut.result()
                if res.get("to"):
                    changed.append(res)
                else:
                    skipped += 1
            except Exception as e:
                errors.append(str(e)[:250])

    for sid, mid in SERVICE_MEDIA.items():
        try:
            put(f"/wp/v2/services/{sid}", {"featured_media": mid})
            changed.append({"id": sid, "type": "service", "to": mid})
        except Exception as e:
            errors.append(f"service {sid}: {e}")
        time.sleep(0.05)

    report = {
        "scanned": len(rows),
        "changed": len([c for c in changed if c.get("type") != "service"]),
        "services": [c for c in changed if c.get("type") == "service"],
        "skipped": skipped,
        "errors": errors[:40],
        "sample": changed[:25],
    }
    out = ROOT / "reports" / "featured-image-fix.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("scanned", "changed", "skipped")}, ensure_ascii=False))
    print("errors", len(errors))


if __name__ == "__main__":
    main()
