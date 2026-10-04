#!/usr/bin/env python3
"""Force UAE WhatsApp +971586634710, hide call, strip all other phone numbers site-wide."""

from __future__ import annotations

import base64
import json
import re
import time
import urllib.request
from pathlib import Path

BASE = "https://www.rukn-eltatawer.com/sa/wp-json"
AUTH = base64.b64encode(b"cursor:PCkk ig95 Gu6c zOgC GLYG FYsk").decode()
H = {
    "Authorization": f"Basic {AUTH}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 RuknUAEWA/2026-10-04",
}
WA = "971586634710"
WA_PLUS = "+971586634710"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "uae-wa-hide-call-results.json"

SNIP15 = r'''/**
 * Rukn SA interim NAP: UAE WhatsApp only, hide call, clear other phones
 * until a Saudi number is available. Does not rewrite SEO title templates.
 */
if ( ! defined( 'ABSPATH' ) ) {
	return;
}

function rukn_sa_wa_digits() {
	return '971586634710';
}

function rukn_sa_trust_apply() {
	$wa      = rukn_sa_wa_digits();
	$wa_plus = '+' . $wa;
	$report  = array();

	$keys = array(
		'phonenumber'               => '',
		'contact_number'            => '',
		'phone'                     => '',
		'info_contact'              => '',
		'whatsapp_number'           => $wa_plus,
		'whatsapp'                  => $wa_plus,
		'kayan_country_sa_phone'    => '',
		'kayan_country_sa_whatsapp' => $wa,
		'kayan_show_call_buttons'   => '0',
		'hide__floating__call'      => '1',
		'kayan_homepage_brand_first'  => 'ركن',
		'kayan_homepage_brand_second' => 'التطور',
		'sitename'                  => 'شركة ركن التطور - السعودية',
	);

	foreach ( $keys as $k => $v ) {
		$old = function_exists( 'yc_get_option' ) ? yc_get_option( $k ) : get_option( $k );
		if ( function_exists( 'yc_update_option' ) ) {
			yc_update_option( $k, $v );
		}
		update_option( $k, $v, false );
		$report['options'][ $k ] = array(
			'old' => is_string( $old ) ? mb_substr( $old, 0, 180 ) : $old,
			'new' => $v,
		);
	}

	$copy = 'حقوق النشر {%YEAR%} © جميع الحقوق محفوظة لصالح "شركة ركن التطور - السعودية"';
	foreach ( array( 'copyrights', 'Copyrights' ) as $ck ) {
		if ( function_exists( 'yc_update_option' ) ) {
			yc_update_option( $ck, $copy );
		}
		update_option( $ck, $copy, false );
	}

	$price = get_option( 'price__option_data', array() );
	if ( ! is_array( $price ) ) {
		$price = array();
	}
	$price['price__mode'] = 'watshapp';
	$price['watshapp']    = array( 'watshapp' => $wa_plus );
	update_option( 'price__option_data', $price, false );

	$biz = get_option( 'YourColor_Schema_business', array() );
	if ( ! is_array( $biz ) ) {
		$biz = array();
	}
	$biz['Business_Name']  = $biz['Business_Name'] ?? 'ركن التطور';
	$biz['Street_Address'] = $biz['Street_Address'] ?: 'حي النسيم';
	$biz['Country']        = 'SA';
	$biz['City']           = 'Riyadh';
	$biz['State']          = 'Riyadh';
	$biz['Postal_Code']    = $biz['Postal_Code'] ?: '11461';
	$biz['telephone']      = '';
	$biz['Price_Range']    = 'SAR';
	update_option( 'YourColor_Schema_business', $biz, false );

	// Call Now Button plugin: disable / clear number
	$cnb = get_option( 'cnb', array() );
	if ( is_array( $cnb ) ) {
		$cnb['number'] = '';
		$cnb['active'] = '0';
		update_option( 'cnb', $cnb, false );
		$report['cnb'] = $cnb;
	}

	$btn = get_option( 'price__button__text', '' );
	$btn_new = 'احجز خطتك الآن مع ركن التطور! تواصل معنا على واتساب مباشرة. رابط واتساب: https://wa.me/' . $wa;
	update_option( 'price__button__text', $btn_new, false );
	$report['price__button__text'] = array( 'old' => mb_substr( (string) $btn, 0, 120 ), 'new' => $btn_new );

	// Clear phone numbers from Rank Math Local SEO (keep titles/templates untouched)
	$titles = get_option( 'rank-math-options-titles', array() );
	if ( is_array( $titles ) ) {
		$titles['phone_numbers'] = array();
		update_option( 'rank-math-options-titles', $titles, false );
		$report['rank_math_phone_numbers'] = 'cleared';
	}

	if ( function_exists( 'do_action' ) ) {
		do_action( 'litespeed_purge_all' );
		$report['cache'] = 'purged';
	}

	return $report;
}

add_action(
	'init',
	function () {
		// Keep options enforced on each request boot (cheap writes only when drifted).
		$wa = rukn_sa_wa_digits();
		$want = array(
			'whatsapp_number'         => '+' . $wa,
			'whatsapp'                => '+' . $wa,
			'phonenumber'             => '',
			'contact_number'          => '',
			'phone'                   => '',
			'info_contact'            => '',
			'kayan_country_sa_phone'  => '',
			'kayan_country_sa_whatsapp' => $wa,
			'kayan_show_call_buttons' => '0',
			'hide__floating__call'    => '1',
		);
		foreach ( $want as $k => $v ) {
			$cur = function_exists( 'yc_get_option' ) ? yc_get_option( $k ) : get_option( $k );
			if ( (string) $cur !== (string) $v ) {
				if ( function_exists( 'yc_update_option' ) ) {
					yc_update_option( $k, $v );
				}
				update_option( $k, $v, false );
			}
		}
	},
	5
);

add_action(
	'rest_api_init',
	function () {
		$can = function () {
			return current_user_can( 'manage_options' );
		};
		register_rest_route(
			'rukn/v1',
			'/apply-trust-fix',
			array(
				'methods'             => 'POST',
				'permission_callback' => $can,
				'callback'            => function () {
					return rest_ensure_response( array( 'ok' => true, 'report' => rukn_sa_trust_apply() ) );
				},
			)
		);
		register_rest_route(
			'rukn/v1',
			'/dump-keys',
			array(
				'methods'             => 'GET',
				'permission_callback' => $can,
				'callback'            => function () {
					$keys = array(
						'phonenumber',
						'whatsapp_number',
						'contact_number',
						'copyrights',
						'kayan_country_sa_phone',
						'kayan_country_sa_whatsapp',
						'kayan_show_call_buttons',
						'hide__floating__call',
						'sitename',
					);
					$out = array();
					foreach ( $keys as $k ) {
						$out[ $k ] = function_exists( 'yc_get_option' ) ? yc_get_option( $k ) : get_option( $k );
					}
					return rest_ensure_response( $out );
				},
			)
		);
	}
);
'''


