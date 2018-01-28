var last_active_tab = "";


var mainApp = angular.module("mainModule", []);

mainApp.controller("product-placement", function($scope) {
	$scope.ppdata = [
		{name: "Амазонка", cost: 171, img: 'images/amazonka.jpg'},
		{name: "Арктика", cost: 90, img: 'images/arktika.png'},
		{name: "Альпы", cost: 130, img: 'images/alps.jpg'},
		{name: "Мёртвое море", cost: 150, img: 'images/Dead-Sea.jpg'},
	];
})

mainApp.controller("formViewer", function($scope, $http) {
	//last_active_tab = 'any-bank-tab';
	
	$scope.formAB = {db: 'any_bank', notSafe: 0};
	$scope.formYB = {db: 'your_bank', notSafe: 0};
	$scope.formPR = {db: 'payment_requests', notSafe: 0};
	var forms = {
		'any_bank_frm': $scope.formAB,
		'your_bank_frm': $scope.formYB,
		'pay_req_frm': $scope.formPR,
	};
	$scope.tabs_visibility = "";
	$scope.form_switcher = "any-bank";
	$scope.response = '';

	$scope.just_pay = function() {
		$scope.tabs_visibility = "";
		$scope.form_switcher = last_active_tab;
	};
	
	$scope.payment_request = function() {
		last_active_tab = $scope.form_switcher;
		$scope.tabs_visibility = "hidden";
		$scope.form_switcher = 'pay-req';
	};
	
	$scope.clear_form = function (fr) {
		frm = forms[fr];
		Object.keys(frm).forEach(function (key) {
			if (key != 'db' && key != 'notSafe') {
				frm[key] = '';
			}
		});
	}

	/*$scope.submit_form = function($event) {
		$scope.clear_form($event.target.name);
	}*/
	
	$scope.submit_form = function($event) {
		$http.post('observer.php', forms[$event.target.name]).then(function(response) {
			if(response.data == 'store: success') {
				$scope.clear_form($event.target.name);
				$scope.response = 'Успешно!';
			} else 
				$scope.response = 'Что-то пошло не так'
			$('#resp').show();
			setTimeout(function(){$('#resp').fadeOut('fast')},5000);
		});
	}
});

mainApp.controller("clientInfo", function($scope) {
	$scope.client_name = "ИП Иванов Владимир Анатольевич";
});

mainApp.controller("captions", function($scope) {
	
	$scope.formAB_cap = {
		id: 'id',
		cardN: 'Номер карты',
		expired: 'Срок действия',
		cvc: 'CVC',
		sum: 'Сумма',
		email: 'Email',
		comment: 'Комментарий',
		notSafe: 'Небезопасный платёж'
	};

	$scope.formYB_cap = {
		id: 'id',
		INN: 'ИНН плательщика',
		BIK: 'БИК',
		accNumber: 'Номер счёта',
		purpose: 'За что',
		sum: 'Сумма',
		notSafe: 'Небезопасный платёж'
	}
	
	$scope.formPR_cap = {
		id: 'id',
		INN: 'ИНН получателя',
		BIK: 'БИК',
		accNumber: 'Номер счёта',
		purpose: 'За что',
		sum: 'Сумма',
		tel: 'Телефон',
		email: 'Email',
		notSafe: 'Небезопасный платёж'
	}
	
});