/**
 * Rukn SA GSC indexing fix (Search Console sitemap sa/sitemap_index.xml).
 *
 * 301 cannibal duplicates + leftover 404s, noindex EN/author/empty archives,
 * include WordPress pages in Rank Math sitemap, exclude redirected/EN URLs.
 */
if ( ! defined( 'ABSPATH' ) ) {
	return;
}

function rukn_sa_gsc_redirect_map() {
	return array(
		'water-leak-detection-south-jeddah' => '/water-leak-detection-jeddah/',
		'water-leak-detection-east-jeddah' => '/water-leak-detection-jeddah/',
		'water-leak-detection-north-jeddah' => '/water-leak-detection-jeddah/',
		'water-leak-detection-jeddah-center' => '/water-leak-detection-jeddah/',
		'water-leak-detection-east-riyadh' => '/water-leak-detection-riyadh-center/',
		'water-leak-detection-north-riyadh' => '/water-leak-detection-riyadh-center/',
		'water-leak-detection-south-riyadh' => '/water-leak-detection-riyadh-center/',
		'water-leak-detection-west-riyadh' => '/water-leak-detection-riyadh-center/',
		'gypsum-tech-jeddah' => '/gypsum-board-jeddah/',
		'gypsum-board-decor-jeddah' => '/gypsum-board-jeddah/',
		'gypsum-tech-mecca' => '/gypsum-board-mecca/',
		'gypsum-board-decor-mecca' => '/gypsum-board-mecca/',
		'gypsum-tech-taif' => '/gypsum-board-taif/',
		'gypsum-board-decor-taif' => '/gypsum-board-taif/',
		'gypsum-board-decor-abha' => '/gypsum-board-abha/',
		'gypsum-tech-abha' => '/gypsum-board-abha/',
		'gypsum-tech-khobar' => '/gypsum-board-khobar/',
		'gypsum-board-decor-khobar' => '/gypsum-board-khobar/',
		'gypsum-tech-riyadh' => '/gypsum-board-riyadh/',
		'gypsum-board-decor-riyadh' => '/gypsum-board-riyadh/',
		'gypsum-tech-dammam' => '/gypsum-board-dammam/',
		'gypsum-board-decor-dammam' => '/gypsum-board-dammam/',
		'gypsum-tech-medina' => '/gypsum-board-medina/',
		'gypsum-board-decor-medina' => '/gypsum-board-medina/',
		'home-electrician-elec-jeddah' => '/home-electrician-jeddah/',
		'home-plumber-elec-mecca' => '/home-plumber-mecca/',
		'home-plumber-elec-jeddah' => '/home-plumber-jeddah/',
		'home-plumber-elec-taif' => '/home-plumber-taif/',
		'home-electrician-elec-medina' => '/home-electrician-medina/',
		'home-plumber-elec-riyadh' => '/home-plumber-riyadh/',
		'home-plumber-elec-abha' => '/home-plumber-abha/',
		'home-electrician-elec-mecca' => '/home-electrician-mecca/',
		'home-electrician-elec-taif' => '/home-electrician-taif/',
		'home-electrician-elec-abha' => '/home-electrician-abha/',
		'home-electrician-elec-khobar' => '/home-electrician-khobar/',
		'home-electrician-elec-riyadh' => '/home-electrician-riyadh/',
		'water-leak-detection-madinah' => '/water-leak-detection-medina/',
		'home-electrician-elec-dammam' => '/home-electrician-dammam/',
		'home-plumber-elec-khobar' => '/home-plumber-khobar/',
		'home-plumber-elec-dammam' => '/home-plumber-dammam/',
		'home-plumber-elec-medina' => '/home-plumber-medina/',
		'artificial-grass-grdn-medina' => '/wall-grass-medina/',
		'artificial-grass-grdn-khobar' => '/wall-grass-khobar/',
		'artificial-grass-grdn-mecca' => '/wall-grass-mecca/',
		'artificial-grass-grdn-abha' => '/wall-grass-abha/',
		'artificial-grass-grdn-taif' => '/wall-grass-taif/',
		'artificial-grass-grdn-jeddah' => '/wall-grass-jeddah/',
		'artificial-grass-grdn-riyadh' => '/wall-grass-riyadh/',
		'artificial-grass-grdn-dammam' => '/wall-grass-dammam/',
		'electric-panel-maintenance-dammam' => '/electrical-maintenance-dammam/',
		'electric-panel-maintenance-riyadh' => '/electrical-maintenance-riyadh/',
		'electric-panel-maintenance-mecca' => '/electrical-maintenance-mecca/',
		'modern-irrigation-taif' => '/automatic-irrigation-taif/',
		'modern-irrigation-mecca' => '/automatic-irrigation-mecca/',
		'contact' => '/contact-us/',
		'privacy' => '/privacy-policy/',
		'ac-cleaning-riyadh' => '/ac-cleaning-washing-riyadh/',
		'ac-maintenance-riyadh' => '/split-ac-maintenance-riyadh/',
		'category/home-cleaning' => '/category/house-cleaning/',
		'category/ac-maintenance' => '/category/split-air-conditioner-maintenance/',
	);
}