def get(path: str):
    last = None
    for i in range(4):
        try:
            req = urllib.request.Request(BASE + path, headers={k: v for k, v in H.items() if k != "Content-Type"})
            with urllib.request.urlopen(req, timeout=90) as resp:
                return dict(resp.headers), json.loads(resp.read().decode())
        except Exception as e:
            last = e
            time.sleep(1.2 * (i + 1))
    raise last


def put(path: str, payload: dict):
    data = json.dumps(payload, ensure_ascii=False).encode()
    last = None
    for i in range(4):
        try:
            req = urllib.request.Request(BASE + path, data=data, headers=H, method="PUT")
            with urllib.request.urlopen(req, timeout=90) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            last = e
            time.sleep(1.2 * (i + 1))
    raise last


def post(path: str, payload: dict | None = None):
    data = json.dumps(payload or {}, ensure_ascii=False).encode()
    last = None
    for i in range(4):
        try:
            req = urllib.request.Request(BASE + path, data=data, headers=H, method="POST")
            with urllib.request.urlopen(req, timeout=90) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            last = e
            time.sleep(1.2 * (i + 1))
    raise last


def patch_snippet_12(code: str) -> str:
    code = code.replace(
        " * Rukn SA frontend repair: force SA phone/WhatsApp, show call, strip leftover UAE copy.",
        " * Rukn SA frontend repair: UAE WhatsApp only, hide call, strip all other phones.",
    )

    # Stop converting UAE numbers to SA
    code = code.replace(
        "\t$html = preg_replace( '/\\+?9715\\d{8}/u', '966568060309', $html );\n",
        "\t// keep UAE WhatsApp; stripping of other phones happens in rukn_sa_rewrite_html\n",
    )

    old_rewrite = """function rukn_sa_rewrite_html( $html ) {
	if ( ! is_string( $html ) || $html === '' ) {
		return $html;
	}
	$wa = '966568060309';

	$html = preg_replace( '#href="\\[https://wa\\.me/[^\\]]+\\]\\([^"]+\\)"#i', 'href="https://wa.me/' . $wa . '"', $html );
	$html = preg_replace( '#https?://wa\\.me/\\+?(?:966000000000|966568060309|9715\\d{8}|0?568060309|0568060309)#i', 'https://wa.me/' . $wa, $html );
	$html = preg_replace( '#href="tel:(?:\\+?966)?0?1556644443[^"]*"#i', 'href="tel:0568060309"', $html );
	$html = preg_replace( '#href="tel:\\+?971[^"]*"#i', 'href="tel:0568060309"', $html );
	$html = str_replace( array( 'tel:+966000000000', 'tel:966000000000' ), 'tel:0568060309', $html );

	$html = preg_replace(
		'/window\\.RuknCS=\\{[^}]*\\}/',
		'window.RuknCS={"call_show":true,"wa_show":true,"call_number":"0568060309","wa_number":"' . $wa . '","wa_message":"مرحباً! شركة ركن التطور - السعودية"}',
		$html
	);

	$html = strtr(
		$html,
		array(
			'+201556644443' => '+966568060309',
			'201556644443'  => '966568060309',
			'01556644443'   => '0568060309',
			'+966000000000' => '+966568060309',
			'966000000000'  => '966568060309',
		)
	);

	$html = preg_replace( '/"telephone"\\s*:\\s*"\\s*"/', '"telephone":"0568060309"', $html );"""

    new_rewrite = """function rukn_sa_strip_other_phones( $html ) {
	if ( ! is_string( $html ) || $html === '' ) {
		return $html;
	}
	$wa = '971586634710';
	// Protect WhatsApp URLs/numbers first.
	$html = preg_replace_callback(
		'#https?://wa\\.me/\\+?971586634710#i',
		function () {
			return 'https://wa.me/__RUKN_WA__';
		},
		$html
	);
	$html = str_replace( array( '+971586634710', '971586634710' ), array( '__RUKN_WA_PLUS__', '__RUKN_WA__' ), $html );

	// Remove tel: links entirely (call hidden until Saudi number exists).
	$html = preg_replace( '#href="tel:[^"]*"#i', 'href="#"', $html );
	$html = preg_replace( '#https?://wa\\.me/\\+?[^"\\s<]+#i', 'https://wa.me/' . $wa, $html );

	// Strip known / generic Gulf & local phone patterns from visible text & attrs.
	$patterns = array(
		'/\\+?966\\s*5\\d{8}/u',
		'/\\b05\\d{8}\\b/u',
		'/\\b01\\d{8}\\b/u',
		'/\\+?9715\\d{8}/u',
		'/\\+?201\\d{9}/u',
		'/\\b01556644443\\b/u',
		'/\\b966000000000\\b/u',
		'/\\+966000000000/u',
	);
	foreach ( $patterns as $pat ) {
		$html = preg_replace( $pat, '', $html );
	}
	$html = preg_replace( '/"telephone"\\s*:\\s*"[^"]*"/', '"telephone":""', $html );
	$html = preg_replace( '/\\s{2,}/u', ' ', $html );

	$html = str_replace(
		array( 'https://wa.me/__RUKN_WA__', '__RUKN_WA_PLUS__', '__RUKN_WA__' ),
		array( 'https://wa.me/' . $wa, '+' . $wa, $wa ),
		$html
	);
	return $html;
}

function rukn_sa_rewrite_html( $html ) {
	if ( ! is_string( $html ) || $html === '' ) {
		return $html;
	}
	$wa = '971586634710';

	$html = preg_replace( '#href="\\[https://wa\\.me/[^\\]]+\\]\\([^"]+\\)"#i', 'href="https://wa.me/' . $wa . '"', $html );
	$html = preg_replace( '#https?://wa\\.me/\\+?[^"\\s<]+#i', 'https://wa.me/' . $wa, $html );

	$html = preg_replace(
		'/window\\.RuknCS=\\{[^}]*\\}/',
		'window.RuknCS={"call_show":false,"wa_show":true,"call_number":"","wa_number":"' . $wa . '","wa_message":"مرحباً! شركة ركن التطور - السعودية"}',
		$html
	);

	$html = rukn_sa_strip_other_phones( $html );"""

    if old_rewrite not in code:
        # Fallback: replace by markers
        code = re.sub(
            r"function rukn_sa_rewrite_html\( \$html \) \{.*?\$html = preg_replace\( '/\"telephone\"\\s\*:\\s\*\"\\s\*\"/', '\"telephone\":\"0568060309\"', \$html \);",
            new_rewrite,
            code,
            count=1,
            flags=re.S,
        )
    else:
        code = code.replace(old_rewrite, new_rewrite)

    # CSS: hide call buttons
    old_css = """	$css = '<style id="rukn-sa-hide-call">
.lang-item,.pll-parent-menu-item,ul.sub-menu .lang-item{display:none!important}
input,textarea,select{text-transform:none!important}
[data-loader-src*="الفيديو"],.video-box:has([data-loader-src*="الفيديو"]){display:none!important}
</style>';"""
    new_css = """	$css = '<style id="rukn-sa-hide-call">
.lang-item,.pll-parent-menu-item,ul.sub-menu .lang-item{display:none!important}
input,textarea,select{text-transform:none!important}
[data-loader-src*="الفيديو"],.video-box:has([data-loader-src*="الفيديو"]){display:none!important}
a[href^="tel:"],.call-btn,.btn-call,.floating-call,.cnb-button,.cnb-full,.phone-btn,[class*="call-now"],[class*="floating__call"],[id*="call-button"]{display:none!important}
</style>';"""
    code = code.replace(old_css, new_css)

    # JSON-LD: remove telephone
    code = code.replace(
        "\t\t\t\t$data[ $key ]['telephone'] = '0568060309';\n",
        "\t\t\t\tunset( $data[ $key ]['telephone'] );\n",
    )

    # DNI REST
    code = code.replace(
        """		if ( is_array( $data ) ) {
			$data['phone']     = '0568060309';
			$data['wa_number'] = '966568060309';
			$result->set_data( $data );
		}""",
        """		if ( is_array( $data ) ) {
			$data['phone']     = '';
			$data['wa_number'] = '971586634710';
			$data['call_show'] = false;
			$data['wa_show']   = true;
			$result->set_data( $data );
		}""",
    )

    # Early head style hide call
    code = code.replace(
        "\t\techo '<style id=\"rukn-sa-hide-call-early\">input,textarea,select{text-transform:none!important}</style>';\n",
        "\t\techo '<style id=\"rukn-sa-hide-call-early\">input,textarea,select{text-transform:none!important}a[href^=\"tel:\"],.call-btn,.btn-call,.floating-call,.cnb-button,.cnb-full,.phone-btn,[class*=\"call-now\"],[class*=\"floating__call\"]{display:none!important}</style>';\n",
    )

    return code


