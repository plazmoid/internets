$(document).ready(function(){
	$("#show-login").click(function(){
		$("#login").attr("style", "display:block");
	});
});

function validate_pwd() {
	var pass = $('#admin-pass').val();
	if (pass.length > 0) {
		var xmlhttp = new XMLHttpRequest();
		xmlhttp.onreadystatechange = function() {
			if(this.readyState == 4 && this.status == 200) {
				if(this.responseText == '1') {
					window.location = 'observer.php';
				}
				else {
					$('#response').html('Неверный пароль' + this.responseText);
				}
			}
		}
		xmlhttp.open("GET", "/observer.php?h="+pass, true);
		xmlhttp.send();
	}
}