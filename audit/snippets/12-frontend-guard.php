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
		if ( get_option( 'rukn_sa_rewrites_flushed_v5' ) ) {
			return;
		}
		flush_rewrite_rules( false );
		update_option( 'rukn_sa_rewrites_flushed_v5', 1, false );
	},
	99
);

add_action(
	'init',
	function () {
		if ( get_option( 'rukn_sa_terms_cleaned_v5' ) ) {
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
			update_option( 'rukn_sa_terms_cleaned_v5', 1, false );
			return;
		}
		foreach ( $terms as $t ) {
			$desc = rukn_sa_replace_geo( (string) $t->description );
			$name = rukn_sa_strip_emoji( rukn_sa_replace_geo( (string) $t->name ) );
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
					$nv = str_replace( array( '♻', '♻️' ), '', $nv );
					if ( $nv !== $val ) {
						update_term_meta( $t->term_id, $mk, $nv );
					}
				}
			}
		}
		update_option( 'rukn_sa_terms_cleaned_v5', 1, false );
	},
	20
);

function rukn_sa_strip_emoji( $text ) {
	$text = preg_replace( '/[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}\x{FE0F}]/u', '', $text );
	return trim( preg_replace( '/\s{2,}/u', ' ', $text ) );
}

function rukn_sa_replace_geo( $html ) {
	if ( ! is_string( $html ) || $html === '' ) {
		return $html;
	}
	$map = array(
		'في السعودية في السعودية'                   => 'في السعودية',
		'خريطة الإمارات'                             => 'خريطة السعودية',
		'خدمات المنزلية في الإمارات'                 => 'خدمات المنزلية في السعودية',
		'للخدمات المنزلية في الإمارات'               => 'للخدمات المنزلية في السعودية',
		'كشف تسربات المياه في الإمارات'              => 'كشف تسربات المياه في السعودية',
		'كشف تسربات المياه وعزل الأسطح في الإمارات'   => 'كشف تسربات المياه وعزل الأسطح في السعودية',
		'تسليك مجاري في الإمارات'                    => 'تسليك المجاري في السعودية',
		'تسليك مجاري في الامارات'                    => 'تسليك المجاري في السعودية',
		'شركة نقل أثاث وتخزين في الإمارات'           => 'شركة نقل أثاث وتخزين في السعودية',
		'نصلك في أي مكان في الإمارات'                => 'نصلك في أي مكان في السعودية',
		'جميع مدن الإمارات، بما في ذلك دبي، أبوظبي، الشارقة، العين، عجمان، رأس الخيمة، الفجيرة، وأم القيوين' => 'مدن المملكة، بما في ذلك الرياض وجدة ومكة والمدينة والدمام والخبر والجبيل والأحساء والطائف وأبها',
		'تغطي خدماتنا جميع إمارات الدولة، بدءًا من أبوظبي ودبي، وصولًا إلى الشارقة وعجمان، وأم القيوين، ورأس الخيمة، والفجيرة.' => 'تغطي خدماتنا مدن المملكة بما في ذلك الرياض وجدة ومكة والمدينة والدمام والخبر والطائف وأبها.',
		'دولة الإمارات العربية المتحدة'              => 'المملكة العربية السعودية',
		'داخل الإمارات'                              => 'داخل السعودية',
		'في الإمارات،'                               => 'في السعودية،',
		'في الامارات'                                => 'في السعودية',
		'في الإمارات'                                => 'في السعودية',
		'مدن الإمارات'                               => 'مدن المملكة',
		'إمارات الدولة'                              => 'مدن المملكة',
		'جميع إمارات الدولة السبع'                   => 'مدن المملكة',
		'خبرة 12 عاماً في الإمارات'                  => 'خبرة أكثر من 10 أعوام في السعودية',
		'خبرة 12 عامًا في الإمارات'                  => 'خبرة أكثر من 10 أعوام في السعودية',
		'الإمارات 🇦🇪'                              => 'السعودية 🇸🇦',
		'دبي، الإمارات العربية المتحدة'              => 'الرياض، المملكة العربية السعودية',
		'مقرنا الرئيسي'                              => 'مقرنا الرئيسي',
		'بلدية دبي وباقي الإمارات'                   => 'الجهات المختصة في السعودية',
		'RuknEltatwer'                               => 'RuknEltatawer',
	);
	$html = strtr( $html, $map );
	$html = preg_replace( '/أبوظبي:\s*محمد بن زايد، خليفة، شخبوط، بني ياس، الشهامة/u', '', $html );
	$html = preg_replace( '/دبي:\s*وسط المدينة، مردف، البرشاء، ديرة، الجميرا/u', '', $html );
	$html = preg_replace( '/باقي الإمارات:\s*العين، الشارقة، رأس الخيمة، الفجيرة، عجمان، أم القيوين/u', '', $html );
	$html = preg_replace( '/\+?971568060309/u', '971586634710', $html );
	$html = preg_replace( '/خصم\s*15%\s*على أول طلب[^\n<]*/u', '', $html );
	$html = preg_replace( '/حماية 100%\s*ضد الخدش/u', 'تغليف يحمي القطع أثناء النقل', $html );
	return $html;
}