def patch_snippet_7(code: str) -> str:
    # Update REST fix endpoint phones so it doesn't reintroduce SA numbers
    code = code.replace("$phone_local = '0568060309';", "$phone_local = '';")
    code = code.replace("$phone_intl  = '+966568060309';", "$phone_intl  = '+971586634710';")
    code = code.replace("$phone_wa    = '966568060309';", "$phone_wa    = '971586634710';")
    code = code.replace(
        "'phone_numbers' => array(\n\t\t\t\tarray( 'type' => 'customer support', 'number' => $phone_local ),\n\t\t\t),",
        "'phone_numbers' => array(),",
    )
    # Remove phone from homepage descriptions if present
    code = re.sub(r"اتصل الآن: 0568060309\\.", "تواصل عبر واتساب.", code)
    code = re.sub(r"تواصل معنا الآن على 0568060309\\.", "تواصل معنا عبر واتساب.", code)
    code = code.replace("$biz['telephone'] = $phone_local;", "$biz['telephone'] = '';")
    code = code.replace("$cnb['number'] = $phone_intl;", "$cnb['number'] = '';\n\t\t\t\t$cnb['active'] = '0';")
    return code


def patch_snippet_16(code: str) -> str:
    # Strip phones from rendered titles/descriptions without editing stored SEO title meta
    inject = """
add_filter(
	'rank_math/frontend/title',
	function ( $title ) {
		if ( ! is_string( $title ) ) {
			return $title;
		}
		$title = preg_replace( '/\\+?966\\s*5\\d{8}/u', '', $title );
		$title = preg_replace( '/\\b05\\d{8}\\b/u', '', $title );
		$title = preg_replace( '/\\b01\\d{8}\\b/u', '', $title );
		$title = preg_replace( '/📞\\s*/u', '', $title );
		$title = preg_replace( '/📢\\s*الإعلان للإيجار/u', '', $title );
		return trim( preg_replace( '/\\s{2,}/u', ' ', $title ) );
	},
	100
);

add_filter(
	'document_title_parts',
	function ( $parts ) {
		foreach ( $parts as $k => $v ) {
			if ( ! is_string( $v ) ) {
				continue;
			}
			$v = preg_replace( '/\\+?966\\s*5\\d{8}/u', '', $v );
			$v = preg_replace( '/\\b05\\d{8}\\b/u', '', $v );
			$v = preg_replace( '/\\b01\\d{8}\\b/u', '', $v );
			$v = preg_replace( '/📞\\s*/u', '', $v );
			$v = preg_replace( '/📢\\s*الإعلان للإيجار/u', '', $v );
			$parts[ $k ] = trim( preg_replace( '/\\s{2,}/u', ' ', $v ) );
		}
		return $parts;
	},
	100
);
"""
    if "📢\\s*الإعلان للإيجار" not in code and "الإعلان للإيجار" not in code:
        code = code.rstrip() + "\n" + inject + "\n"
    return code


