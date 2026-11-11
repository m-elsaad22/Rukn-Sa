#!/usr/bin/env python3
"""Show SA call button (+966552481093), keep UAE WA, SEO titles with phone+emojis."""

from __future__ import annotations

import base64
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "https://www.rukn-eltatawer.com/sa/wp-json"
AUTH = base64.b64encode(b"cursor:PCkk ig95 Gu6c zOgC GLYG FYsk").decode()
H = {
    "Authorization": f"Basic {AUTH}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 RuknSACallSEO/2026-11-11",
}
ROOT = Path(__file__).resolve().parents[1]
PHONE_LOCAL = "0552481093"
PHONE_INTL = "+966552481093"
PHONE_DIGITS = "966552481093"
WA = "971586634710"
WA_PLUS = "+971586634710"

# service family → (emoji1, emoji2, attractor)
FAM = {
    "leak": ("🔎", "💦", "الشركة المعتمدة"),
    "insul": ("🏠", "🛡️", "خصم 30%"),
    "ac": ("❄️", "💨", "ركن التطور"),
    "clean": ("✨", "🧹", "خدمة فورية"),
    "pest": ("🐛", "🛡️", "مكافحة معتمدة"),
    "drain": ("🔧", "💧", "خصم 25%"),
    "moving": ("📦", "🚚", "ركن التطور"),
    "oven": ("🔥", "✨", "تنظيف معتمد"),
    "tank": ("💧", "✅", "الشركة المعتمدة"),
    "paint": ("🎨", "✨", "خصم 20%"),
    "camera": ("📷", "🔐", "ركن التطور"),
    "default": ("📞", "✅", "ركن التطور"),
}

SNIP15 = r'''/**
 * Rukn SA NAP: Saudi call +966552481093 shown, UAE WhatsApp kept.
 * Does not rewrite per-post SEO title bodies (handled separately).
 */
if ( ! defined( 'ABSPATH' ) ) {
	return;
}

function rukn_sa_wa_digits() {
	return '971586634710';
}

function rukn_sa_phone_intl() {
	return '+966552481093';
}

function rukn_sa_phone_local() {
	return '0552481093';
}

function rukn_sa_trust_apply() {
	$wa      = rukn_sa_wa_digits();
	$wa_plus = '+' . $wa;
	$phone   = rukn_sa_phone_intl();
	$local   = rukn_sa_phone_local();
	$report  = array();

	$keys = array(
		'phonenumber'                 => $phone,
		'contact_number'              => $phone,
		'phone'                       => $phone,
		'info_contact'                => $phone,
		'whatsapp_number'             => $wa_plus,
		'whatsapp'                    => $wa_plus,
		'kayan_country_sa_phone'      => $phone,
		'kayan_country_sa_whatsapp'   => $wa,
		'kayan_show_call_buttons'     => '1',
		'hide__floating__call'        => '0',
		'kayan_homepage_brand_first'  => 'ركن',
		'kayan_homepage_brand_second' => 'التطور',
		'sitename'                    => 'شركة ركن التطور - السعودية',
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
	$biz['telephone']      = $phone;
	$biz['Price_Range']    = 'SAR';
	update_option( 'YourColor_Schema_business', $biz, false );

	$cnb = get_option( 'cnb', array() );
	if ( is_array( $cnb ) ) {
		$cnb['number'] = $phone;
		$cnb['active'] = '1';
		update_option( 'cnb', $cnb, false );
		$report['cnb'] = $cnb;
	}

	$btn = get_option( 'price__button__text', '' );
	$btn_new = 'احجز خطتك الآن مع ركن التطور! اتصل على ' . $local . ' أو واتساب. رابط واتساب: https://wa.me/' . $wa;
	update_option( 'price__button__text', $btn_new, false );
	$report['price__button__text'] = array( 'old' => mb_substr( (string) $btn, 0, 120 ), 'new' => $btn_new );

	$titles = get_option( 'rank-math-options-titles', array() );
	if ( is_array( $titles ) ) {
		$titles['phone_numbers'] = array(
			array( 'type' => 'customer support', 'number' => $phone ),
		);
		update_option( 'rank-math-options-titles', $titles, false );
		$report['rank_math_phone_numbers'] = $phone;
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
		$wa    = rukn_sa_wa_digits();
		$phone = rukn_sa_phone_intl();
		$want  = array(
			'whatsapp_number'           => '+' . $wa,
			'whatsapp'                  => '+' . $wa,
			'phonenumber'               => $phone,
			'contact_number'            => $phone,
			'phone'                     => $phone,
			'info_contact'              => $phone,
			'kayan_country_sa_phone'    => $phone,
			'kayan_country_sa_whatsapp' => $wa,
			'kayan_show_call_buttons'   => '1',
			'hide__floating__call'      => '0',
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
			'/apply-trust-nap',
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

SNIP7 = r'''if ( ! defined( 'ABSPATH' ) ) { return; }

