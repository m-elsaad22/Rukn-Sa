/**
 * Rukn SA frontend repair: UAE WhatsApp only, hide call, strip leftover UAE copy.
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

add_filter(
	'register_post_type_args',
	function ( $args, $post_type ) {
		if ( in_array( $post_type, array( 'services', 'pricing', 'reviews', 'faqs', 'portfolio', 'before_after' ), true ) ) {
			$args['has_archive'] = false;
		}
		return $args;
	},
	20,
	2
);

add_action(
	'init',
	function () {
		if ( get_option( 'rukn_sa_rewrites_flushed_v3' ) ) {
			return;
		}
		flush_rewrite_rules( false );
		update_option( 'rukn_sa_rewrites_flushed_v3', 1, false );
	},
	99
);

add_action(
	'init',
	function () {
		if ( get_option( 'rukn_sa_terms_cleaned_v4' ) ) {
			return;
		}
		if ( ! taxonomy_exists( 'category' ) ) {
			return;
		}
		$terms = get_terms(
			array(
				'taxonomy'   => 'category',
				'hide_empty' => false,
			)
		);
		if ( is_wp_error( $terms ) || empty( $terms ) ) {
			update_option( 'rukn_sa_terms_cleaned_v4', 1, false );
			return;
		}
		foreach ( $terms as $t ) {
			$desc = rukn_sa_replace_geo( (string) $t->description );
			$name = rukn_sa_replace_geo( (string) $t->name );
			$args = array();
			if ( $desc !== $t->description ) {
				$args['description'] = $desc;
			}
			if ( $name !== $t->name ) {
				$args['name'] = $name;
			}
			if ( $args ) {
				wp_update_term( (int) $t->term_id, 'category', $args );
			}
			foreach ( array( 'rank_math_title', 'rank_math_description', 'rank_math_facebook_description' ) as $mk ) {
				$val = get_term_meta( $t->term_id, $mk, true );
				if ( is_string( $val ) && $val !== '' ) {
					$nv = rukn_sa_replace_geo( $val );
					if ( $nv !== $val ) {
						update_term_meta( $t->term_id, $mk, $nv );
					}
				}
			}
		}
		update_option( 'rukn_sa_terms_cleaned_v4', 1, false );
	},
	20
);

function rukn_sa_replace_geo( $html ) {
	$map = array(
		'في السعودية في السعودية'                 => 'في السعودية',
		'خريطة الإمارات'                           => 'خريطة السعودية',
		'خدمات المنزلية في الإمارات'               => 'خدمات المنزلية في السعودية',
		'للخدمات المنزلية في الإمارات'             => 'للخدمات المنزلية في السعودية',
		'كشف تسربات المياه في الإمارات'            => 'كشف تسربات المياه في السعودية',
		'كشف تسربات المياه وعزل الأسطح في الإمارات' => 'كشف تسربات المياه وعزل الأسطح في السعودية',
		'تسليك مجاري في الإمارات'                  => 'تسليك المجاري في السعودية',
		'تسليك مجاري في الامارات'                  => 'تسليك المجاري في السعودية',
		'شركة نقل أثاث وتخزين في الإمارات'         => 'شركة نقل أثاث وتخزين في السعودية',
		'نصلك في أي مكان في الإمارات'              => 'نصلك في أي مكان في السعودية',
		'جميع مدن الإمارات، بما في ذلك دبي، أبوظبي، الشارقة، العين، عجمان، رأس الخيمة، الفجيرة، وأم القيوين' => 'مدن المملكة، بما في ذلك الرياض وجدة ومكة والمدينة والدمام والخبر والجبيل والأحساء والطائف وأبها',
		'دولة الإمارات العربية المتحدة'            => 'المملكة العربية السعودية',
		'في الإمارات،'                             => 'في السعودية،',
		'في الامارات'                              => 'في السعودية',
		'في الإمارات'                              => 'في السعودية',
		'مدن الإمارات'                             => 'مدن المملكة',
		'خبرة 12 عاماً في الإمارات'                => 'خبرة أكثر من 10 أعوام في السعودية',
		'خبرة 12 عامًا في الإمارات'                => 'خبرة أكثر من 10 أعوام في السعودية',
		'الإمارات 🇦🇪'                            => 'السعودية 🇸🇦',
		'🇦🇪'                                      => '🇸🇦',
		'RuknEltatwer'                             => 'RuknEltatawer',
	);
	return strtr( $html, $map );
}

function rukn_sa_rewrite_html( $html ) {
	if ( ! is_string( $html ) || $html === '' ) {
		return $html;
	}
	$wa = '971586634710';

	$html = preg_replace( '#href="\[https://wa\.me/[^\]]+\]\([^"]+\)"#i', 'href="https://wa.me/' . $wa . '"', $html );
	$html = preg_replace( '#https?://wa\.me/\+?(?:966000000000|966568060309|971588634710|971586634710)#i', 'https://wa.me/' . $wa, $html );
	$html = preg_replace( '#href="tel:[^"]+"#i', 'href="https://wa.me/' . $wa . '" data-rukn-cta="whatsapp"', $html );
	$html = preg_replace( '#href=&quot;tel:[^&]*&quot;#i', 'href="https://wa.me/' . $wa . '"', $html );
	$html = str_replace( array( 'tel:0568060309', 'tel:+966568060309', 'tel:+966000000000' ), 'https://wa.me/' . $wa, $html );

	$html = preg_replace(
		'/window\.RuknCS=\{[^}]*\}/',
		'window.RuknCS={"call_show":false,"wa_show":true,"call_number":"","wa_number":"' . $wa . '","wa_message":"مرحباً! شركة ركن التطور - السعودية"}',
		$html
	);

	$html = strtr(
		$html,
		array(
			'+201556644443' => '+' . $wa,
			'201556644443'  => $wa,
			'01556644443'   => $wa,
			'+201151481000' => '+' . $wa,
			'201151481000'  => $wa,
			'+966000000000' => '+' . $wa,
			'966000000000'  => $wa,
			'+966568060309' => '+' . $wa,
			'966568060309'  => $wa,
		)
	);

	$html = rukn_sa_replace_geo( $html );
	$html = str_replace( 'https://www.rukn-eltatawer.com/sa/sa/', 'https://www.rukn-eltatawer.com/sa/', $html );
	$html = str_replace( array( 'class="uae-svg"', 'uae-svg' ), array( 'class="ksa-svg"', 'ksa-svg' ), $html );
	$html = preg_replace( '#<span class="eztoc-hide"[^>]*>Toggle</span>#i', '', $html );
	$html = str_replace( 'data-count="20"', 'data-count="12"', $html );
	$html = preg_replace( '/(<(?:b|div)[^>]*data-count="(\d+)"[^>]*>)0(<\/(?:b|div)>)/', '$1$2$3', $html );
	$html = str_replace( 'شركة كيان ويب للتسويق الإلكتروني', 'شركة ركن التطور', $html );

	$css = '<style id="rukn-sa-hide-call">
a[href^="tel:"],.--MH--header-contact--,.fab-stack a[href^="tel:"],.call-float,.call-btn,[data-button="call"],header .icon-btn[aria-label*="اتصال"],header a[href^="tel:"],a[data-rukn-cta="whatsapp"]:has(.fa-phone-volume),a[data-rukn-cta="whatsapp"]:has(.fa-phone){display:none!important}
.lang-item,.pll-parent-menu-item,ul.sub-menu .lang-item{display:none!important}
</style>';
	if ( false === strpos( $html, 'rukn-sa-hide-call' ) ) {
		$html = str_replace( '</head>', $css . '</head>', $html );
	}
	return $html;
}

add_action(
	'template_redirect',
	function () {
		if ( is_admin() ) {
			return;
		}
		ob_start( 'rukn_sa_rewrite_html' );
	},
	0
);

add_action(
	'wp_head',
	function () {
		echo '<style id="rukn-sa-hide-call-early">a[href^="tel:"],.--MH--header-contact--{display:none!important}</style>';
	},
	1
);

add_filter(
	'rank_math/json_ld',
	function ( $data, $jsonld ) {
		if ( empty( $data ) || ! is_array( $data ) ) {
			return $data;
		}
		foreach ( $data as $key => $piece ) {
			if ( ! is_array( $piece ) ) {
				continue;
			}
			if ( isset( $piece['url'] ) && is_string( $piece['url'] ) ) {
				$data[ $key ]['url'] = str_replace( 'https://www.rukn-eltatawer.com/sa/sa/', 'https://www.rukn-eltatawer.com/sa/', $piece['url'] );
			}
			if ( isset( $piece['@id'] ) && is_string( $piece['@id'] ) ) {
				$data[ $key ]['@id'] = str_replace( 'https://www.rukn-eltatawer.com/sa/sa/', 'https://www.rukn-eltatawer.com/sa/', $piece['@id'] );
			}
			$types = isset( $piece['@type'] ) ? (array) $piece['@type'] : array();
			$biz   = array( 'Organization', 'LocalBusiness', 'HomeAndConstructionBusiness' );
			if ( array_intersect( $types, $biz ) || ( isset( $piece['@id'] ) && false !== strpos( (string) $piece['@id'], '#organization' ) ) ) {
				unset( $data[ $key ]['telephone'] );
				$data[ $key ]['areaServed'] = array( '@type' => 'Country', 'name' => 'Saudi Arabia' );
			}
		}
		return $data;
	},
	100,
	2
);

add_filter(
	'rest_post_dispatch',
	function ( $result, $server, $request ) {
		if ( ! $request instanceof WP_REST_Request ) {
			return $result;
		}
		if ( '/kayan/v1/dni' !== $request->get_route() ) {
			return $result;
		}
		$data = $result->get_data();
		if ( is_array( $data ) ) {
			$data['phone']     = '';
			$data['wa_number'] = '971586634710';
			$result->set_data( $data );
		}
		return $result;
	},
	10,
	3
);
