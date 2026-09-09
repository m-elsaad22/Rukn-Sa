#!/usr/bin/env python3
"""Probe whether nested GroupsField meta survives REST PUT."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_client import post, get, delete, PHONE, WHATSAPP

payload = {
    "title": "اختبار حقول القالب — احذف",
    "status": "draft",
    "excerpt": "مسودة اختبار للحقول المخصصة",
    "content": "<p>تجربة</p>\n[post_call]\n[post_features]\n[post_steps]\n",
    "meta": {
        "phone_number": PHONE,
        "whatsapp_number": WHATSAPP,
        "yourcolor__faqs": [
            {"question": "سؤال تجريبي؟", "answer": "إجابة تجريبية."},
        ],
        "post__features__data": {
            "features__title": "مميزات تجريبية",
            "features__content": "وصف المميزات",
            "yourcolor__post_features": [
                {"title": "ميزة 1", "content": "تفاصيل", "icon": '<i class="fa-solid fa-check"></i>'},
            ],
        },
        "post__work_steps__data": {
            "work_steps__title": "خطوات تجريبية",
            "work_steps__content": "وصف الخطوات",
            "work_steps_items": [
                {"title": "خطوة 1", "content": "تفاصيل الخطوة"},
            ],
        },
        "post__call_section__data": {
            "call_section_title": "تواصل",
            "call_section_content": "نص",
            "call_section_phone": PHONE,
            "call_section_whatsapp": WHATSAPP,
        },
        "YourColor_Service": {
            "description": "وصف خدمة",
            "telephone": PHONE,
            "addressCountry": "SA",
            "addressLocality": "الرياض",
            "areaServed": "الرياض",
        },
        "YourColor_Article": {
            "headline": "عنوان",
            "description": "وصف مقال",
        },
    },
}

created, _ = post("/wp/v2/posts", payload)
pid = created["id"]
print("CREATED", pid)
got, _ = get(f"/wp/v2/posts/{pid}?context=edit")
meta = got.get("meta") or {}
print("FAQS", json.dumps(meta.get("yourcolor__faqs"), ensure_ascii=False)[:500])
print("FEATURES", json.dumps(meta.get("post__features__data"), ensure_ascii=False)[:800])
print("STEPS", json.dumps(meta.get("post__work_steps__data"), ensure_ascii=False)[:800])
print("CALL", json.dumps(meta.get("post__call_section__data"), ensure_ascii=False)[:500])
print("SERVICE", json.dumps(meta.get("YourColor_Service"), ensure_ascii=False)[:500])
print("PHONE", meta.get("phone_number"))

# Rank Math
try:
    rm, _ = post(
        "/rankmath/v1/updateMeta",
        {
            "objectType": "post",
            "objectID": pid,
            "meta": {
                "rank_math_title": "تجربة رانك ماث",
                "rank_math_description": "وصف تجريبي لرانك ماث.",
                "rank_math_focus_keyword": "تجربة",
            },
        },
    )
    print("RANKMATH", rm)
except Exception as e:
    print("RANKMATH ERR", e)

deleted, _ = delete(f"/wp/v2/posts/{pid}")
print("DELETED", deleted.get("id") if isinstance(deleted, dict) else deleted)