add_action( 'rest_api_init', function () {
	$can = function () { return current_user_can( 'manage_options' ); };

	register_rest_route( 'rukn/v1', '/fix-site-identity', array(
		'methods'             => 'POST',
		'permission_callback' => $can,
		'callback'            => function ( WP_REST_Request $req ) {
			$phone_local = '0552481093';
			$phone_intl  = '+966552481093';
			$phone_wa    = '971586634710';
			$geo         = '24.7136, 46.6753';
			$report      = array();

			$titles = get_option( 'rank-math-options-titles', array() );
			if ( ! is_array( $titles ) ) { $titles = array(); }
			$before = array(
				'geo' => $titles['geo'] ?? null,
				'pt_post_title' => $titles['pt_post_title'] ?? null,
				'homepage_title' => $titles['homepage_title'] ?? null,
				'phone_numbers' => $titles['phone_numbers'] ?? null,
			);

			$titles['geo'] = $geo;
			$titles['pt_post_title'] = '%title% %sep% %sitename%';
			$titles['pt_post_default_snippet_name'] = '%title%';
			$titles['phone_numbers'] = array(
				array( 'type' => 'customer support', 'number' => $phone_intl ),
			);
			$titles['local_address'] = array(
				'streetAddress'   => 'حي النسيم',
				'addressLocality' => 'الرياض',
				'addressRegion'   => 'الرياض',
				'postalCode'      => '11461',
				'addressCountry'  => 'SA',
			);
			$titles['homepage_title'] = 'شركة ركن التطور | صيانة عامة وكشف تسربات المياه والعزل في السعودية';
			$titles['homepage_description'] = 'شركة ركن التطور للصيانة العامة والخدمات المتكاملة في السعودية، متخصصة في كشف تسربات المياه، العزل، صيانة المباني والمكيفات، والتنظيف. خدمة 24 ساعة. اتصل الآن: ' . $phone_local . '.';
			$titles['homepage_facebook_title'] = 'شركة ركن التطور – صيانة عامة وخدمات متكاملة في السعودية';
			$titles['homepage_facebook_description'] = 'نقدم خدمات الصيانة العامة، كشف تسربات المياه، العزل، والتنظيف في جميع أنحاء السعودية. تواصل معنا الآن على ' . $phone_local . '.';
			$titles['organization_description'] = "شركة ركن التطور للخدمات المتكاملة في المملكة العربية السعودية، متخصصة في كشف تسربات المياه، الصيانة العامة، العزل، والتنظيف، باستخدام أحدث الأجهزة وبدون تكسير.\nنغطي جميع مناطق السعودية مع خدمة 24 ساعة، سرعة تنفيذ، وأسعار تنافسية.";
			$titles['url'] = 'https://www.rukn-eltatawer.com/sa';
			$titles['knowledgegraph_name'] = 'شركة ركن التطور';
			$titles['local_business_type'] = 'HomeAndConstructionBusiness';
			$titles['local_seo'] = true;

			update_option( 'rank-math-options-titles', $titles, false );
			$report['rank_math_titles'] = array( 'before' => $before, 'after_geo' => $titles['geo'], 'after_pt_post_title' => $titles['pt_post_title'] );

			$simple_opts = array(
				'whatsapp_number' => '+' . $phone_wa,
				'phone'           => $phone_intl,
				'whatsapp'        => '+' . $phone_wa,
				'info_contact'    => $phone_intl,
				'phonenumber'     => $phone_intl,
			);
			foreach ( $simple_opts as $k => $v ) {
				$old = get_option( $k );
				update_option( $k, $v, false );
				$report['options'][ $k ] = array( 'old' => $old, 'new' => $v );
			}

			$price = get_option( 'price__option_data', array() );
			if ( ! is_array( $price ) ) { $price = array(); }
			$price['price__mode'] = 'watshapp';
			$price['watshapp'] = array( 'watshapp' => '+' . $phone_wa );
			update_option( 'price__option_data', $price, false );
			$report['price__option_data'] = $price;

			$btn = get_option( 'price__button__text', '' );
			$btn_new = 'احجز خطتك الآن مع ركن التطور! اتصل على ' . $phone_local . ' أو واتساب: https://wa.me/' . $phone_wa;
			update_option( 'price__button__text', $btn_new, false );
			$report['price__button__text'] = array( 'old' => mb_substr( (string) $btn, 0, 120 ), 'new' => $btn_new );

			$cnb = get_option( 'cnb', array() );
			if ( is_array( $cnb ) ) {
				$cnb['number'] = $phone_intl;
				$cnb['active'] = '1';
				update_option( 'cnb', $cnb, false );
				$report['cnb'] = $cnb['number'];
			}

			$biz = get_option( 'YourColor_Schema_business', array() );
			if ( ! is_array( $biz ) ) { $biz = array(); }
			$biz['Business_Name'] = $biz['Business_Name'] ?? 'ركن التطور';
			$biz['Street_Address'] = $biz['Street_Address'] ?: 'حي النسيم';
			$biz['Country'] = 'SA';
			$biz['City'] = 'Riyadh';
			$biz['State'] = 'Riyadh';
			$biz['Postal_Code'] = $biz['Postal_Code'] ?: '11461';
			$biz['telephone'] = $phone_intl;
			$biz['Price_Range'] = 'SAR';
			update_option( 'YourColor_Schema_business', $biz, false );
			$report['YourColor_Schema_business_telephone'] = $biz['telephone'];

			if ( class_exists( 'LiteSpeed\Purge' ) ) {
				try { \LiteSpeed\Purge::purge_all(); $report['cache'] = 'litespeed_purged'; } catch ( Exception $e ) { $report['cache'] = $e->getMessage(); }
			} elseif ( function_exists( 'do_action' ) ) {
				do_action( 'litespeed_purge_all' );
				$report['cache'] = 'litespeed_purge_all_action';
			}

			return rest_ensure_response( array( 'ok' => true, 'report' => $report ) );
		},
	) );
} );
'''

SNIP16 = r'''/**
 * Rukn SA theme hardening: titles cleanup (keep official SA phone), redirects, dump-keys auth.
 */
