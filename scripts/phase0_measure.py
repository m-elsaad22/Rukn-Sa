#!/usr/bin/env python3
"""Read-only measurement against Phase 0 quality standard for Phase 1 inventory."""

from __future__ import annotations

import base64
import json
import re
import urllib.request
from difflib import SequenceMatcher
from pathlib import Path

BASE = "https://www.rukn-eltatawer.com/sa/wp-json"
AUTH = base64.b64encode(b"cursor:PCkk ig95 Gu6c zOgC GLYG FYsk").decode()
H = {"Authorization": f"Basic {AUTH}", "User-Agent": "Mozilla/5.0 RuknPhase0Measure/2026-11-09"}
ROOT = Path(__file__).resolve().parents[1]
INV = json.loads((ROOT / "data" / "phase1-inventory-2026-11-09.json").read_text(encoding="utf-8"))
CITIES_AR = ["الرياض", "جدة", "مكة المكرمة", "المدينة المنورة", "الدمام", "الخبر", "الطائف", "أبها", "مكة", "المدينة"]


def get(path: str):
    r = urllib.request.Request(BASE + path, headers=H)
    with urllib.request.urlopen(r, timeout=90) as resp:
        return json.loads(resp.read().decode())


def strip(html: str) -> str:
    t = re.sub(r"<[^>]+>", " ", html or "")
    return re.sub(r"\s+", " ", t).strip()


def ar_words(html: str) -> int:
    return len(re.findall(r"[\u0600-\u06FF]+", strip(html)))


def norm(text: str, n: int = 400) -> str:
    for c in CITIES_AR:
        text = text.replace(c, "CITY")
    return re.sub(r"\s+", " ", text)[:n]


def main():
    rows = []
    by_fam = {}
    for fam, cities in INV["targets"].items():
        by_fam[fam] = []
        for city, t in cities.items():
            p = get(f"/wp/v2/posts/{t['id']}?context=edit&_fields=id,slug,status,content,title")
            raw = p["content"].get("raw") or ""
            plain = strip(raw)
            words = ar_words(raw)
            row = {
                "id": t["id"],
                "fam": fam,
                "city": city,
                "slug": p["slug"],
                "status": p["status"],
                "words": words,
                "ge_3000": words >= 3000,
                "has_post_call": "[post_call]" in raw,
                "has_placeholder": bool(re.search(r"\{[A-Z_]{3,}\}", raw)),
                "op220": norm(plain, 220),
                "op400": norm(plain, 400),
            }
            rows.append(row)
            by_fam[fam].append(row)
            print(fam, city, words, "OK" if words >= 3000 else "LOW", flush=True)

    sim = []
    for fam, items in by_fam.items():
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a, b = items[i], items[j]
                if a["op220"] == b["op220"]:
                    sim.append({"fam": fam, "a": a["city"], "b": b["city"], "type": "exact"})
                r = SequenceMatcher(None, a["op400"], b["op400"]).ratio()
                if r >= 0.82:
                    sim.append({"fam": fam, "a": a["city"], "b": b["city"], "type": "ratio", "ratio": round(r, 3)})

    out = {
        "rows": rows,
        "under_3000": [r for r in rows if not r["ge_3000"]],
        "placeholders": [r for r in rows if r["has_placeholder"]],
        "similarity_fails": sim,
        "pass": len([r for r in rows if r["ge_3000"]]) == len(rows) and not sim,
    }
    path = ROOT / "data" / "phase1-measure-2026-11-09.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("PASS" if out["pass"] else "FAIL", "under", len(out["under_3000"]), "sim", len(sim), flush=True)


if __name__ == "__main__":
    main()