PHONE_CONTENT_RE = re.compile(
    r"(?:\+?966\s*5\d{8}|\b05\d{8}\b|\b01\d{8}\b|\+?9715\d{8}(?!.*wa))"
)


def strip_phones_from_content(raw: str) -> str:
    if not raw:
        return raw
    # Protect UAE WA first
    raw2 = raw.replace("+971586634710", "__RUKN_WA_PLUS__").replace("971586634710", "__RUKN_WA__")
    raw2 = re.sub(r"https?://wa\.me/\+?971586634710", "https://wa.me/__RUKN_WA__", raw2, flags=re.I)
    # Remove other phones
    for pat in [
        r"\+?966\s*5\d{8}",
        r"\b05\d{8}\b",
        r"\b01\d{8}\b",
        r"\+?9715\d{8}",
        r"\+?201\d{9}",
        r"\b01556644443\b",
        r"tel:\+?[\d]+",
    ]:
        raw2 = re.sub(pat, "", raw2)
    # Normalize wa links to UAE
    raw2 = re.sub(r"https?://wa\.me/\+?[\d]+", "https://wa.me/971586634710", raw2, flags=re.I)
    raw2 = raw2.replace("__RUKN_WA_PLUS__", "+971586634710").replace("__RUKN_WA__", "971586634710")
    raw2 = re.sub(r"https://wa\.me/971586634710", "https://wa.me/971586634710", raw2)
    return raw2