if ( ! defined( 'ABSPATH' ) ) {
	return;
}

add_action(
	'after_setup_theme',
	function () {
		add_theme_support( 'title-tag' );
	},
	99
);

function rukn_sa_title_clean( $title ) {
	if ( ! is_string( $title ) ) {
		return $title;
	}
	// Protect official numbers then strip polluted leftovers.
	$title = str_replace(
		array( '0552481093', '+966552481093', '966552481093' ),
		array( '__RUKN_PHONE__', '__RUKN_PHONE_PLUS__', '__RUKN_PHONE_DIGITS__' ),
		$title
	);
	$title = str_replace( array( '♻', '♻️' ), '', $title );
	$title = preg_replace( '/\b0568060309\b/u', '', $title );
	$title = preg_replace( '/\b01151481000\b/u', '', $title );
	$title = preg_replace( '/\b01\d{8,10}\b/u', '', $title );
	$title = preg_replace( '/📢\s*الإعلان للإيجار/u', '', $title );
	// strip unknown SA mobiles except protected
	$title = preg_replace( '/\+?966\s*5\d{8}/u', '', $title );
	$title = preg_replace( '/\b05\d{8}\b/u', '', $title );
	$title = str_replace(
		array( '__RUKN_PHONE__', '__RUKN_PHONE_PLUS__', '__RUKN_PHONE_DIGITS__' ),
		array( '0552481093', '+966552481093', '966552481093' ),
		$title
	);
	return trim( preg_replace( '/\s{2,}/u', ' ', $title ) );
}

