<?php
/**
 * Expose Kayan/YourColor article block meta to REST for posts, services, and pages.
 */
if ( ! defined( 'ABSPATH' ) ) {
	return;
}

add_action(
	'init',
	function () {
		$auth = function () {
			return current_user_can( 'edit_posts' );
		};

		$object_schema = array(
			'type'                 => 'object',
			'additionalProperties' => true,
		);
		$array_schema  = array(
			'type'  => 'array',
			'items' => array(
				'type'                 => 'object',
				'additionalProperties' => true,
			),
		);

		$keys_object = array(
			'post__features__data',
			'post__work_steps__data',
			'post__services__data',
			'post__price_list__data',
			'post__call_section__data',
			'post__card__data',
			'post__popover__data',
			'post__service_request__data',
			'YourColor_ImageObject',
			'YourColor_Service',
			'YourColor_Article',
			'YourColor__Rating',
			'defualt__rating',
			'post_gallery',
		);

		$keys_array = array(
			'yourcolor__faqs',
			'Pages__List__URL',
		);

		$keys_string = array(
			'phone_number',
			'whatsapp_number',
			'title_post_gallery',
			'content_post_gallery',
			'articon',
			'references',
			'VideoID',
			'cover',
		);

		$keys_booleanish = array(
			'hide_features__section',
			'hide_work_steps',
			'hide_services_section',
			'hide_price_list__section',
			'hide_post_gallery',
			'hide_call_section',
			'hide__post_card',
			'hide__single__popover',
			'hide__sidebar__service_request',
			'pin',
		);

		$types = array( 'post', 'services', 'page' );

		foreach ( $types as $type ) {
			foreach ( $keys_object as $key ) {
				register_post_meta(
					$type,
					$key,
					array(
						'type'          => 'object',
						'single'        => true,
						'show_in_rest'  => array( 'schema' => $object_schema ),
						'auth_callback' => $auth,
					)
				);
			}
			foreach ( $keys_array as $key ) {
				register_post_meta(
					$type,
					$key,
					array(
						'type'          => 'array',
						'single'        => true,
						'show_in_rest'  => array( 'schema' => $array_schema ),
						'auth_callback' => $auth,
					)
				);
			}
			foreach ( $keys_string as $key ) {
				register_post_meta(
					$type,
					$key,
					array(
						'type'          => 'string',
						'single'        => true,
						'show_in_rest'  => true,
						'auth_callback' => $auth,
					)
				);
			}
			foreach ( $keys_booleanish as $key ) {
				register_post_meta(
					$type,
					$key,
					array(
						'type'          => 'string',
						'single'        => true,
						'show_in_rest'  => true,
						'auth_callback' => $auth,
					)
				);
			}
		}
	},
	20
);
