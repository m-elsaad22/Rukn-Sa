/**
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
