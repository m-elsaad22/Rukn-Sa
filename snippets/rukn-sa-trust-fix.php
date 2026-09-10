<?php
/**
 * Rukn SA trust fix: NAP, copyrights, homepage stats, frontend number guard.
 * Installed via Code Snippets REST as snippet "Rukn SA Trust NAP Fix".
 */
if ( ! defined( 'ABSPATH' ) ) {
	return;
}

function rukn_sa_trust_apply() {
	$phone_local = '0568060309';
	$phone_intl  = '+966568060309';
	$phone_wa    = '966568060309';
	$report      = array();

	$keys = array(
		'phonenumber'                 => $phone_local,
		'contact_number'              => $phone_local,
		'phone'                       => $phone_local,
		'info_contact'                => $phone_local,
		'whatsapp_number'             => $phone_intl,
		'whatsapp'                    => $phone_intl,
		'kayan_country_sa_phone'      => $phone_local,
		'kayan_country_sa_whatsapp'   => $phone_wa,
		'kayan_show_call_buttons'     => '1',
		'hide__floating__call'        => '',
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
		$old = get_option( $ck );
		update_option( $ck, $copy, false );
		if ( function_exists( 'yc_update_option' ) ) {
			yc_update_option( $ck, $copy );
		}
		$report['copyrights'][ $ck ] = is_string( $old ) ? mb_substr( $old, 0, 240 ) : $old;
	}

	$stats = array(
		array(
			'label'  => 'خدمة أساسية',
			'count'  => '12',
			'suffix' => '',
			'dec'    => '',
		),
		array(
			'label'  => 'مدينة نغطيها',
			'count'  => '18',
			'suffix' => '+',
			'dec'    => '',
		),
		array(
			'label'  => 'سنوات عمل',
			'count'  => '10',
			'suffix' => '+',
			'dec'    => '',
		),
	);
	if ( function_exists( 'yc_update_option' ) ) {
		yc_update_option( 'kayan_hp_stats_items', $stats );
	}
	update_option( 'kayan_hp_stats_items', $stats, false );
	$report['stats'] = $stats;

	$reviews = function_exists( 'yc_get_option' ) ? yc_get_option( 'kayan_seo_home_reviews' ) : get_option( 'kayan_seo_home_reviews' );
	if ( is_array( $reviews ) && $reviews ) {
		$uae_cities = array( 'دبي', 'أبوظبي', 'الشارقة', 'عجمان', 'العين' );
		$has_uae    = false;
		foreach ( $reviews as $rv ) {
			$city = isset( $rv['city'] ) ? $rv['city'] : '';
			if ( in_array( $city, $uae_cities, true ) ) {
				$has_uae = true;
				break;
			}
		}
		if ( $has_uae ) {
			if ( function_exists( 'yc_update_option' ) ) {
				yc_update_option( 'kayan_seo_home_reviews', array() );
			}
			update_option( 'kayan_seo_home_reviews', array(), false );
			$report['reviews'] = 'cleared_uae_placeholders';
		} else {
			$report['reviews'] = 'kept_existing';
		}
	} else {
		$report['reviews'] = 'empty';
	}

	if ( function_exists( 'do_action' ) ) {
		do_action( 'litespeed_purge_all' );
		$report['cache'] = 'litespeed_purge_all_action';
	}

	return $report;
}

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
						'Copyrights',
						'kayan_country_sa_phone',
						'kayan_country_sa_whatsapp',
						'kayan_hp_stats_items',
						'kayan_hp_hero_title',
						'kayan_homepage_brand_first',
						'kayan_seo_home_reviews',
						'sitename',
						'kayan_show_call_buttons',
						'hide__floating__call',
					);
					$out  = array();
					foreach ( $keys as $k ) {
						$out[ $k ] = function_exists( 'yc_get_option' ) ? yc_get_option( $k ) : get_option( $k );
					}
					return rest_ensure_response( $out );
				},
			)
		);
	}
);

add_action(
	'template_redirect',
	function () {
		if ( is_admin() ) {
			return;
		}
		ob_start(
			function ( $html ) {
				if ( ! is_string( $html ) || $html === '' ) {
					return $html;
				}
				$map = array(
					'+201556644443' => '+966568060309',
					'201556644443'  => '966568060309',
					'01556644443'   => '0568060309',
					'+201151481000' => '+966568060309',
					'201151481000'  => '966568060309',
				);
				$html = strtr( $html, $map );
				$html = str_replace( 'شركة كيان ويب للتسويق الإلكتروني', 'شركة ركن التطور', $html );
				return $html;
			}
		);
	},
	1
);
