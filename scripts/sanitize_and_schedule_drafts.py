#!/usr/bin/env python3
"""Sanitize SA draft posts, prioritize by search demand, publish one now and schedule the rest every 10 minutes."""

from __future__ import annotations

import hashlib
import html as html_lib
import json
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

BASE = "https://www.rukn-eltatawer.com/sa"
AUTH = HTTPBasicAuth("cursor", "PCkk ig95 Gu6c zOgC GLYG FYsk")
H = {"User-Agent": "Mozilla/5.0 RuknPublish/1.0", "Content-Type": "application/json"}
PHONE = "0568060309"
ROOT = Path(__file__).resolve().parents[1]

# Featured/media pools by topic
MEDIA = {
    "ac": [2869, 2827, 2686, 2870],
    "leak": [10623, 10636, 10630, 10619, 10618, 10614],
    "clean": [2897, 2895, 2894, 2896],
    "pest": [2895, 2897, 2894],
    "insul": [11080, 11079, 11078, 2612, 2602],
    "plumb": [2870, 2868, 2869, 2827],
    "elec": [2733, 2600, 2612],
    "build": [2827, 2733, 2600],
    "garden": [2602, 2896, 2547],
    "move": [2733, 2600],
    "default": [10623, 2897, 2827, 2600, 2612],
}

IMG_URL = {
    "ac": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2021/08/plumber-1.webp",
    "leak": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2026/08/water-leak-detection.webp",
    "clean": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2021/12/cleaning-6.webp",
    "pest": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2021/12/clean-2.webp",
    "insul": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2026/08/roof-insulation-ae.webp",
    "plumb": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2021/08/plumbing.webp",
    "elec": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2021/12/toolbox.webp",
    "build": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2021/12/plumber.webp",
    "garden": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2020/10/waterproof-fabric-3.webp",
    "move": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2020/10/equipment.webp",
    "default": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2026/08/water-leak-detection.webp",
}

CITY_PRIORITY = {
    "الرياض": 100,
    "جدة": 90,
    "مكة": 85,
    "المدينة": 80,
    "الدمام": 75,
    "الخبر": 70,
    "الطائف": 60,
    "أبها": 55,
}

# Higher = more search demand / business-critical for this site
SERVICE_PRIORITY = [
    (100, ["كشف تسربات", "كشف تسريبات", "تسريبات مواسير", "تسربات مياه"]),
    (98, ["عزل أسطح", "عزل الاسطح", "عزل الأسطح", "عزل خزانات", "عزل فوم"]),
    (95, ["تنظيف منازل", "تنظيف فلل", "تنظيف شقق", "تنظيف كنب", "تنظيف سجاد", "تعقيم"]),
    (93, ["مكافحة حشرات", "مكافحة الصراصير", "مكافحة النمل", "رش مبيدات"]),
    (92, ["صيانة مكيفات", "غسيل مكيفات", "تنظيف مكيفات", "تكييف", "فريون", "سبليت"]),
    (90, ["سباك", "سباكة", "سخانات", "مضخات مياه", "مواسير"]),
    (88, ["تسليك مجاري", "تسليك", "مجاري"]),
    (85, ["كهربائي", "كهرباء", "إنارة", "لوحات كهرباء"]),
    (80, ["نقل عفش", "نقل أثاث"]),
    (75, ["جلي بلاط", "جلي رخام"]),
    (70, ["مسابح", "مسبح"]),
    (65, ["حدائق", "عشب"]),
    (60, ["كاميرات", "أمن"]),
    (50, ["ديكور", "جبس", "باركيه"]),
]

DISTRICTS = {
    "الرياض": ["النسيم", "الملز", "العليا", "الياسمين", "الشفا", "طويق"],
    "جدة": ["الروضة", "أبحر", "الصفا", "النعيم", "الفيصلية"],
    "مكة": ["العزيزية", "الشوقية", "العوالي", "النسيم"],
    "المدينة": ["قباء", "العوالي", "الحرة الشرقية", "الملك فهد"],
    "الدمام": ["الفيصلية", "الشاطئ", "الجلوية", "أحد"],
    "الخبر": ["العقربية", "الحزام", "اليرموك", "الثقبة"],
    "الطائف": ["الشفا", "الحوية", "الروضة", "السلامة"],
    "أبها": ["المنسك", "الموظفين", "الوردتين", "الخالدية"],
}


def wc(html: str) -> int:
    t = re.sub(r"\[[^\]]+\]", " ", html or "")
    t = re.sub(r"<[^>]+>", " ", t)
    t = html_lib.unescape(t)
    return len(re.findall(r"[\w\u0600-\u06FF]+", t))


