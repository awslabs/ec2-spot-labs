/*############################################################################*/
/*                                                                            */
/*   Coauthors: Antoine Eddi (@antoeddi) & Philippe Desmaison (@desmaisn)     */
/*                                                                            */
/*   Team: EMEA Partner Solutions Architects                                  */
/*   Date: March 2016                                                         */
/*                                                                            */
/*############################################################################*/

var frontend = {

	loading: false,

	fill_infos_list: function(id, content, success)
	{
		var elem = jQuery('#' + id);

		elem.children('p').html(content);
		if (success) {
			elem.removeClass('disabled');
			collected[id] = content;
		}
	},

	update_progress_message: function(text, remove, slide)
	{
		jQuery('#dropcontainer h3').html(text);
		if (slide) {
			setTimeout(function() {
				jQuery('#carousel').carousel(1);
				setTimeout(function() {
					jQuery('#dropzone img').remove();
					jQuery('#dropzone').removeClass('dropped');
					if (collected.mobile === 'Yes') {
						jQuery('#dropcontainer h3').html('Touch here to upload a photo');
					}
					else {
						jQuery('#dropcontainer h3').html('Drop photo here to be mustached');
					}
				}, 500);
			}, 1000);
		}
		else if (remove) {
			jQuery('#dropzone img').remove();
			jQuery('#dropzone').removeClass('dropped');
		}
	},

	update_mustache_level: function(target)
	{
		var mustache_lvl = jQuery('#mustache p');
		var current = parseInt(mustache_lvl.html());

		current = (isNaN(current)) ? 0 : current;
		if (current > target) {
			current = 0;
		}
		if (current != target) {
			collected['mustache'] = target.toString();
			post_infos();
			jQuery({value: current}).animate({value: target}, {
				duration: (target - current) * 250,
				step: function() {
					mustache_lvl.html(Math.round(this.value));
				}
			});
		}
	},

	display_img_thumbnail: function(file)
	{
		var reader = new FileReader();

		frontend.update_progress_message('<i class="fa fa-spinner fa-pulse"></i>&nbsp; Uploading and processing...', true, false);
		reader.onload = function(event) {
			var dropzone = jQuery('#dropzone');
			var image = new Image();

			image.src = event.target.result;
			dropzone.append(image);
			dropzone.addClass('dropped');
		};
		reader.readAsDataURL(file);
	},

	add_img_to_list: function(image_src, from_dropzone, count)
	{
		var new_elem = jQuery('<div class="item"></div>');
		var image = jQuery('<img src="' + image_src + '">');
		var splits = image_src.split('/');
		var name = "mustached-" + splits[splits.length - 1];
		var link = jQuery('<a>').attr({
			'href': image_src,
			'download': name
		});

		image.on('load', function() {
			if (!this.complete || typeof this.naturalWidth == "undefined" || this.naturalWidth == 0) {
				console.error('Error: broken image');
				frontend.update_progress_message('Error: drop a new image to retry', true, false);
			}
			else {
				frontend.resize_carousel_img(image[0]);
				frontend.set_short_url(image);

				if (from_dropzone) {
					new_elem.insertAfter('#dropcontainer');
				}
				else {
					new_elem.insertAfter('.carousel-inner .item:last');
				}

				new_elem.append(link);
				link.append(image);
				frontend.update_carousel_buttons();

				if (from_dropzone) {
					frontend.update_progress_message('Done! You got mustached!', true, true);
					frontend.update_mustache_level(count);
				}
				else {
					frontend.loading = false;
				}
			}
		});
		image.on('error', function() {
			console.error('Error: downloading image');
			frontend.update_progress_message('Error: drop a new image to retry', true, false);
		});
	},

	display_images_list: function(list)
	{
		var base_url = window.location.href + 'image?filepath=' + collected.uuid + '/';
		var count = 0;

		function load_img_synchronously()
		{
			if (!frontend.loading) {
				frontend.loading = true;
				frontend.add_img_to_list(base_url + list[count], false, 0);
				count++;
			}
			if (count < list.length) {
				setTimeout(load_img_synchronously, 100);
			}
		}
		if (list && list.length) {
			load_img_synchronously();
		}
	},

	resize_carousel_img: function(image)
	{
		var ref_height = jQuery('.carousel-inner').height();
		var diff = ref_height * 5/100;

		image.width = image.naturalWidth;
		image.height = image.naturalHeight;
		image.style.marginTop = "0px";
		if (ref_height - diff < image.height) {
			image.width *= ((ref_height - diff) / image.height);
			image.height = ref_height - diff;
		}
		if (ref_height > image.height) {
			image.style.marginTop = ((ref_height - image.height) / 2) + "px";
		}
	},

	update_carousel_buttons: function()
	{
		var index_max = jQuery('.carousel-inner > div').size() - 1;
		var index_cur = jQuery('#carousel .active').index('#carousel .item');
		var add_butt = jQuery('#car-prev button').eq(0);
		var prev_butt = jQuery('#car-prev button').eq(1);
		var next_butt = jQuery('#car-next button').eq(0);

		if (index_cur == 0) {
			prev_butt.fadeOut(100);
			add_butt.fadeOut(100);
		}
		else if (index_cur == 1) {
			prev_butt.hide();
			add_butt.show();
		}
		else {
			add_butt.hide();
			prev_butt.show();
		}
		if (index_cur == index_max) {
			next_butt.fadeOut(100);
		}
		else {
			next_butt.fadeIn(100);
		}
	},

	update_share_buttons: function()
	{
		var social_buttons = jQuery('.ssk-group');
		var current_elem = jQuery('#carousel .active');

		if (current_elem.index('#carousel .item') === 0) {
			social_buttons.slideUp(300);
		}
		else {
			social_buttons.attr('data-url', current_elem.children('a').children('img').attr('short-url'));
			social_buttons.slideDown(500);
		}
	},

	set_short_url: function(image)
	{
		jQuery.ajax({
			type: 'GET',
			url: 'https://is.gd/create.php?format=json&url=' + encodeURIComponent(image.attr('src')),
			dataType: 'json',    
			success: function(data) {
				if (data.shorturl === undefined) {
					data.shorturl = image.attr('src');
				}
				image.attr('short-url', data.shorturl);
			},
			timeout: 20000
		});
	},

	geolocate_user: function() {
		if (navigator.geolocation) {
			navigator.geolocation.getCurrentPosition(
				function(pos) {
					frontend.fill_infos_list('gps', pos.coords.latitude + ', ' + pos.coords.longitude, true)
					get_location(pos.coords);
				},
				function(error) {
					console.error('Error getting position: ' + error.message);
					frontend.fill_infos_list('address', 'Unknown', false);
					frontend.fill_infos_list('gps', 'Unknown', false);
				}
			);
		}
		else { 
			frontend.fill_infos_list('address', 'Geolocation disabled in your browser', false);
			frontend.fill_infos_list('gps', 'Geolocation disabled in your browser', false);
		}
	},

	display_map: function(coords)
	{
		var map_display = jQuery('#map-display');
		var my_pos = {lat: coords.latitude, lng: coords.longitude};
		var map = new google.maps.Map(map_display[0], {
			center: my_pos,
			zoom: 15
		});
		var marker = new google.maps.Marker({
			position: my_pos,
			map: map,
			title: 'Your position'
		});
		var draw_map = function() {
			var map_width = jQuery('#gps p').width() - 20;
			var map_height = map_width * 10/16;

			map_display.width(map_width);
			map_display.height(map_height);
			google.maps.event.trigger(map, "resize");
			map.setZoom(map.getZoom());
			map.setCenter(my_pos);
		};

		jQuery(window).on('resize', draw_map);
		jQuery('#panel-element-location').on('show.bs.collapse', function() {
			setTimeout(draw_map, 200);
		});
		draw_map();
	},

	display_modal: function(title, body)
	{
		jQuery('h4.modal-title').text(title);
		jQuery('div.modal-body').text(body);
		jQuery('#modal').modal('show');
	},

	register_events: function()
	{
		var dropzone = jQuery('#dropzone');
		var carousel = jQuery('#carousel');
		var car_cont = jQuery('.carousel-inner');
		var car_prev = jQuery('#car-prev button');
		var car_next = jQuery('#car-next button');


		car_prev.click(function() {
			carousel.carousel('prev');
		});
		car_next.click(function() {
			carousel.carousel('next');
		});

		var car_set_size = function() {
			car_cont.height(car_cont.width() * 9/16);
			jQuery(".carousel-inner div img").each(function() {
				frontend.resize_carousel_img(jQuery(this)[0]);
			});
		};
		car_set_size();

		jQuery(window).on('resize', car_set_size);
		carousel.on('slid.bs.carousel', function() {
			frontend.update_carousel_buttons();
			frontend.update_share_buttons();
		});

		jQuery(document).on('dragenter dragleave drop', function(event) {
			event.preventDefault();
		});
		jQuery(document).on('dragover', function(event) {
			event.preventDefault();
			carousel.carousel(0);
		});
		jQuery(document).keyup(function(event) {
			if(event.which == 39){
				event.preventDefault();
				carousel.carousel('next');
			}
			else if(event.which == 37){
				event.preventDefault();
				carousel.carousel('prev');
			}
		});
		dropzone[0].addEventListener('dragover', function(event) {
			event.dataTransfer.dropEffect = 'copy';
			event.preventDefault();
			event.stopPropagation();
			if (!dropzone.hasClass('hovered')) {
				dropzone.addClass('hovered');
			}
		}, false);
		dropzone[0].addEventListener('dragleave', function(event) {
			event.preventDefault();
			if (dropzone.hasClass('hovered')) {
				dropzone.removeClass('hovered');
			}
		}, false);
		dropzone[0].addEventListener('drop', function(event) {
			event.preventDefault();
			if (dropzone.hasClass('hovered')) {
				dropzone.removeClass('hovered');
			}
			handle_added_files(event.dataTransfer.files);
		}, false);
		dropzone.click(function() {
			jQuery('#file-input').click();
		});
	},

	init_frontend: function()
	{
		window.addEventListener('DOMContentLoaded', function() {
			SocialShareKit.init();
			setTimeout(function() {
				if (collected.mobile === 'Yes') {
					jQuery('#dropzone').addClass('mobile');
					jQuery('#dropcontainer h3').html('Touch here to upload a photo');
				}
				else {
					jQuery('#dropcontainer h3').html('Drop photo here to be mustached');
				}
				jQuery('#page-loader').fadeOut(420);
			}, 420);

			frontend.fill_infos_list('os', infos.os + ' ' + infos.osVersion, true);
			frontend.fill_infos_list('browser', infos.browser + ' ' + infos.browserMajorVersion + ' (' + infos.browserVersion + ')', true);
			frontend.fill_infos_list('mobile', infos.mobile, true);
			frontend.fill_infos_list('cookies', infos.cookies, true);
			frontend.fill_infos_list('screen', infos.screen, true);
			frontend.fill_infos_list('time', infos.time.toGMTString(), true);
			get_public_ip();
			get_instance_metadata();
			frontend.geolocate_user();
		});

		frontend.register_events();
	}
};
