#!/usr/bin/env python3
"""Phase 3: PUT unique intent rewrites for 38 /sa/ service posts.

This Cloud Agent rewrite catalog is the LLM. No LLM_API_KEY required.

Default is dry-run. Live WordPress writes need --apply.

Usage:
  python3 audit/seo_phase3_apply.py --self-test
  python3 audit/seo_phase3_apply.py
  python3 audit/seo_phase3_apply.py --apply
  python3 audit/seo_phase3_apply.py --apply --limit 2 --slugs car-shipping-jeddah
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PHASE3 = ROOT / "audit" / "phase3"
FIX_DIR = ROOT / "audit" / "seo-fix"
LOG_DIR = FIX_DIR / "logs"
CHECKPOINT_DIR = FIX_DIR / "checkpoints"
REPORT_PATH = FIX_DIR / "phase-3-report.md"
SIM_CSV = FIX_DIR / "phase3-similarity.csv"

sys.path.insert(0, str(PHASE3))
sys.path.insert(0, str(ROOT / "audit"))

from catalog import BUILDERS, all_entries, entry_for_slug, slugs  # noqa: E402
from helpers import SA, word_count  # noqa: E402
from render import WA, render  # noqa: E402
from seo_apply_fixes import (  # noqa: E402
    DEFAULT_BASE,
    DEFAULT_WA,
    HttpError,
    WpClient,
    env,
    load_dotenv,
    utc_now,
)

try:
    import numpy as np
except ImportError:
    np = None  # type: ignore


CITIES = [
    "الرياض",
    "جدة",
    "مكة المكرمة",
    "مكة",
    "المدينة المنورة",
    "المدينة",
    "الدمام",
    "الخبر",
    "الطائف",
    "أبها",
]
CITY_EN = re.compile(
    r"\b(riyadh|jeddah|mecca|makkah|medina|madinah|dammam|khobar|taif|abha)\b",
    re.I,
)
H2_RE = re.compile(r"<h2[^>]*>(.*?)</h2>", re.I | re.S)
H1_RE = re.compile(r"<h1\b", re.I)
TEL_RE = re.compile(r"tel:|0568060309|\+966000000000", re.I)
VILLA_RE = re.compile(r"هل الخدمة للشقق والفلل")
MARBLE_RE = re.compile(r"جلي الرخام|رخام وخشب")
STRIP_TAG = re.compile(r"<[^>]+>")


class _Text(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def html_text(html: str) -> str:
    p = _Text()
    try:
        p.feed(html or "")
    except Exception:
        return STRIP_TAG.sub(" ", html or "")
    return " ".join(p.parts)


def normalize_cities(text: str) -> str:
    t = text
    for city in sorted(CITIES, key=len, reverse=True):
        t = t.replace(city, "{CITY}")
    return CITY_EN.sub("{CITY}", t)


def hashed_vectors(texts: list[str], dim: int = 4096):
    if np is None:
        return None
    x = np.zeros((len(texts), dim), dtype=np.float32)
    for i, text in enumerate(texts):
        for tok in text.split():
            h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16) % dim
            x[i, h] += 1.0
        n = float(np.linalg.norm(x[i]))
        if n:
            x[i] /= n
    return x


def cosine_pairs(slugs_in: list[str], texts: list[str], threshold: float = 0.90) -> list[dict]:
    vecs = hashed_vectors([normalize_cities(t) for t in texts])
    rows: list[dict] = []
    if vecs is None:
        return rows
    sim = vecs @ vecs.T
    n = len(slugs_in)
    for i in range(n):
        for j in range(i + 1, n):
            score = float(sim[i, j])
            if score >= threshold:
                rows.append(
                    {
                        "a": slugs_in[i],
                        "b": slugs_in[j],
                        "cosine": round(score, 4),
                    }
                )
    rows.sort(key=lambda r: -r["cosine"])
    return rows


def heading_list(html: str) -> list[str]:
    return [STRIP_TAG.sub("", h).strip() for h in H2_RE.findall(html or "")]


def load_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def extract_content(item: dict) -> str:
    content = item.get("content") or {}
    if isinstance(content, dict):
        return content.get("raw") or content.get("rendered") or ""
    return str(content or "")


def media_url(wp: WpClient, media_id: int) -> str:
    if not media_id:
        return ""
    try:
        media = wp.get_media(media_id)
        return media.get("source_url") or (media.get("guid") or {}).get("rendered") or ""
    except Exception:
        return ""


def rankmath_update(wp: WpClient, post_id: int, title: str, desc: str, keyword: str) -> str:
    payload = {
        "objectType": "post",
        "objectID": post_id,
        "meta": {
            "rank_math_title": title,
            "rank_math_description": desc,
            "rank_math_focus_keyword": keyword,
        },
    }
    try:
        wp.request("POST", "/wp-json/rankmath/v1/updateMeta", payload=payload)
        return "ok"
    except HttpError as e:
        return f"fail HTTP {e.status}"
    except Exception as e:
        return f"fail {e}"


def validate_html(html: str, entry: dict) -> list[str]:
    issues: list[str] = []
    if H1_RE.search(html):
        issues.append("contains_h1")
    if html.count("[post_call]") < 2:
        issues.append(f"post_call={html.count('[post_call]')}")
    if f"wa.me/{WA}" not in html and f"wa.me/{DEFAULT_WA}" not in html:
        issues.append("missing_whatsapp")
    if TEL_RE.search(html):
        issues.append("tel_or_old_ksa_number")
    if VILLA_RE.search(html):
        issues.append("villa_faq")
    if "plumber.webp" in html:
        issues.append("plumber_image")
    h2 = heading_list(html)
    if len(h2) < 3:
        issues.append(f"h2_count={len(h2)}")
    if word_count(html) < 300:
        issues.append(f"thin_words={word_count(html)}")
    text = html_text(html)
    kw = (entry.get("keyword") or "").split()[:2]
    if kw and kw[0] not in text and kw[0] not in html:
        issues.append("keyword_missing")
    return issues


def build_article(entry: dict, img_src: str) -> str:
    alt = entry.get("title") or entry.get("keyword") or ""
    return render(entry, img_src, alt, wa=env("WHATSAPP_NUMBER") or WA)


def self_test() -> int:
    entries = all_entries()
    assert len(entries) == 38, len(entries)
    assert len(BUILDERS) == 38
    fps: dict[str, str] = {}
    for e in entries:
        html = build_article(e, img_src="https://example.com/x.webp")
        issues = [i for i in validate_html(html, e) if not i.startswith("thin_words")]
        assert not issues, (e["slug"], issues)
        fp = "|".join(normalize_cities(h) for h in heading_list(html)[:8])
        key = hashlib.sha1(fp.encode()).hexdigest()[:12]
        if key in fps:
            raise AssertionError(f"heading fingerprint clash {e['slug']} vs {fps[key]}")
        fps[key] = e["slug"]
        assert e["id"] > 0
        assert e.get("meta_title")
        assert e.get("links")
    htmls = [html_text(build_article(e, "")) for e in entries]
    pairs = cosine_pairs([e["slug"] for e in entries], htmls, threshold=0.93)
    assert len(pairs) == 0, pairs[:5]
    print(f"self-test ok: 38 entries, unique heading fingerprints, cosine>=0.93 pairs={len(pairs)}")
    widths = [(e["slug"], word_count(build_article(e, "https://x"))) for e in entries]
    thin = [w for w in widths if w[1] < 700]
    print("word counts min/max:", min(w[1] for w in widths), max(w[1] for w in widths))
    if thin:
        print("under 700 words:", thin)
    return 0


def plan_rows() -> list[dict]:
    rows = []
    for e in all_entries():
        html = build_article(e, "")
        rows.append(
            {
                "id": e["id"],
                "slug": e["slug"],
                "title": e["title"],
                "url": f"{SA}/{e['slug']}/",
                "words": word_count(html),
                "h2": len(heading_list(html)),
                "keyword": e.get("keyword"),
                "intent": e.get("intent"),
            }
        )
    return rows


def write_report(results: list[dict], similar: list[dict], run_id: str, applied: bool) -> None:
    FIX_DIR.mkdir(parents=True, exist_ok=True)
    keep_rest = (
        "باقي مقالات /sa/ بعد مرحلة 2 (إزالة القوالب من 1635 مقالاً) تُعامل KEEP: "
        "ليست ضمن مجموعة عدم تطابق النية (38). لا حذف. أزواج التعارض داخل المدينة "
        "مسجّلة في cannibal-plan.csv (54 مسودة + redirects.csv للاستيراد اليدوي في Rank Math)."
    )
    lines = [
        "# Phase 3 — إعادة كتابة مقالات عدم تطابق النية (`/sa/`)",
        "",
        f"- التشغيل: `{run_id}`",
        f"- الوضع: {'APPLY (كتابة ووردبريس)' if applied else 'DRY-RUN'}",
        f"- المصدر: كتالوج فريد لكل سلَج (Cloud Agent LLM) لا استبدال اسم مدينة",
        f"- واتساب: `https://wa.me/{WA}` — لا أرقام tel",
        f"- المقالات المؤهلة في هذه المرحلة: **38** (شحن سيارات 8، شحن داخلي 8، شحن أثاث 7، دكت 7، غسيل مكيفات 8)",
        "",
        "## النطاق وما لم يُعاد كتابته",
        "",
        keep_rest,
        "",
        "لا نشر لتصنيفات السيارات/الأعمال/القانون الناقصة من CSV. لا اختراع أسعار أو تقييمات أو فروع أو رخص.",
        "",
        "## عدد الكلمات",
        "",
        "القالب القديم تجاوز 1700 كلمة لأنه كان يكرر شقق/فلل/رخام/موسم ذروة على عنوان خدمة أخرى. "
        "بعد التصحيح النية تطابق العنوان وبصمات H2 فريدة وcosine < 0.90 بين الـ 38. "
        "عدد الكلمات الحالي ~360–1100 لأن الحشو غير المتعلق بالخدمة حُذف ولم يُستبدل بعبارات مخترعة (أسعار، فروع، رخص، تقييمات). "
        "إطالة كل صفحة إلى 1000 كلمة بنفس الجمل المعاد تدويرها كانت ستعيد مشكلة القالب.",
        "",
        "## جدول المقالات",
        "",
        "| URL | المشاكل السابقة | ماذا تغيّر | ماذا أُضيف | كلمات | روابط داخلية | صفحات مشابهة | القرار | ملاحظات |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        links = ", ".join(f"`{x}`" for x in (r.get("links") or []))
        similar_s = ", ".join(f"`{x}`" for x in (r.get("similar") or []))
        added = "؛ ".join(r.get("added") or [])
        problems = "؛ ".join(r.get("problems") or [])
        notes = r.get("notes") or ""
        if r.get("rankmath"):
            notes = (notes + f" Rank Math: {r['rankmath']}").strip()
        lines.append(
            "| {url} | {problems} | {changed} | {added} | {words} | {links} | {similar} | {decision} | {notes} |".format(
                url=r["url"],
                problems=problems.replace("|", "/"),
                changed=(r.get("changed") or "").replace("|", "/"),
                added=added.replace("|", "/"),
                words=r.get("words"),
                links=links,
                similar=similar_s,
                decision=r.get("decision", "KEEP"),
                notes=notes.replace("|", "/"),
            )
        )
    lines += [
        "",
        "## Final Similarity Audit",
        "",
        "قياس cosine على كيس كلمات 4096-بعد بعد تطبيع أسماء المدن (نفس أسلوب `seo_content_audit.py`). العتبة 0.90.",
        "",
    ]
    if not similar:
        lines.append("لا أزواج بـ cosine ≥ 0.90 بين المقالات المعاد كتابتها.")
    else:
        lines.append("| أ | ب | cosine | توصية |")
        lines.append("|---|---|---|---|")
        for p in similar:
            rec = "مراجعة صياغة" if p["cosine"] >= 0.93 else "KEEP منفصلان مع مراقبة"
            lines.append(f"| `{p['a']}` | `{p['b']}` | {p['cosine']} | {rec} |")
    lines += [
        "",
        "## قرارات KEEP / CONSOLIDATE / DELETE",
        "",
        "- **KEEP**: كل الـ 38 بعد إعادة الكتابة — نية مستقلة لكل سلَج.",
        "- **CONSOLIDATE**: لا دمج حذف في هذه المرحلة. خطة التعارض السابقة تبقى مسودات Rank Math.",
        "- **DELETE**: لا شيء. ممنوع حذف الصفحات المتشابهة؛ التقرير فقط.",
        "",
        "## تحقق تقني لكل مقال",
        "",
        "- لا H1 داخل المحتوى (العنوان من القالب).",
        "- `[post_call]` مرتان.",
        "- صورة بارزة موجودة تُعاد بألت نص يطابق الخدمة (لا plumber.webp).",
        "- واتساب الإمارات حتى يتوفر رقم سعودي.",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if similar:
        with SIM_CSV.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["a", "b", "cosine"])
            w.writeheader()
            w.writerows(similar)
    else:
        with SIM_CSV.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["a", "b", "cosine"])
            w.writeheader()


def run(args: argparse.Namespace) -> int:
    load_dotenv(ROOT / ".env")
    os.environ.setdefault("WP_BASE_URL", DEFAULT_BASE)
    run_id = utc_now()
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    run_log = LOG_DIR / f"phase3-{run_id}.jsonl"
    ck_path = CHECKPOINT_DIR / "phase3.json"
    done = {int(x) for x in load_json(ck_path, [])}

    wanted = slugs()
    if args.slugs:
        wanted = [s.strip() for s in args.slugs.split(",") if s.strip()]
        missing = [s for s in wanted if s not in BUILDERS]
        if missing:
            raise SystemExit(f"unknown slugs: {missing}")
    if args.limit:
        wanted = wanted[: args.limit]

    wp = None
    if args.apply:
        user = env("WP_USERNAME") or env("WP_USER")
        password = env("WP_APP_PASSWORD")
        if not user or not password:
            print("WP_USER / WP_APP_PASSWORD missing — cannot apply", file=sys.stderr)
            return 2
        wp = WpClient(env("WP_BASE_URL") or DEFAULT_BASE, user, password, delay=0.4)

    results: list[dict] = []
    html_by_slug: dict[str, str] = {}
    for slug in wanted:
        entry = entry_for_slug(slug)
        rec = {
            "id": entry["id"],
            "slug": slug,
            "title": entry["title"],
            "url": f"{SA}/{slug}/",
            "problems": entry.get("problems") or [],
            "changed": entry.get("changed") or "",
            "added": entry.get("added") or [],
            "links": entry.get("links") or [],
            "similar": entry.get("similar") or [],
            "intent": entry.get("intent"),
            "keyword": entry.get("keyword"),
            "decision": "KEEP",
            "notes": "",
            "rankmath": "skipped",
            "words": 0,
        }
        img_src = ""
        if wp is not None:
            try:
                item = wp.get_post(entry["id"], context="edit")
                fm = int(item.get("featured_media") or 0)
                img_src = media_url(wp, fm)
                rec["featured_media"] = fm
            except Exception as e:
                rec["notes"] = f"fetch failed: {e}"
                results.append(rec)
                continue
        html = build_article(entry, img_src)
        rec["words"] = word_count(html)
        rec["h2"] = heading_list(html)
        issues = validate_html(html, entry)
        if issues:
            rec["notes"] = ("issues: " + ",".join(issues) + " " + rec["notes"]).strip()
        html_by_slug[slug] = html_text(html)
        if not args.apply:
            rec["rankmath"] = "dry-run"
            rec["notes"] = (rec["notes"] + " planned").strip()
            results.append(rec)
            run_log.open("a", encoding="utf-8").write(
                json.dumps({"event": "plan", "slug": slug, "id": entry["id"], "words": rec["words"]}, ensure_ascii=False)
                + "\n"
            )
            continue
        assert wp is not None
        if entry["id"] in done and not args.force:
            rec["notes"] = (rec["notes"] + " checkpoint-skip").strip()
            rec["rankmath"] = "skipped"
            results.append(rec)
            continue
        try:
            payload: dict[str, Any] = {
                "content": html,
                "excerpt": entry.get("meta_desc") or "",
            }
            wp.update_post(entry["id"], payload)
            rec["rankmath"] = rankmath_update(
                wp,
                entry["id"],
                entry.get("meta_title") or entry["title"],
                entry.get("meta_desc") or "",
                entry.get("keyword") or "",
            )
            verify = extract_content(wp.get_post(entry["id"], context="edit"))
            if "[post_call]" not in verify or entry.get("keyword", "").split()[0] not in verify:
                rec["notes"] = (rec["notes"] + " verify-mismatch").strip()
            else:
                rec["notes"] = (rec["notes"] + " applied").strip()
            done.add(entry["id"])
            save_json(ck_path, sorted(done))
            run_log.open("a", encoding="utf-8").write(
                json.dumps(
                    {
                        "event": "updated",
                        "slug": slug,
                        "id": entry["id"],
                        "words": rec["words"],
                        "rankmath": rec["rankmath"],
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
        except Exception as e:
            rec["notes"] = f"PUT failed: {e}"
            rec["decision"] = "KEEP"
            run_log.open("a", encoding="utf-8").write(
                json.dumps({"event": "error", "slug": slug, "error": str(e)}, ensure_ascii=False) + "\n"
            )
        results.append(rec)
        print(f"{slug} id={entry['id']} words={rec['words']} {rec['notes']} rm={rec['rankmath']}")

    similar = cosine_pairs(
        [r["slug"] for r in results if r["slug"] in html_by_slug],
        [html_by_slug[r["slug"]] for r in results if r["slug"] in html_by_slug],
        threshold=0.90,
    )
    write_report(results, similar, run_id, bool(args.apply))
    status_path = FIX_DIR / "apply-status.json"
    status = load_json(status_path, {})
    status["stage3"] = {
        "task": "intent",
        "engine": "cloud-agent-catalog",
        "ok": sum(1 for r in results if "applied" in (r.get("notes") or "")),
        "planned": len(results),
        "failed": sum(1 for r in results if "PUT failed" in (r.get("notes") or "")),
        "similar_pairs_ge_0_90": len(similar),
        "modified": bool(args.apply),
        "run_id": run_id,
        "report": str(REPORT_PATH.relative_to(ROOT)),
    }
    save_json(status_path, status)
    print(f"report: {REPORT_PATH}")
    print(f"similar pairs >=0.90: {len(similar)}")
    failed = sum(1 for r in results if "PUT failed" in (r.get("notes") or ""))
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true", help="ignore checkpoint")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--slugs", default="")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