def topic_of(title: str) -> str:
    t = title
    if any(k in t for k in ["مكيف", "تكييف", "تبريد", "فريون", "دكت", "سبليت"]):
        return "ac"
    if any(k in t for k in ["تسرب", "تسريب"]):
        return "leak"
    if any(k in t for k in ["تنظيف", "تعقيم", "جلي"]):
        return "clean"
    if any(k in t for k in ["مكافحة", "حشرات", "صراصير", "نمل", "بق"]):
        return "pest"
    if any(k in t for k in ["عزل", "فوم", "عازل"]):
        return "insul"
    if any(k in t for k in ["سباك", "سباكة", "سخان", "مضخ", "مواسير", "صحية"]):
        return "plumb"
    if any(k in t for k in ["كهرب", "إنارة", "لوحة"]):
        return "elec"
    if any(k in t for k in ["حدائق", "عشب", "ري"]):
        return "garden"
    if any(k in t for k in ["نقل", "عفش", "أثاث"]):
        return "move"
    if any(k in t for k in ["مسبح", "مسابح"]):
        return "garden"
    return "default"


def city_of(title: str) -> str | None:
    for c in CITY_PRIORITY:
        if c in title:
            return c
    return None


def score_draft(title: str) -> int:
    city = city_of(title)
    s = CITY_PRIORITY.get(city or "", 20)
    for pts, keys in SERVICE_PRIORITY:
        if any(k in title for k in keys):
            s += pts
            break
    else:
        s += 30
    # slight boost for exact "شركة ... بالرياض" core pattern
    if title.startswith("شركة"):
        s += 5
    return s


def sanitize_content(title: str, raw: str) -> str:
    city = city_of(title) or "السعودية"
    topic = topic_of(title)
    body = raw or ""
    good_long = wc(body) >= 1100
    # country / phone cleanup always
    repls = [
        ("خريطة الإمارات", "خريطة السعودية"),
        ("الإمارات العربية المتحدة", "المملكة العربية السعودية"),
        ("في الإمارات", "في السعودية"),
        ("بالإمارات", "بالسعودية"),
        ("بالامارات", "بالسعودية"),
        ("درهم", "ريال"),
        ("+971", "+966"),
        ("01556644443", PHONE),
        ("966XXXXXXXXX", "966568060309"),
    ]
    for a, b in repls:
        body = body.replace(a, b)

    if good_long:
        if "[post_call]" not in body:
            body = "[post_call]\n" + body
            if body.count("[post_call]") < 2:
                body += "\n[post_call]\n"
        elif body.count("[post_call]") > 4:
            parts = body.split("[post_call]")
            body = parts[0] + "[post_call]" + "".join(parts[1:-1]) + "[post_call]" + parts[-1]
        body = re.sub(r"\n{3,}", "\n\n", body).strip()
        return body

    # Continue with template sanitization for short drafts
    city = city_of(title) or "السعودية"
    # soft geo replacements for templates only
    for a, b in [
        ("دبي", city if city != "السعودية" else "الرياض"),
        ("أبوظبي", city if city != "السعودية" else "الرياض"),
        ("ابوظبي", city if city != "السعودية" else "الرياض"),
    ]:
        body = body.replace(a, b)

    return _sanitize_template(title, body, city, topic)


def _sanitize_template(title: str, body: str, city: str, topic: str) -> str:
    if "<!DOCTYPE" in body or "<html" in body.lower():
        m = re.search(r"<body[^>]*>(.*)</body>", body, flags=re.S | re.I)
        body = m.group(1) if m else body

    img_url = IMG_URL.get(topic, IMG_URL["default"])
    body = re.sub(
        r'<img[^>]+src=["\'](?!https?://)[^"\']+\.webp["\'][^>]*>',
        f'<p style="margin:28px 0;"><img src="{img_url}" alt="{html_lib.escape(title)}" '
        f'loading="lazy" decoding="async" style="width:100%;height:auto;border-radius:8px;" /></p>',
        body,
        count=1,
        flags=re.I,
    )
    body = re.sub(
        r'<img[^>]+src=["\'](?!https?://)[^"\']+\.webp["\'][^>]*>',
        "",
        body,
        flags=re.I,
    )

    # Demote content H1 (theme already prints title)
    body = re.sub(
        r"<h1\b[^>]*>(.*?)</h1>",
        r'<p style="font-size:1.25em;font-weight:700;color:#005CB9;line-height:1.5;">\1</p>',
        body,
        count=1,
        flags=re.S | re.I,
    )

    # Ensure one [post_call] near top after lead
    body = re.sub(r"\[post_call\]", "", body)
    # Insert after first paragraph block / author box
    insert_at = None
    for pat in [r"</div>\s*", r"</p>\s*"]:
        m = re.search(pat, body)
        if m:
            insert_at = m.end()
            break
    if insert_at:
        body = body[:insert_at] + "\n[post_call]\n" + body[insert_at:]
    else:
        body = "[post_call]\n" + body

    # Local uniqueness block if missing districts mention
    districts = DISTRICTS.get(city, ["أحياء المدينة"])
    dcsv = "، ".join(districts[:4])
    marker = f"نطاق الخدمة داخل {city}"
    if marker not in body:
        extra = f"""
<h2>{marker}</h2>
<p>فريق ركن التطور يغطي {city} وما حولها، بما في ذلك أحياء مثل {dcsv}. عند الطلب اذكر الحي ونوع العقار ووصف المشكلة لنصل بالمعدات المناسبة.</p>
<p>رقم التواصل الموحّد داخل السعودية: {PHONE} (اتصال وواتساب).</p>
"""
        # append before last section if possible
        if re.search(r"<h2[^>]*>\s*خاتمة", body, flags=re.I):
            body = re.sub(r"<h2[^>]*>\s*خاتمة", extra + r"<h2>خاتمة", body, count=1, flags=re.I)
        else:
            body += extra

    # Final call once at end if only one near top
    if body.count("[post_call]") < 2:
        body += "\n[post_call]\n"

    # Collapse excessive blank lines
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    return body


