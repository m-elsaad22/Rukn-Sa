"""Render Rank-Math-ready HTML for Phase 3 rewrites. No H1 (theme prints title)."""

from __future__ import annotations

WA = "971586634710"


def img_block(src: str, alt: str) -> str:
    if not src:
        return ""
    return (
        f'<p style="margin:28px 0;"><img src="{src}" alt="{alt}" loading="lazy" '
        f'decoding="async" style="width:100%;height:auto;border-radius:8px;" /></p>\n'
    )


def render(entry: dict, img_src: str, img_alt: str, wa: str = WA) -> str:
    parts: list[str] = []
    parts.append(
        f'<p style="font-size:1.22em;font-weight:700;color:#005CB9;line-height:1.55;">{entry["lead"]}</p>\n'
    )
    parts.append(entry["intro"])
    parts.append("\n[post_call]\n")
    parts.append(img_block(img_src, img_alt))
    for heading, body in entry["sections"]:
        parts.append(f"<h2>{heading}</h2>\n{body}\n")
    if entry.get("faqs"):
        parts.append(f"<h2>{entry.get('faq_heading', 'أسئلة قبل تأكيد الطلب')}</h2>\n")
        for q, a in entry["faqs"]:
            parts.append(f"<h3>{q}</h3>\n<p>{a}</p>\n")
    parts.append("[post_call]\n")
    cta = entry.get("cta") or "تواصل عبر واتساب لتوضيح حالة المركبة أو الشحنة"
    parts.append(
        f'<p><a href="https://wa.me/{wa}"><i class="fa-solid fa-comments"></i> {cta}</a></p>\n'
    )
    return "".join(parts)
