<?php
/**
 * Source mirror of Code Snippet #8: Rukn SA Google Indexing Fix
 * Applied live via Code Snippets plugin.
 */

if ( ! defined( 'ABSPATH' ) ) { return; }

/**
 * Write / update physical robots.txt for the SA WordPress root.
 */
function rukn_sa_robots_contents() {
	return "User-Agent: *\n"
		. "Allow: /\n"
		. "Allow: /wp-admin/admin-ajax.php\n"
		. "Allow: /wp-content/uploads/\n"
		. "Disallow: /wp-admin/\n"
		. "Disallow: /wp-includes/\n"
		. "Disallow: /wp-content/plugins/\n"
		. "Disallow: /trackback\n"
		. "Disallow: /*.php$\n"
		. "Disallow: /*.inc$\n"
		. "Disallow: /*.gz$\n"
		. "Disallow: /wp-login.php\n"
		. "\n"
		. "Sitemap: https://www.rukn-eltatawer.com/sa/sitemap_index.xml\n";
}

function rukn_sa_write_robots_file() {
	$path = ABSPATH . 'robots.txt';
	$contents = rukn_sa_robots_contents();
	$written = false;
	$method = 'none';

	if ( function_exists( 'WP_Filesystem' ) ) {
		require_once ABSPATH . 'wp-admin/includes/file.php';
		$creds = request_filesystem_credentials( site_url(), '', false, false, null );
		if ( WP_Filesystem( $creds ) ) {
			global $wp_filesystem;
			$written = $wp_filesystem->put_contents( $path, $contents, FS_CHMOD_FILE );
			$method = 'wp_filesystem';
		}
	}
	if ( ! $written ) {
		$written = ( false !== @file_put_contents( $path, $contents ) );
		$method = 'file_put_contents';
	}

	// Also force virtual robots_txt filter as fallback when no physical file is used.
	return array(
		'path'       => $path,
		'abspath'    => ABSPATH,
		'exists'     => file_exists( $path ),
		'writable'   => is_writable( ABSPATH ) || ( file_exists( $path ) && is_writable( $path ) ),
		'written'    => (bool) $written,
		'method'     => $method,
		'size'       => file_exists( $path ) ? filesize( $path ) : 0,
		'preview'    => file_exists( $path ) ? substr( (string) @file_get_contents( $path ), 0, 500 ) : '',
	);
}

add_filter( 'robots_txt', function ( $output, $public ) {
	if ( '0' === (string) $public ) {
		return $output;
	}
	return rukn_sa_robots_contents();
}, 99999, 2 );

// Prevent Rank Math from appending/overriding sitemap to root domain if filter available.
add_filter( 'rank_math/robots/sitemap', function ( $sitemap ) {
	return 'https://www.rukn-eltatawer.com/sa/sitemap_index.xml';
} );

add_action( 'rest_api_init', function () {
	register_rest_route( 'rukn/v1', '/fix-robots', array(
		'methods'             => 'POST',
		'permission_callback' => function () { return current_user_can( 'manage_options' ); },
		'callback'            => function () {
			$info = rukn_sa_write_robots_file();
			do_action( 'litespeed_purge_all' );
			return $info;
		},
	) );

	register_rest_route( 'rukn/v1', '/ping-sitemaps', array(
		'methods'             => 'POST',
		'permission_callback' => function () { return current_user_can( 'manage_options' ); },
		'callback'            => function () {
			$urls = array(
				'https://www.rukn-eltatawer.com/sa/sitemap_index.xml',
				'https://www.rukn-eltatawer.com/sa/post-sitemap.xml',
			);
			$results = array();
			foreach ( $urls as $u ) {
				$ping = 'https://www.google.com/ping?sitemap=' . rawurlencode( $u );
				$res  = wp_remote_get( $ping, array( 'timeout' => 15 ) );
				$results[] = array(
					'sitemap' => $u,
					'code'    => is_wp_error( $res ) ? $res->get_error_message() : wp_remote_retrieve_response_code( $res ),
				);
			}
			return array( 'ok' => true, 'results' => $results );
		},
	) );
} );

add_filter( 'rank_math/json_ld', function ( $data, $jsonld ) {
	if ( empty( $data ) || ! is_array( $data ) ) { return $data; }
	foreach ( $data as $key => $piece ) {
		if ( ! is_array( $piece ) ) { continue; }
		$types = isset( $piece['@type'] ) ? (array) $piece['@type'] : array();
		$biz = array( 'Organization', 'LocalBusiness', 'HomeAndConstructionBusiness' );
		if ( array_intersect( $types, $biz ) || ( isset( $piece['@id'] ) && false !== strpos( (string) $piece['@id'], '#organization' ) ) ) {
			$data[ $key ]['telephone'] = '0568060309';
			$data[ $key ]['areaServed'] = array( '@type' => 'Country', 'name' => 'Saudi Arabia' );
		}
		if ( in_array( 'Place', $types, true ) || ( isset( $piece['@id'] ) && false !== strpos( (string) $piece['@id'], '#place' ) ) ) {
			$data[ $key ]['geo'] = array( '@type' => 'GeoCoordinates', 'latitude' => '24.7136', 'longitude' => '46.6753' );
		}
	}
	return $data;
}, 99, 2 );