function rukn_sa_gsc_arabic_cities() {
	return array(
		'الرياض'           => 'riyadh',
		'جدة'              => 'jeddah',
		'مكه'              => 'makkah',
		'مكة'              => 'makkah',
		'مكة المكرمة'      => 'makkah',
		'المدينة'          => 'madinah',
		'المدينة المنورة'  => 'madinah',
		'المدينه'          => 'madinah',
		'الدمام'           => 'dammam',
		'الخبر'            => 'khobar',
		'الطائف'           => 'taif',
		'الطايف'           => 'taif',
		'أبها'             => 'abha',
		'ابها'             => 'abha',
		'تبوك'             => 'tabuk',
		'بريدة'            => 'buraidah',
		'بريده'            => 'buraidah',
		'خميس مشيط'        => 'khamis-mushait',
		'جازان'            => 'jazan',
		'جيزان'            => 'jazan',
		'الأحساء'          => 'ahsa',
		'الاحساء'          => 'ahsa',
		'حائل'             => 'hail',
		'حايل'             => 'hail',
		'ينبع'             => 'yanbu',
		'الجبيل'           => 'jubail',
	);
}

function rukn_sa_gsc_request_path() {
	$uri  = isset( $_SERVER['REQUEST_URI'] ) ? (string) $_SERVER['REQUEST_URI'] : '';
	$path = (string) wp_parse_url( $uri, PHP_URL_PATH );
	$path = preg_replace( '#^/sa(?=/|$)#', '', $path );
	$path = trim( rawurldecode( $path ), '/' );
	return $path;
}

function rukn_sa_gsc_start_sitemap_buffer() {
	static $started = false;
	if ( $started ) {
		return;
	}
	$started = true;
	ob_start(
		function ( $xml ) {
			if ( ! is_string( $xml ) || $xml === '' ) {
				return $xml;
			}
			return preg_replace(
				'#<url>\s*<loc>https://www\.rukn-eltatawer\.com/sa/en/?</loc>.*?</url>#s',
				'',
				$xml
			);
		}
	);
}

add_action(
	'init',
	function () {
		$uri  = isset( $_SERVER['REQUEST_URI'] ) ? (string) $_SERVER['REQUEST_URI'] : '';
		$path = (string) wp_parse_url( $uri, PHP_URL_PATH );
		if ( substr( $path, -4 ) === '.xml' && false !== strpos( $path, 'sitemap' ) ) {
			rukn_sa_gsc_start_sitemap_buffer();
		}
	},
	0
);

function rukn_sa_gsc_should_noindex() {
	$uri  = isset( $_SERVER['REQUEST_URI'] ) ? (string) $_SERVER['REQUEST_URI'] : '';
	$path = rukn_sa_gsc_request_path();
	if ( $path === 'en' || strpos( $path, 'en/' ) === 0 ) {
		return true;
	}
	if ( false !== strpos( $uri, '/en/' ) ) {
		return true;
	}
	if ( function_exists( 'pll_current_language' ) && 'en' === pll_current_language() ) {
		return true;
	}
	if ( function_exists( 'is_author' ) && is_author() ) {
		return true;
	}
	if ( function_exists( 'is_search' ) && is_search() ) {
		return true;
	}
	if ( function_exists( 'is_date' ) && is_date() ) {
		return true;
	}
	if ( function_exists( 'is_attachment' ) && is_attachment() ) {
		return true;
	}
	if ( function_exists( 'is_category' ) && is_category() ) {
		$term = get_queried_object();
		if ( $term && isset( $term->count ) && (int) $term->count === 0 ) {
			return true;
		}
	}
	return false;
}