add_action(
	'wp_head',
	function () {
		if ( did_action( '_wp_render_title_tag' ) ) {
			return;
		}
		$title = function_exists( 'wp_get_document_title' ) ? wp_get_document_title() : get_bloginfo( 'name' );
		$title = rukn_sa_title_clean( $title );
		echo '<title>' . esc_html( $title ) . '</title>' . "\n";
		echo '<meta property="og:title" content="' . esc_attr( $title ) . '" />' . "\n";
		if ( is_singular() ) {
			$desc = get_the_excerpt();
			if ( is_string( $desc ) && $desc !== '' ) {
				$desc = wp_strip_all_tags( $desc );
				$desc = rukn_sa_title_clean( $desc );
				echo '<meta name="description" content="' . esc_attr( trim( $desc ) ) . '" />' . "\n";
			}
		}
	},
	0
);

add_filter(
	'document_title_parts',
	function ( $parts ) {
		foreach ( $parts as $k => $v ) {
			if ( is_string( $v ) ) {
				$parts[ $k ] = rukn_sa_title_clean( $v );
			}
		}
		return $parts;
	},
	99
);

add_filter(
	'rank_math/frontend/title',
	function ( $title ) {
		return rukn_sa_title_clean( $title );
	},
	99
);

add_filter(
	'rank_math/frontend/description',
	function ( $desc ) {
		return is_string( $desc ) ? rukn_sa_title_clean( $desc ) : $desc;
	},
	99
);

add_action(
	'template_redirect',
	function () {
		$uri = isset( $_SERVER['REQUEST_URI'] ) ? (string) $_SERVER['REQUEST_URI'] : '';
		if ( preg_match( '#/sa/sa(/|$|\?)#', $uri ) ) {
			wp_safe_redirect( home_url( '/' ), 301 );
			exit;
		}
		if ( preg_match( '#/city/riyadh/?#', $uri ) ) {
			wp_safe_redirect( home_url( '/cities/riyadh/' ), 301 );
			exit;
		}
		if ( preg_match( '#/city/([^/?]+)/?#', $uri, $m ) ) {
			wp_safe_redirect( home_url( '/cities/' . sanitize_title( $m[1] ) . '/' ), 301 );
			exit;
		}
	},
	1
);

add_filter(
	'rest_pre_dispatch',
	function ( $result, $server, $request ) {
		if ( $result !== null ) {
			return $result;
		}
		if ( ! $request instanceof WP_REST_Request ) {
			return $result;
		}
		$route = $request->get_route();
		if ( '/rukn/v1/dump-keys' === $route && ! current_user_can( 'manage_options' ) ) {
			return new WP_Error( 'rest_forbidden', 'Authentication required.', array( 'status' => 401 ) );
		}
		return $result;
	},
	0,
	3
);