def scrub_content(results: dict):
    """Strip phone numbers from published pages/posts content (not titles)."""
    fixed = []
    for ctype in ("pages", "posts"):
        page = 1
        while True:
            hdr, items = get(
                f"/wp/v2/{ctype}?per_page=50&page={page}&status=publish&context=edit&_fields=id,slug,content"
            )
            if not items:
                break
            for p in items:
                raw = (p.get("content") or {}).get("raw") or ""
                new = strip_phones_from_content(raw)
                # also ensure wa.me uses UAE
                new2 = re.sub(r"https?://wa\.me/\+?[\d]+", "https://wa.me/971586634710", new, flags=re.I)
                if new2 != raw:
                    put(f"/wp/v2/{ctype}/{p['id']}", {"content": new2})
                    fixed.append({"type": ctype, "id": p["id"], "slug": p.get("slug")})
                    if len(fixed) % 20 == 0:
                        print("content scrubbed", len(fixed), flush=True)
                    time.sleep(0.12)
            print(ctype, "page", page, "fixed", len(fixed), flush=True)
            if page >= int(hdr.get("X-WP-TotalPages", page)):
                break
            page += 1
    results["content_scrubbed"] = len(fixed)
    results["content_samples"] = fixed[:30]


def verify(results: dict):
    samples = {}
    for url in [
        "https://www.rukn-eltatawer.com/sa/",
        "https://www.rukn-eltatawer.com/sa/cities/riyadh/",
        "https://www.rukn-eltatawer.com/sa/en-home-cleaning-riyadh/",
        "https://www.rukn-eltatawer.com/sa/water-leak-detection-riyadh/",
    ]:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            html = resp.read().decode("utf-8", "ignore")
        wa = sorted(set(re.findall(r"wa\.me/(\d+)", html)))
        tel = sorted(set(re.findall(r"tel:([+\d]+)", html)))
        has_056 = "0568060309" in html
        has_966 = "966568060309" in html
        has_011 = "01151481000" in html
        has_971 = "971586634710" in html
        title_m = re.search(r"<title>([^<]+)</title>", html, re.I)
        samples[url] = {
            "wa": wa,
            "tel": tel,
            "has_056": has_056,
            "has_966_sa": has_966,
            "has_011": has_011,
            "has_uae_wa": has_971,
            "title": (title_m.group(1)[:120] if title_m else None),
        }
        print("VERIFY", url, samples[url], flush=True)
    results["verify"] = samples
    keys = get("/rukn/v1/dump-keys")[1]
    results["dump_keys"] = keys
    print("KEYS", keys, flush=True)