add_action(
	'template_redirect',
	function () {
		if ( is_admin() ) {
			return;
		}

		$path = rukn_sa_gsc_request_path();
		$map  = rukn_sa_gsc_redirect_map();

		if ( substr( $path, -4 ) === '.xml' && false !== strpos( $path, 'sitemap' ) ) {
			rukn_sa_gsc_start_sitemap_buffer();
		}

		if ( isset( $_GET['p'] ) && (string) $_GET['p'] === '1' && $path === '' ) {
			wp_safe_redirect( home_url( '/' ), 301 );
			exit;
		}

		if ( preg_match( '#^page/(\d+)$#', $path, $m ) && (int) $m[1] >= 2 ) {
			wp_safe_redirect( home_url( '/' ), 301 );
			exit;
		}

		$cities = rukn_sa_gsc_arabic_cities();
		if ( preg_match( '#^(?:city|cities)/([^/]+)$#u', $path, $m ) ) {
			$raw = trim( rawurldecode( $m[1] ) );
			if ( isset( $cities[ $raw ] ) ) {
				wp_safe_redirect( home_url( '/cities/' . $cities[ $raw ] . '/' ), 301 );
				exit;
			}
		}

		if ( $path !== '' && isset( $map[ $path ] ) ) {
			wp_safe_redirect( home_url( $map[ $path ] ), 301 );
			exit;
		}

		if ( strpos( $path, 'en/' ) === 0 ) {
			$exists = url_to_postid( home_url( '/' . $path . '/' ) );
			if ( ! $exists ) {
				wp_safe_redirect( home_url( '/en/' ), 301 );
				exit;
			}
		}

		if ( rukn_sa_gsc_should_noindex() && ! headers_sent() ) {
			header( 'X-Robots-Tag: noindex, follow', true );
		}
	},
	-1
);

add_action(
	'wp_head',
	function () {
		if ( rukn_sa_gsc_should_noindex() ) {
			echo '<meta name="robots" content="noindex, follow" />' . "\n";
		}
	},
	1
);

add_filter(
	'rank_math/frontend/robots',
	function ( $robots ) {
		if ( ! is_array( $robots ) ) {
			$robots = array();
		}
		if ( rukn_sa_gsc_should_noindex() ) {
			$robots['index']  = 'noindex';
			$robots['follow'] = 'follow';
			unset( $robots['nofollow'] );
		}
		return $robots;
	},
	99
);

function rukn_sa_gsc_sitemap_loc( $url ) {
	if ( is_array( $url ) ) {
		return (string) ( $url['loc'] ?? '' );
	}
	return is_string( $url ) ? $url : '';
}

function rukn_sa_gsc_should_drop_sitemap_loc( $loc ) {
	if ( $loc === '' ) {
		return false;
	}
	$path = (string) wp_parse_url( $loc, PHP_URL_PATH );
	$path = preg_replace( '#^/sa(?=/|$)#', '', $path );
	$path = trim( (string) $path, '/' );
	if ( $path === 'en' || strpos( $path, 'en/' ) === 0 ) {
		return true;
	}
	$map = rukn_sa_gsc_redirect_map();
	if ( $path !== '' && isset( $map[ $path ] ) ) {
		return true;
	}
	return false;
}

add_filter(
	'rank_math/sitemap/entry',
	function ( $url, $type = '', $object = null ) {
		$loc = rukn_sa_gsc_sitemap_loc( $url );
		if ( rukn_sa_gsc_should_drop_sitemap_loc( $loc ) ) {
			return false;
		}
		return $url;
	},
	20,
	3
);

