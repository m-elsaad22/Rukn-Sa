/**
 * Rukn SA trust fix: WhatsApp UAE (temporary), hide call buttons, Saudi identity.
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
		'kayan_show_call_buttons'   => '',
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

	$stats = array(
		array( 'label' => 'خدمة أساسية', 'count' => '12', 'suffix' => '', 'dec' => '' ),
		array( 'label' => 'مدينة نغطيها', 'count' => '18', 'suffix' => '+', 'dec' => '' ),
		array( 'label' => 'سنوات عمل', 'count' => '10', 'suffix' => '+', 'dec' => '' ),
	);
	if ( function_exists( 'yc_update_option' ) ) {
		yc_update_option( 'kayan_hp_stats_items', $stats );
	}
	update_option( 'kayan_hp_stats_items', $stats, false );
	$report['stats'] = $stats;

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
	unset( $biz['telephone'] );
	$biz['Price_Range'] = 'SAR';
	update_option( 'YourColor_Schema_business', $biz, false );

	$reviews = function_exists( 'yc_get_option' ) ? yc_get_option( 'kayan_seo_home_reviews' ) : get_option( 'kayan_seo_home_reviews' );
	if ( is_array( $reviews ) && $reviews ) {
		$uae_cities = array( 'دبي', 'أبوظبي', 'الشارقة', 'عجمان', 'العين' );
		foreach ( $reviews as $rv ) {
			$city = isset( $rv['city'] ) ? $rv['city'] : '';
			if ( in_array( $city, $uae_cities, true ) ) {
				if ( function_exists( 'yc_update_option' ) ) {
					yc_update_option( 'kayan_seo_home_reviews', array() );
				}
				update_option( 'kayan_seo_home_reviews', array(), false );
				$report['reviews'] = 'cleared_uae_placeholders';
				break;
			}
		}
	}

	if ( function_exists( 'do_action' ) ) {
		do_action( 'litespeed_purge_all' );
		$report['cache'] = 'purged';
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
						'kayan_country_sa_phone',
						'kayan_country_sa_whatsapp',
						'kayan_hp_stats_items',
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
