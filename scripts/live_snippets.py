#!/usr/bin/env python3
"""Install/update live Code Snippets and apply NAP/trust option fixes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_client import get, post, put

ROOT = Path(__file__).resolve().parents[1]
SNIPPET_FILE = ROOT / "snippets" / "rukn-sa-trust-fix.php"
META_BRIDGE_FILE = ROOT / "snippets" / "rukn-rest-meta-bridge.php"
COPY_GUARD_FILE = ROOT / "snippets" / "rukn-sa-copy-guard.php"


def find_snippet(name: str) -> dict | None:
    body, _ = get("/code-snippets/v1/snippets?per_page=100")
    for s in body or []:
        if s.get("name") == name:
            return s
    return None


def upsert_snippet(name: str, code: str, desc: str, active: bool = True) -> dict:
    # Strip opening php tag if present; Code Snippets stores raw PHP body.
    body_code = code.strip()
    if body_code.startswith("<?php"):
        body_code = body_code[5:].lstrip()
    existing = find_snippet(name)
    payload = {
        "name": name,
        "desc": desc,
        "code": body_code,
        "scope": "global",
        "active": active,
        "priority": 10,
    }
    if existing:
        out, _ = put(f"/code-snippets/v1/snippets/{existing['id']}", payload)
        return {"action": "updated", "id": out.get("id"), "active": out.get("active")}
    out, _ = post("/code-snippets/v1/snippets", payload)
    return {"action": "created", "id": out.get("id"), "active": out.get("active")}


def main() -> None:
    report: dict = {"snippets": []}
    report["snippets"].append(
        upsert_snippet(
            "Rukn SA Trust NAP Fix",
            SNIPPET_FILE.read_text(encoding="utf-8"),
            "Unify Saudi NAP, remove Egyptian leftover numbers, honest homepage stats.",
            True,
        )
    )
    report["snippets"].append(
        upsert_snippet(
            "Rukn REST Meta Bridge for Article Blocks",
            META_BRIDGE_FILE.read_text(encoding="utf-8"),
            "Expose Kayan article/service/page block meta to REST.",
            True,
        )
    )
    report["snippets"].append(
        upsert_snippet(
            "Rukn SA Frontend Copy Guard",
            COPY_GUARD_FILE.read_text(encoding="utf-8"),
            "Replace leftover UAE/Egypt copy in frontend HTML.",
            True,
        )
    )

    applied, _ = post("/rukn/v1/apply-trust-fix", {})
    report["apply_trust_fix"] = applied
    keys, _ = get("/rukn/v1/dump-keys")
    report["dump_keys"] = keys

    # deactivate noisy inspect snippet if present
    inspect = find_snippet("Rukn Inspect Options (temp)")
    if inspect and inspect.get("active"):
        put(f"/code-snippets/v1/snippets/{inspect['id']}", {"active": False})
        report["deactivated_inspect"] = inspect["id"]

    out = ROOT / "reports" / "trust-nap-fix.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"snippets": report["snippets"], "apply_ok": (applied or {}).get("ok")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
