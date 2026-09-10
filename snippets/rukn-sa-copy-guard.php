<?php
/**
 * Replace leftover UAE/Egypt copy in frontend HTML.
 */
if ( ! defined( 'ABSPATH' ) ) {
	return;
}

add_filter(
	'rank_math/frontend/breadcrumb/items',
	function ( $crumbs ) {
		if ( empty( $crumbs ) || ! is_array( $crumbs ) ) {
			return $crumbs;
		}
		if ( isset( $crumbs[0][0] ) && in_array( $crumbs[0][0], array( 'Home', 'home' ), true ) ) {
			$crumbs[0][0] = 'الرئيسية';
		}
		return $crumbs;
	},
	20
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
				$html = str_replace( 'خريطة الإمارات', 'خريطة السعودية', $html );
				$html = str_replace( 'خبرة 12 عاماً في الإمارات', 'خبرة 12 عاماً في السعودية', $html );
				$html = str_replace( 'خبرة 12 عامًا في الإمارات', 'خبرة 12 عامًا في السعودية', $html );
				$html = str_replace( '+201556644443', '+966568060309', $html );
				$html = str_replace( '201556644443', '966568060309', $html );
				$html = str_replace( '01556644443', '0568060309', $html );
				$html = str_replace( '+201151481000', '+966568060309', $html );
				$html = str_replace( '201151481000', '966568060309', $html );
				return $html;
			}
		);
	}
);
