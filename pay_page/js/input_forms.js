var active_tab = '#pay-tab';
var active_tab_small = '#any-bank-tab';

$(document).ready(function(){
	$(".tab-link").click(function() {
		var tabclass = this.className.split(' ');
		if (~tabclass.indexOf('as-button')) {
			$(active_tab_small).css("box-shadow", "");
			$(this).css("box-shadow", "0 0 2px black");
			active_tab_small = this;
		} else {
			$(active_tab).css("background-color", "");
			$(this).css("background-color", "lightgreen");
			active_tab = this;
		}
		$(".bank-form").hide();
		switch(this.id) {
			case 'pay-tab':
				$(".as-button").show();
				$('#'+active_tab_small.id.slice(0, active_tab_small.id.lastIndexOf("-"))).show();
				break;
				
			case 'payment-request-tab':
				$(".as-button").hide();
				break;
				
			case 'any-bank-tab':
				$("#any-bank").show();
				break;
				
			case 'your-bank-tab':
				$("#your-bank").show();
				break;
		}
	});
});