function rukn_sa_rewrite_html( $html ) {
	if ( ! is_string( $html ) || $html === '' ) {
		return $html;
	}
	$wa = '971586634710';

	$html = preg_replace( '#href="\[https://wa\.me/[^\]]+\]\([^"]+\)"#i', 'href="https://wa.me/' . $wa . '"', $html );
	$html = preg_replace( '#https?://wa\.me/\+?(?:966000000000|966568060309|971588634710|971568060309|971586634710)#i', 'https://wa.me/' . $wa, $html );
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

	$html = str_replace( 'اتصل الآن 0568060309', 'تواصل عبر واتساب', $html );
	$html = str_replace( 'تواصل على 0568060309', 'تواصل عبر واتساب', $html );
	$html = str_replace( 'راسلنا على 0568060309', 'راسلنا عبر واتساب', $html );
	$html = preg_replace( '/على 0568060309/', 'عبر واتساب', $html );
	$html = preg_replace( '/0568060309/', '', $html );
	$html = preg_replace( '/"telephone"\s*:\s*"\s*"/', '"telephone":""', $html );

	$html = rukn_sa_replace_geo( $html );
	$html = str_replace( 'https://www.rukn-eltatawer.com/sa/sa/', 'https://www.rukn-eltatawer.com/sa/', $html );
	$html = str_replace( array( 'class="uae-svg"', 'uae-svg' ), array( 'class="ksa-svg"', 'ksa-svg' ), $html );
	$html = str_replace( 'roof-insulation-ae.webp', 'roof-insulation-a.webp', $html );
	$html = preg_replace( '#<span class="eztoc-hide"[^>]*>Toggle</span>#i', '', $html );
	$html = str_replace( 'data-count="20"', 'data-count="12"', $html );
	$html = preg_replace( '/(<(?:b|div)[^>]*data-count="(\d+)"[^>]*>)0(<\/(?:b|div)>)/', '$1$2$3', $html );
	$html = str_replace( 'شركة كيان ويب للتسويق الإلكتروني', 'شركة ركن التطور', $html );

	$html = str_replace( '"currency":"AED"', '"currency":"SAR"', $html );
	$html = str_replace( "'currency':'AED'", "'currency':'SAR'", $html );
	$html = str_replace( 'data-currency="AED"', 'data-currency="SAR"', $html );
	$html = str_replace( '"taxRate":"5"', '"taxRate":"15"', $html );
	$html = str_replace( "'taxRate':'5'", "'taxRate':'15'", $html );
	$html = str_replace( '199 ريال', 'يُحدد بعد المعاينة', $html );
	$html = str_replace( '349 ريال', 'يُحدد بعد المعاينة', $html );
	$html = preg_replace( '/data-amount="(?:199|349)"/', 'data-amount=""', $html );

	$html = preg_replace( '/(data-country="ae"[^>]*>[\s\S]{0,180}ksw-btn-flag[^>]*>)🇸🇦(<\/span>)/u', '${1}🇦🇪${2}', $html );

	$html = str_replace( array( '♻ ', '♻', '♻️' ), array( '', '', '' ), $html );

	$html = preg_replace( '/,"aggregateRating"\s*:\s*\{[^}]*"ratingCount"\s*:\s*"16948"[^}]*\}/s', '', $html );
	$html = preg_replace( '/,"aggregateRating"\s*:\s*\{[^}]*"reviewCount"\s*:\s*"6481"[^}]*\}/s', '', $html );
	$html = preg_replace( '/"aggregateRating"\s*:\s*\{[^}]*"ratingCount"\s*:\s*"16948"[^}]*\},?/s', '', $html );
	$html = preg_replace( '/"aggregateRating"\s*:\s*\{[^}]*"reviewCount"\s*:\s*"6481"[^}]*\},?/s', '', $html );

	$html = preg_replace( '#<div[^>]*>\s*<img[^>]*img\.youtube\.com/vi/الفيديو/[^>]*>[\s\S]{0,200}?</div>#u', '', $html );

	if ( false === stripos( $html, '<title' ) && false !== stripos( $html, '</head>' ) ) {
		$title = function_exists( 'wp_get_document_title' ) ? wp_get_document_title() : get_bloginfo( 'name' );
		$title = str_replace( array( '♻', '♻️' ), '', $title );
		$meta  = '<title>' . esc_html( $title ) . '</title>';
		$meta .= '<meta property="og:title" content="' . esc_attr( $title ) . '" />';
		$html  = preg_replace( '/<\/head>/i', $meta . '</head>', $html, 1 );
	}

	$css = '<style id="rukn-sa-hide-call">
a[href^="tel:"],.--MH--header-contact--,.fab-stack a[href^="tel:"],.call-float,.call-btn,[data-button="call"],header .icon-btn[aria-label*="اتصال"],header a[href^="tel:"],a[data-rukn-cta="whatsapp"]:has(.fa-phone-volume),a[data-rukn-cta="whatsapp"]:has(.fa-phone){display:none!important}
.lang-item,.pll-parent-menu-item,ul.sub-menu .lang-item{display:none!important}
input,textarea,select{text-transform:none!important}
[data-loader-src*="الفيديو"],.video-box:has([data-loader-src*="الفيديو"]){display:none!important}
</style>';
	if ( false === strpos( $html, 'rukn-sa-hide-call' ) ) {
		$html = str_replace( '</head>', $css . '</head>', $html );
	} elseif ( false === strpos( $html, 'text-transform:none' ) ) {
		$html = str_replace( '</style>', "input,textarea,select{text-transform:none!important}\n[data-loader-src*=\"الفيديو\"],.video-box:has([data-loader-src*=\"الفيديو\"]){display:none!important}\n</style>", $html );
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
		echo '<style id="rukn-sa-hide-call-early">a[href^="tel:"],.--MH--header-contact--{display:none!important}input,textarea,select{text-transform:none!important}</style>';
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
			if ( isset( $piece['aggregateRating'] ) && is_array( $piece['aggregateRating'] ) ) {
				$count = (string) ( $piece['aggregateRating']['ratingCount'] ?? $piece['aggregateRating']['reviewCount'] ?? '' );
				if ( in_array( $count, array( '16948', '6481' ), true ) ) {
					unset( $data[ $key ]['aggregateRating'] );
				}
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
