
if ( ! defined( 'ABSPATH' ) ) { return; }

add_action( 'rest_api_init', function () {
	$can = function () { return current_user_can( 'manage_options' ); };

	register_rest_route( 'rukn/v1', '/fix-site-identity', array(
		'methods'             => 'POST',
		'permission_callback' => $can,
		'callback'            => function ( WP_REST_Request $req ) {
			$phone_local = '0568060309';
			$phone_intl  = '+966568060309';
			$phone_wa    = '966568060309';
			$geo         = '24.7136, 46.6753'; // Riyadh
			$report      = array();

			// 1) Rank Math titles / Local SEO / homepage
			$titles = get_option( 'rank-math-options-titles', array() );
			if ( ! is_array( $titles ) ) { $titles = array(); }
			$before = array(
				'geo' => $titles['geo'] ?? null,
				'pt_post_title' => $titles['pt_post_title'] ?? null,
				'homepage_title' => $titles['homepage_title'] ?? null,
				'phone_numbers' => $titles['phone_numbers'] ?? null,
			);

			$titles['geo'] = $geo;
			$titles['pt_post_title'] = '%title% %sep% %sitename%';
			$titles['pt_post_default_snippet_name'] = '%title%';
			$titles['phone_numbers'] = array(
				array( 'type' => 'customer support', 'number' => $phone_local ),
			);
			$titles['local_address'] = array(
				'streetAddress'   => 'حي النسيم',
				'addressLocality' => 'الرياض',
				'addressRegion'   => 'الرياض',
				'postalCode'      => '11461',
				'addressCountry'  => 'SA',
			);
			$titles['homepage_title'] = 'شركة ركن التطور | صيانة عامة وكشف تسربات المياه والعزل في السعودية';
			$titles['homepage_description'] = 'شركة ركن التطور للصيانة العامة والخدمات المتكاملة في السعودية، متخصصة في كشف تسربات المياه، العزل، صيانة المباني والمكيفات، والتنظيف. خدمة 24 ساعة، سرعة تنفيذ، وأسعار تنافسية. اتصل الآن: 0568060309.';
			$titles['homepage_facebook_title'] = 'شركة ركن التطور – صيانة عامة وخدمات متكاملة في السعودية';
			$titles['homepage_facebook_description'] = 'نقدم خدمات الصيانة العامة، كشف تسربات المياه، العزل، والتنظيف في جميع أنحاء السعودية. تواصل معنا الآن على 0568060309.';
			$titles['organization_description'] = "شركة ركن التطور للخدمات المتكاملة في المملكة العربية السعودية، متخصصة في كشف تسربات المياه، الصيانة العامة، العزل، والتنظيف، باستخدام أحدث الأجهزة وبدون تكسير.\nنغطي جميع مناطق السعودية مع خدمة 24 ساعة، سرعة تنفيذ، وأسعار تنافسية.";
			$titles['url'] = 'https://www.rukn-eltatawer.com/sa';
			$titles['knowledgegraph_name'] = 'شركة ركن التطور';
			$titles['local_business_type'] = 'HomeAndConstructionBusiness';
			$titles['local_seo'] = true;

			update_option( 'rank-math-options-titles', $titles, false );
			$report['rank_math_titles'] = array( 'before' => $before, 'after_geo' => $titles['geo'], 'after_pt_post_title' => $titles['pt_post_title'] );

			// 2) Theme contact options
			$simple_opts = array(
				'whatsapp_number' => $phone_intl,
				'phone'           => $phone_local,
				'whatsapp'        => $phone_intl,
				'info_contact'    => $phone_local,
				'phonenumber'     => $phone_local,
			);
			foreach ( $simple_opts as $k => $v ) {
				$old = get_option( $k );
				update_option( $k, $v, false );
				$report['options'][ $k ] = array( 'old' => $old, 'new' => $v );
			}

			// price whatsapp
			$price = get_option( 'price__option_data', array() );
			if ( ! is_array( $price ) ) { $price = array(); }
			$price['price__mode'] = 'watshapp';
			$price['watshapp'] = array( 'watshapp' => $phone_intl );
			update_option( 'price__option_data', $price, false );
			$report['price__option_data'] = $price;

			$btn = get_option( 'price__button__text', '' );
			$btn_new = 'احجز خطتك الآن مع ركن التطور! تواصل معنا على واتساب مباشرة للحصول على عرض سعر فوري لجميع خدمات الصيانة العامة والخدمات المنزلية. رابط واتساب: https://wa.me/' . $phone_wa;
			update_option( 'price__button__text', $btn_new, false );
			$report['price__button__text'] = array( 'old' => mb_substr( (string) $btn, 0, 120 ), 'new' => $btn_new );

			// Call Now Button plugin
			$cnb = get_option( 'cnb', array() );
			if ( is_array( $cnb ) ) {
				$cnb['number'] = $phone_intl;
				$cnb['active'] = isset( $cnb['active'] ) ? $cnb['active'] : '1';
				update_option( 'cnb', $cnb, false );
				$report['cnb'] = $cnb['number'];
			}

			// YourColor LocalBusiness schema
			$biz = get_option( 'YourColor_Schema_business', array() );
			if ( ! is_array( $biz ) ) { $biz = array(); }
			$biz['Business_Name'] = $biz['Business_Name'] ?? 'ركن التطور';
			$biz['Street_Address'] = $biz['Street_Address'] ?: 'حي النسيم';
			$biz['Country'] = 'SA';
			$biz['City'] = 'Riyadh';
			$biz['State'] = 'Riyadh';
			$biz['Postal_Code'] = $biz['Postal_Code'] ?: '11461';
			$biz['telephone'] = $phone_local;
			$biz['Price_Range'] = 'SAR';
			update_option( 'YourColor_Schema_business', $biz, false );
			$report['YourColor_Schema_business_telephone'] = $biz['telephone'];

			// Optional: clear LiteSpeed cache if available
			if ( class_exists( 'LiteSpeed\Purge' ) ) {
				try { \LiteSpeed\Purge::purge_all(); $report['cache'] = 'litespeed_purged'; } catch ( Exception $e ) { $report['cache'] = $e->getMessage(); }
			} elseif ( function_exists( 'do_action' ) ) {
				do_action( 'litespeed_purge_all' );
				$report['cache'] = 'litespeed_purge_all_action';
			}

			return rest_ensure_response( array( 'ok' => true, 'report' => $report ) );
		},
	) );
} );
