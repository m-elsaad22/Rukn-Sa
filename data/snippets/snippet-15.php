/**
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