def make_excerpt(title: str) -> str:
    city = city_of(title) or "السعودية"
    return (
        f"{title} من شركة ركن التطور في {city}: خدمة ميدانية عملية، "
        f"توضيح النطاق قبل التنفيذ، وتواصل مباشر على {PHONE}."
    )


def fetch_drafts() -> list[dict]:
    items: list[dict] = []
    page = 1
    while True:
        r = requests.get(
            f"{BASE}/wp-json/wp/v2/posts",
            auth=AUTH,
            headers=H,
            params={
                "per_page": 100,
                "page": page,
                "status": "draft",
                "context": "edit",
                "_fields": "id,title,content,featured_media,slug,status,date",
            },
            timeout=120,
        )
        if r.status_code != 200:
            break
        batch = r.json()
        if not batch:
            break
        items.extend(batch)
        page += 1
        if page > 30:
            break
    return items


def update_and_set_status(pid: int, payload: dict) -> dict:
    r = requests.post(
        f"{BASE}/wp-json/wp/v2/posts/{pid}",
        auth=AUTH,
        headers=H,
        json=payload,
        timeout=120,
    )
    r.raise_for_status()
    return r.json()


def main():
    import sys
    print("starting fetch...", flush=True)
    drafts = fetch_drafts()
    print(f"drafts={len(drafts)}", flush=True)
    ranked = []
    for p in drafts:
        title = p["title"]["raw"] if isinstance(p["title"], dict) else str(p["title"])
        ranked.append((score_draft(title), p["id"], title, p))
    ranked.sort(key=lambda x: (-x[0], x[2], x[1]))

    report = {
        "total_drafts": len(ranked),
        "published_now": None,
        "scheduled": [],
        "errors": [],
        "top20": [{"id": i, "score": s, "title": t} for s, i, t, _ in ranked[:20]],
    }

    # Schedule origin: now + 10 minutes for first future, then +10 each
    # First item publishes immediately
    now = datetime.now(timezone(timedelta(hours=3)))  # Asia/Riyadh approx

    for idx, (sc, pid, title, p) in enumerate(ranked):
        raw = (p.get("content") or {}).get("raw") or ""
        try:
            content = sanitize_content(title, raw)
            topic = topic_of(title)
            feat = MEDIA.get(topic, MEDIA["default"])[pid % len(MEDIA.get(topic, MEDIA["default"]))]
            payload = {
                "content": content,
                "excerpt": make_excerpt(title),
                "featured_media": feat if not p.get("featured_media") else p["featured_media"],
            }
            if idx == 0:
                # If anything already published in this run context, still schedule
                payload["status"] = "publish"
                payload["date"] = now.strftime("%Y-%m-%dT%H:%M:%S")
                when = "now"
            else:
                when_dt = now + timedelta(minutes=10 * idx)
                payload["status"] = "future"
                payload["date"] = when_dt.strftime("%Y-%m-%dT%H:%M:%S")
                when = payload["date"]

            update_and_set_status(pid, payload)
            item = {
                "id": pid,
                "score": sc,
                "title": title,
                "when": when,
                "words": wc(content),
                "topic": topic,
                "city": city_of(title),
            }
            if idx == 0:
                report["published_now"] = item
                print(f"PUBLISH now #{pid} score={sc} {title} wc={item['words']}", flush=True)
            else:
                report["scheduled"].append(item)
                if idx <= 15 or idx % 50 == 0:
                    print(f"SCHEDULE #{pid} @ {when} score={sc} {title[:50]}", flush=True)
            time.sleep(0.05)
        except Exception as e:
            report["errors"].append({"id": pid, "title": title, "error": str(e)[:200]})
            print("ERR", pid, e, flush=True)
            time.sleep(0.2)

    out = ROOT / "data/draft-publish-schedule.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    # keep scheduled list but truncate titles file size: store summary + first 50 + counts
    slim = {
        "total_drafts": report["total_drafts"],
        "published_now": report["published_now"],
        "scheduled_count": len(report["scheduled"]),
        "errors": report["errors"],
        "top20": report["top20"],
        "scheduled_first50": report["scheduled"][:50],
        "scheduled_last10": report["scheduled"][-10:],
        "interval_minutes": 10,
        "city_priority": CITY_PRIORITY,
    }
    out.write_text(json.dumps(slim, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "published": 1 if report["published_now"] else 0,
                "scheduled": len(report["scheduled"]),
                "errors": len(report["errors"]),
                "first": report["published_now"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
