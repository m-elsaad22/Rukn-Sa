/**
 * Rukn SA theme hardening: titles, /sa/sa/ redirect, dump-keys auth, 404, EN noindex.
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

add_action(
	'wp_head',
	function () {
		if ( did_action( '_wp_render_title_tag' ) ) {
			return;
		}
		$title = function_exists( 'wp_get_document_title' ) ? wp_get_document_title() : get_bloginfo( 'name' );
		$title = str_replace( array( '♻', '♻️' ), '', $title );
		echo '<title>' . esc_html( $title ) . '</title>' . "\n";
		echo '<meta property="og:title" content="' . esc_attr( $title ) . '" />' . "\n";
		if ( is_singular() ) {
			$desc = get_the_excerpt();
			if ( is_string( $desc ) && $desc !== '' ) {
				$desc = wp_strip_all_tags( $desc );
				$desc = str_replace( array( '0568060309', '♻' ), '', $desc );
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
				$parts[ $k ] = trim( str_replace( array( '♻', '♻️' ), '', $v ) );
			}
		}
		return $parts;
	},
	99
);

add_filter(
	'rank_math/frontend/title',
	function ( $title ) {
		return is_string( $title ) ? trim( str_replace( array( '♻', '♻️' ), '', $title ) ) : $title;
	},
	99
);

add_filter(
	'rank_math/frontend/description',
	function ( $desc ) {
		if ( ! is_string( $desc ) ) {
			return $desc;
		}
		$desc = str_replace( array( '0568060309', '♻', '♻️' ), '', $desc );
		return trim( preg_replace( '/\s{2,}/u', ' ', $desc ) );
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

add_action(
	'wp_head',
	function () {
		$uri = isset( $_SERVER['REQUEST_URI'] ) ? (string) $_SERVER['REQUEST_URI'] : '';
		if ( false !== strpos( $uri, '/en/' ) || ( function_exists( 'pll_current_language' ) && 'en' === pll_current_language() ) ) {
			echo '<meta name="robots" content="noindex, follow" />' . "\n";
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

add_filter(
	'wp_sitemaps_enabled',
	function ( $enabled ) {
		return $enabled;
	}
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