add_action(
	'init',
	function () {
		if ( function_exists( 'yc_update_option' ) ) {
			yc_update_option( 'currency', 'SAR' );
			yc_update_option( 'taxRate', '15' );
		}
		$booking = get_option( 'KayanBookingConfig', array() );
		if ( is_array( $booking ) ) {
			$booking['currency'] = 'SAR';
			$booking['taxRate']  = '15';
			update_option( 'KayanBookingConfig', $booking, false );
		}
	},
	30
);
'''


def req(method: str, path: str, payload=None, retries: int = 5):
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode()
    last = None
    for i in range(retries):
        try:
            r = urllib.request.Request(BASE + path, data=data, headers=H, method=method)
            with urllib.request.urlopen(r, timeout=120) as resp:
                raw = resp.read().decode()
                return json.loads(raw) if raw else {}
        except Exception as e:
            last = e
            time.sleep(1.2 * (i + 1))
    raise last


def get_snippet(sid: int) -> str:
    return req("GET", f"/code-snippets/v1/snippets/{sid}")["code"]


def put_snippet(sid: int, code: str, name: str | None = None):
    payload = {"code": code, "active": True}
    if name:
        payload["name"] = name
    return req("PUT", f"/code-snippets/v1/snippets/{sid}", payload)


def patch_snippet_12(code: str) -> str:
    """Surgical updates on live frontend copy guard."""
    new_strip = r'''function rukn_sa_strip_other_phones( $html ) {
	if ( ! is_string( $html ) || $html === '' ) {
		return $html;
	}
	$wa = '971586634710';
	$phone_local = '0552481093';
	$phone_intl = '+966552481093';
	$phone_digits = '966552481093';

	// 1) Protect WA + official SA call number.
	$html = preg_replace( '#https?://wa\.me/\+?[^"\s<]*#i', 'https://wa.me/__RUKN_WA__', $html );
	$html = str_replace( array( '+971586634710', '971586634710' ), array( '__RUKN_WA_PLUS__', '__RUKN_WA__' ), $html );
	$html = str_replace(
		array( $phone_local, $phone_intl, $phone_digits ),
		array( '__RUKN_PHONE__', '__RUKN_PHONE_PLUS__', '__RUKN_PHONE_DIGITS__' ),
		$html
	);

	// 2) Force call links to official SA number (placeholder form so strip won't eat it).
	$html = preg_replace( '#href="tel:[^"]*"#i', 'href="tel:__RUKN_PHONE_PLUS__"', $html );

	// 3) Strip other phone numbers (placeholders intact).
	$patterns = array(
		'/\+?966\s*5\d{8}/u',
		'/\b05\d{8}\b/u',
		'/\b01\d{8,10}\b/u',
		'/\b01151481000\b/u',
		'/\+?9715\d{8}/u',
		'/\+?201\d{9}/u',
		'/\b01556644443\b/u',
		'/\b966000000000\b/u',
		'/\+966000000000/u',
		'/📢\s*الإعلان للإيجار/u',
	);
	foreach ( $patterns as $pat ) {
		$html = preg_replace( $pat, '', $html );
	}
	$html = preg_replace( '/"telephone"\s*:\s*"[^"]*"/', '"telephone":"' . $phone_intl . '"', $html );
	$html = preg_replace( '/\s{2,}/u', ' ', $html );

	// 4) Restore WA + SA call.
	$html = str_replace(
		array(
			'https://wa.me/__RUKN_WA__',
			'__RUKN_WA_PLUS__',
			'__RUKN_WA__',
			'__RUKN_PHONE__',
			'__RUKN_PHONE_PLUS__',
			'__RUKN_PHONE_DIGITS__',
		),
		array(
			'https://wa.me/' . $wa,
			'+' . $wa,
			$wa,
			$phone_local,
			$phone_intl,
			$phone_digits,
		),
		$html
	);
	return $html;
}'''

    m = re.search(
        r"function rukn_sa_strip_other_phones\( \$html \) \{.*?\n\}\n\n\nfunction rukn_sa_rewrite_html",
        code,
        flags=re.S,
    )
    if not m:
        raise SystemExit("could not locate rukn_sa_strip_other_phones in snippet 12")
    code = code[: m.start()] + new_strip + "\n\nfunction rukn_sa_rewrite_html" + code[m.end() :]

    code = code.replace(
        'window.RuknCS={"call_show":false,"wa_show":true,"call_number":"","wa_number":"\' . $wa . \'","wa_message":"مرحباً! شركة ركن التطور - السعودية"}',
        'window.RuknCS={"call_show":true,"wa_show":true,"call_number":"+966552481093","wa_number":"\' . $wa . \'","wa_message":"مرحباً! شركة ركن التطور - السعودية"}',
    )
    # alternate quote style if present
    code = re.sub(
        r'window\.RuknCS=\{"call_show":false,"wa_show":true,"call_number":"","wa_number":"\' \. \$wa \. \'","wa_message":"مرحباً! شركة ركن التطور - السعودية"\}',
        'window.RuknCS={"call_show":true,"wa_show":true,"call_number":"+966552481093","wa_number":"\' . $wa . \'","wa_message":"مرحباً! شركة ركن التطور - السعودية"}',
        code,
    )

    # Remove CSS that hides call buttons
    code = re.sub(
        r"a\[href\^=\"tel:\"\],\.call-btn,\.btn-call,\.floating-call,\.cnb-button,\.cnb-full,\.phone-btn,\[class\*=\"call-now\"\],\[class\*=\"floating__call\"\](?:,\[id\*=\"call-button\"\])?\{display:none!important\}",
        "/* call buttons visible */",
        code,
    )

    # Update header comment
    code = code.replace(
        "Rukn SA frontend repair: UAE WhatsApp only, hide call, strip all other phones.",
        "Rukn SA frontend repair: show SA call +966552481093, keep UAE WhatsApp, strip other phones.",
    )

    # JSON-LD: set telephone instead of unset
    code = code.replace(
        "unset( $data[ $key ]['telephone'] );",
        "$data[ $key ]['telephone'] = '+966552481093';",
    )

    # DNI REST override
    code = code.replace(
        """			$data['phone']     = '';
			$data['wa_number'] = '971586634710';
			$data['call_show'] = false;
			$data['wa_show']   = true;""",
        """			$data['phone']     = '+966552481093';
			$data['wa_number'] = '971586634710';
			$data['call_show'] = true;
			$data['wa_show']   = true;""",
    )

    # Remove body.rukn-hide-call class forcing if any inline — keep generic
    code = code.replace("rukn-hide-call", "rukn-call-enabled")

    return code


def classify(slug: str, title: str) -> str:
    blob = f"{slug} {title}".lower()
    rules = [
        ("leak", ["leak", "تسرب", "تسربات"]),
        ("insul", ["insulation", "عزل", "عوازل"]),
        ("ac", ["ac-cleaning", "ac_", "مكيف", "تكييف", "غسيل-مكيف"]),
        ("oven", ["oven", "أفران", "افران", "فرن"]),
        ("pest", ["pest", "cockroach", "termite", "مكافحة", "صراصير", "نمل", "بق", "فئران", "حشرات"]),
        ("drain", ["drain", "sewer", "مجاري", "تسليك"]),
        ("moving", ["moving", "furniture", "نقل", "عفش", "اثاث", "أثاث"]),
        ("tank", ["tank", "خزان", "خزانات"]),
        ("paint", ["paint", "دهان", "صبغ"]),
        ("camera", ["camera", "كاميرا", "مراقبة"]),
        ("clean", ["cleaning", "clean", "تنظيف", "جلي", "غسيل-سجاد", "سجاد"]),
    ]
    for fam, keys in rules:
        if any(k in blob for k in keys):
            return fam
    return "default"


def seo_title_for(slug: str, title: str) -> str:
    fam = classify(slug, title)
    e1, e2, attr = FAM[fam]
    return f"%title% {e1} {PHONE_LOCAL} {e2} {attr}"


def list_all(ctype: str):
    items = []
    page = 1
    while True:
        batch = None
        for attempt in range(5):
            try:
                r = urllib.request.Request(
                    BASE + f"/wp/v2/{ctype}?per_page=100&page={page}&status=publish&_fields=id,slug,title",
                    headers={k: v for k, v in H.items() if k != "Content-Type"},
                )
                with urllib.request.urlopen(r, timeout=120) as resp:
                    batch = json.loads(resp.read().decode())
                    total_pages = int(resp.headers.get("X-WP-TotalPages") or "1")
                break
            except urllib.error.HTTPError as e:
                if e.code == 400 and page > 1:
                    return items
                time.sleep(1.2 * (attempt + 1))
            except Exception:
                time.sleep(1.2 * (attempt + 1))
        if not batch:
            break
        for p in batch:
            title = p["title"]["rendered"] if isinstance(p["title"], dict) else str(p["title"])
            items.append({"id": p["id"], "slug": p["slug"], "title": title, "type": ctype})
        if page >= total_pages:
            break
        page += 1
        if page % 5 == 0:
            print(f"  listed {ctype} page {page}/{total_pages}", flush=True)
    return items


def update_titles(items):
    rows = []
    for it in items:
        obj_type = "post" if it["type"] in ("posts", "services") else "post" if it["type"] == "posts" else it["type"].rstrip("s")
        # Rank Math objectType: post for posts/custom posts, page for pages
        if it["type"] == "pages":
            obj_type = "page"
        elif it["type"] == "services":
            obj_type = "services"
        else:
            obj_type = "post"
        seo = seo_title_for(it["slug"], it["title"])
        rows.append(
            {
                "objectID": it["id"],
                "objectType": obj_type,
                "meta": {"rank_math_title": seo},
                "_fam": classify(it["slug"], it["title"]),
                "_seo": seo,
                "_slug": it["slug"],
            }
        )

    # Per-item updateMeta (bulk endpoint can report success without persisting).
    ok = 0
    fails = []
    for i, r in enumerate(rows, 1):
        try:
            req(
                "POST",
                "/rankmath/v1/updateMeta",
                {
                    "objectType": r["objectType"],
                    "objectID": r["objectID"],
                    "meta": r["meta"],
                },
            )
            ok += 1
        except Exception as e:
            try:
                req(
                    "POST",
                    "/rankmath/v1/updateMeta",
                    {
                        "objectType": "post",
                        "objectID": r["objectID"],
                        "meta": r["meta"],
                    },
                )
                ok += 1
            except Exception as e2:
                fails.append({"id": r["objectID"], "error": str(e2)})
        if i % 50 == 0 or i == len(rows):
            print(f"titles {i}/{len(rows)} ok={ok} fails={len(fails)}", flush=True)
        time.sleep(0.05)
    return rows, ok, fails


def main():
    out = {"phone": PHONE_INTL, "wa": WA_PLUS, "steps": {}}

    print("1) patch snippets", flush=True)
    live12 = get_snippet(12)
    new12 = patch_snippet_12(live12)
    if "call_show\":true" not in new12 and "call_show\":true" not in new12.replace("\\", ""):
        # verify critical markers
        if 'call_show":true' not in new12:
            raise SystemExit("snippet 12 patch failed: call_show not true")
    if "display:none!important" in new12 and "a[href^=\"tel:\"]" in new12:
        # may still have other none rules; ensure tel hide rule gone
        if re.search(r'a\[href\^="tel:"\][^\{]*\{display:none', new12):
            raise SystemExit("snippet 12 still hides tel links")

    (ROOT / "data/snippets").mkdir(parents=True, exist_ok=True)
    (ROOT / "data/snippets/snippet-12.php").write_text(new12, encoding="utf-8")
    (ROOT / "data/snippets/snippet-15.php").write_text(SNIP15, encoding="utf-8")
    (ROOT / "data/snippets/snippet-7.php").write_text(SNIP7, encoding="utf-8")
    (ROOT / "data/snippets/snippet-16.php").write_text(SNIP16, encoding="utf-8")

    put_snippet(15, SNIP15, "Rukn SA Trust NAP Fix")
    put_snippet(12, new12, "Rukn SA Frontend Copy Guard")
    put_snippet(7, SNIP7, "Rukn Fix Site Identity Schema Phones")
    put_snippet(16, SNIP16, "Rukn SA Theme Hardening")
    out["steps"]["snippets"] = "updated_7_12_15_16"

    print("2) apply NAP", flush=True)
    try:
        out["steps"]["apply_trust_nap"] = req("POST", "/rukn/v1/apply-trust-nap")
    except Exception as e:
        out["steps"]["apply_trust_nap_error"] = str(e)
    try:
        out["steps"]["fix_site_identity"] = req("POST", "/rukn/v1/fix-site-identity")
    except Exception as e:
        out["steps"]["fix_site_identity_error"] = str(e)

    print("3) dump-keys", flush=True)
    out["dump_keys"] = req("GET", "/rukn/v1/dump-keys")
    print(out["dump_keys"], flush=True)

    print("4) list content", flush=True)
    items = []
    for ctype in ("posts", "pages", "services"):
        part = list_all(ctype)
        print(f"  {ctype}: {len(part)}", flush=True)
        items.extend(part)
    out["counts"] = {
        "posts": sum(1 for i in items if i["type"] == "posts"),
        "pages": sum(1 for i in items if i["type"] == "pages"),
        "services": sum(1 for i in items if i["type"] == "services"),
        "total": len(items),
    }

    print("5) SEO titles", flush=True)
    rows, ok, fails = update_titles(items)
    out["titles_ok"] = ok
    out["titles_fails"] = fails
    out["title_samples"] = [
        {"id": r["objectID"], "slug": r["_slug"], "fam": r["_fam"], "seo": r["_seo"]} for r in rows[:12]
    ]
    # fam distribution
    dist = {}
    for r in rows:
        dist[r["_fam"]] = dist.get(r["_fam"], 0) + 1
    out["fam_dist"] = dist

    path = ROOT / "data/sa-call-seo-titles-results-2026-11-11.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("WROTE", path, flush=True)
    print("SUMMARY", {"titles_ok": ok, "fails": len(fails), "dump": out.get("dump_keys")}, flush=True)


if __name__ == "__main__":
    main()
