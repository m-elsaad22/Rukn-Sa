from __future__ import annotations

SA = "https://www.rukn-eltatawer.com/sa"

# Map newer FA names to icons commonly present on FA5/FA6 free solid.
FA_ALIAS = {
    "cloud-dust": "wind",
    "vacuum": "broom",
    "temperature-half": "sun",
    "boxes-stacked": "boxes",
    "road-barrier": "road",
    "map-pin": "map-marker-alt",
    "elevator": "building",
    "vector-square": "border-all",
    "tape": "box",
    "route": "road",
}


def a(slug: str, text: str) -> str:
    return f'<a href="{SA}/{slug}/">{text}</a>'


def p(*chunks: str) -> str:
    return "".join(f"<p>{c}</p>\n" for c in chunks)


def ul(*items: str) -> str:
    return "<ul>\n" + "".join(f"<li>{i}</li>\n" for i in items) + "</ul>\n"


def icon(name: str, text: str) -> str:
    name = FA_ALIAS.get(name, name)
    return f'<p><i class="fa-solid fa-{name}"></i> {text}</p>\n'


def word_count(html: str) -> int:
    import re

    text = re.sub(r"<[^>]+>", " ", html or "")
    text = re.sub(r"\[post_call\]", " ", text)
    return len(re.findall(r"[A-Za-z\u0600-\u06FF]{2,}", text))
