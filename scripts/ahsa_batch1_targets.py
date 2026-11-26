# -*- coding: utf-8 -*-
"""RSCA-8 Ahsa batch 1 targets: water leak detection & moisture treatment."""

CITY_AR = "الأحساء"
CITY_EN = "ahsa"
PHONE_DISPLAY = "0552481093"
PHONE_E164 = "+966552481093"
PHONE_WA = "966552481093"
CATEGORY_ID = 2457  # الخدمات
CATEGORY_LEAK = 166  # كشف تسربات المياه
CATEGORY_LEAK_INSUL = 2778  # خدمات كشف التسربات والعزل

# Existing live URLs safe for internal links (published only)
INTERNAL_LINKS = {
    "services": "https://www.rukn-eltatawer.com/sa/services/",
    "cities": "https://www.rukn-eltatawer.com/sa/cities/",
    "ahsa_city": "https://www.rukn-eltatawer.com/sa/cities/ahsa/",
    "contact": "https://www.rukn-eltatawer.com/sa/contact-us/",
    "about": "https://www.rukn-eltatawer.com/sa/about/",
    "leak_primary": "https://www.rukn-eltatawer.com/sa/water-leak-detection-al-ahsa/",
    "roof_insul": "https://www.rukn-eltatawer.com/sa/roof-insulation-ahsa/",
    "home_cleaning": "https://www.rukn-eltatawer.com/sa/home-cleaning-ahsa/",
    "ac_cleaning": "https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-ahsa/",
    "pest": "https://www.rukn-eltatawer.com/sa/pest-control-ahsa/",
}

# Featured media from library (verified leak-related IDs)
MEDIA = {
    "leak_a": 10620,
    "leak_e": 10621,
    "leak_u": 10622,
    "leak_w": 10623,
    "leak_water": 10634,
    "leak_z": 10636,
    "leakage": 2471,
}

# Full batch-1 service list (including existing primary to audit)
AUDIT_SERVICES = [
    {
        "service": "كشف تسربات المياه",
        "title": "كشف تسربات المياه في الأحساء",
        "focus": "كشف تسربات المياه في الأحساء",
        "slug": "water-leak-detection-al-ahsa",
        "key": "general_leak",
    },
    {
        "service": "كشف تسربات المياه بدون تكسير",
        "title": "كشف تسربات المياه بدون تكسير في الأحساء",
        "focus": "كشف تسربات المياه بدون تكسير في الأحساء",
        "slug": "non-destructive-water-leak-detection-ahsa",
        "key": "nondestructive",
        "media": "leak_a",
        "emoji": "🔎",
    },
    {
        "service": "كشف تسربات الخزانات",
        "title": "كشف تسربات الخزانات في الأحساء",
        "focus": "كشف تسربات الخزانات في الأحساء",
        "slug": "water-tank-leak-detection-ahsa",
        "key": "tank",
        "media": "leak_water",
        "emoji": "💧",
    },
    {
        "service": "كشف تسربات المسابح",
        "title": "كشف تسربات المسابح في الأحساء",
        "focus": "كشف تسربات المسابح في الأحساء",
        "slug": "pool-leak-detection-ahsa",
        "key": "pool",
        "media": "leak_z",
        "emoji": "🏊",
    },
    {
        "service": "كشف تسربات الحمامات",
        "title": "كشف تسربات الحمامات في الأحساء",
        "focus": "كشف تسربات الحمامات في الأحساء",
        "slug": "bathroom-leak-detection-ahsa",
        "key": "bathroom",
        "media": "leak_e",
        "emoji": "🚿",
    },
    {
        "service": "كشف تسربات الأسطح",
        "title": "كشف تسربات الأسطح في الأحساء",
        "focus": "كشف تسربات الأسطح في الأحساء",
        "slug": "roof-leak-detection-ahsa",
        "key": "roof",
        "media": "leak_u",
        "emoji": "🏠",
    },
    {
        "service": "معالجة رطوبة الجدران",
        "title": "معالجة رطوبة الجدران في الأحساء",
        "focus": "معالجة رطوبة الجدران في الأحساء",
        "slug": "wall-moisture-treatment-ahsa",
        "key": "moisture",
        "media": "leakage",
        "emoji": "🧱",
    },
    {
        "service": "معالجة تسربات المياه",
        "title": "معالجة تسربات المياه في الأحساء",
        "focus": "معالجة تسربات المياه في الأحساء",
        "slug": "water-leak-treatment-ahsa",
        "key": "treatment",
        "media": "leak_w",
        "emoji": "🛠️",
    },
]

# Only services that should become new drafts
CREATE_TARGETS = [t for t in AUDIT_SERVICES if t["key"] != "general_leak"]