add_filter(
	'rank_math/sitemap/content',
	function ( $content ) {
		if ( ! is_string( $content ) || $content === '' ) {
			return $content;
		}
		$content = preg_replace(
			'#<url>\s*<loc>https://www\.rukn-eltatawer\.com/sa/en/?</loc>.*?</url>#s',
			'',
			$content
		);
		return $content;
	},
	99
);

function rukn_sa_gsc_apply_sitemap_settings() {
	$opt = get_option( 'rank-math-options-sitemap', array() );
	if ( ! is_array( $opt ) ) {
		$opt = array();
	}
	$before = $opt;
	$opt['pt_post_sitemap']       = 'on';
	$opt['pt_page_sitemap']       = 'on';
	$opt['authors_sitemap']       = 'off';
	$opt['pt_attachment_sitemap'] = 'off';
	update_option( 'rank-math-options-sitemap', $opt, false );

	$titles = get_option( 'rank-math-options-titles', array() );
	if ( is_array( $titles ) ) {
		$titles['author_custom_robots'] = 'on';
		$titles['author_robots']        = array( 'noindex' );
		$titles['pt_page_robots']       = array( 'index', 'follow' );
		update_option( 'rank-math-options-titles', $titles, false );
	}

	if ( function_exists( 'as_unschedule_all_actions' ) ) {
		as_unschedule_all_actions( 'rank_math/sitemap/generator' );
	}
	delete_transient( 'rank_math_sitemap_cache_index' );
	global $wpdb;
	$removed_files = array();
	$upload        = function_exists( 'wp_upload_dir' ) ? wp_upload_dir() : array();
	$dirs          = array();
	if ( ! empty( $upload['basedir'] ) ) {
		$dirs[] = $upload['basedir'] . '/rank-math';
		$dirs[] = $upload['basedir'] . '/rank-math/sitemap';
	}
	if ( defined( 'WP_CONTENT_DIR' ) ) {
		$dirs[] = WP_CONTENT_DIR . '/uploads/rank-math';
	}
	foreach ( $dirs as $dir ) {
		if ( ! is_dir( $dir ) ) {
			continue;
		}
		foreach ( glob( $dir . '/*.xml' ) ?: array() as $file ) {
			$removed_files[] = basename( $file );
			@unlink( $file );
		}
	}
	if ( isset( $wpdb ) ) {
		$wpdb->query(
			"DELETE FROM {$wpdb->options} WHERE option_name LIKE '\\_transient%rank_math%sitemap%' OR option_name LIKE '\\_transient_timeout%rank_math%sitemap%' OR option_name LIKE '\\_transient%rank-math-sitemap%' OR option_name LIKE '\\_transient_timeout%rank-math-sitemap%'"
		);
	}
	if ( function_exists( 'do_action' ) ) {
		do_action( 'rank_math/sitemap/invalidate' );
		do_action( 'litespeed_purge_all' );
		do_action( 'litespeed_purge_url', home_url( '/sitemap_index.xml' ) );
		do_action( 'litespeed_purge_url', home_url( '/page-sitemap.xml' ) );
		for ( $i = 1; $i <= 12; $i++ ) {
			do_action( 'litespeed_purge_url', home_url( '/post-sitemap' . $i . '.xml' ) );
		}
	}

	$related = array();
	foreach ( $opt as $k => $v ) {
		if ( false !== stripos( $k, 'pt_' ) || false !== stripos( $k, 'author' ) || false !== stripos( $k, 'page' ) ) {
			$related[ $k ] = $v;
		}
	}
	return array(
		'ok'            => true,
		'related'       => $related,
		'changed'       => $before !== $opt,
		'removed_files' => $removed_files,
	);
}

add_action(
	'rest_api_init',
	function () {
		$can = function () {
			return current_user_can( 'manage_options' );
		};
		register_rest_route(
			'rukn/v1',
			'/apply-gsc-fix',
			array(
				'methods'             => 'POST',
				'permission_callback' => $can,
				'callback'            => function () {
					$info = rukn_sa_gsc_apply_sitemap_settings();
					return rest_ensure_response( $info );
				},
			)
		);
	}
);