def main():
    results = {"wa": WA_PLUS, "hide_call": True}

    print("=== update snippet 15 ===", flush=True)
    put("/code-snippets/v1/snippets/15", {"code": SNIP15, "active": True})

    print("=== update snippet 12 ===", flush=True)
    _, s12 = get("/code-snippets/v1/snippets/12")
    new12 = patch_snippet_12(s12.get("code") or "")
    # sanity
    assert "971586634710" in new12
    assert "call_show\":false" in new12 or "call_show\":false" in new12.replace("\\", "")
    put("/code-snippets/v1/snippets/12", {"code": new12, "active": True})

    print("=== update snippet 7 ===", flush=True)
    _, s7 = get("/code-snippets/v1/snippets/7")
    new7 = patch_snippet_7(s7.get("code") or "")
    put("/code-snippets/v1/snippets/7", {"code": new7, "active": True})

    print("=== update snippet 16 title phone strip ===", flush=True)
    _, s16 = get("/code-snippets/v1/snippets/16")
    new16 = patch_snippet_16(s16.get("code") or "")
    put("/code-snippets/v1/snippets/16", {"code": new16, "active": True})

    print("=== apply trust fix ===", flush=True)
    try:
        report = post("/rukn/v1/apply-trust-fix", {})
        results["apply_trust"] = report
        print("apply ok", flush=True)
    except Exception as e:
        results["apply_trust_error"] = str(e)
        print("apply err", e, flush=True)

    print("=== scrub content phones ===", flush=True)
    scrub_content(results)

    print("=== verify ===", flush=True)
    time.sleep(2)
    verify(results)

    # save snippet snapshots
    snap = ROOT / "data" / "snippets"
    snap.mkdir(parents=True, exist_ok=True)
    for sid in (7, 12, 15, 16):
        _, s = get(f"/code-snippets/v1/snippets/{sid}")
        (snap / f"snippet-{sid}.php").write_text(s.get("code") or "", encoding="utf-8")

    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print("WROTE", OUT, flush=True)


if __name__ == "__main__":
    main()
