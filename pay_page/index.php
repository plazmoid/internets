<?
	session_start();
	header('Content-type:text/html; charset=utf-8');
?>
<!DOCTYPE html>
<html>
<head>
	<title>Заплатить</title>
	<link rel="stylesheet" type="text/css" href="css/payments.css">
	<link rel="shortcut icon" href="images/favicon.ico">
	<script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.6.4/angular.min.js"></script>
	<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
	<script type="text/javascript" src="js/angular_content.js"></script>
	<script type="text/javascript" src="js/admin_entry.js"></script>
	<meta name="viewport" content="width=device-width, initial-scale=1">
</head>

<body ng-app="mainModule">
<div id="head_panel">
	<div id='head_container'>
		<div class='login_forms'>
		<? if(isset($_SESSION['admin'])) {?>
			<a href='observer.php'>Панель обменистратора</a>
			<a href='observer.php?q=exit'>(Выйти)</a>
		<?} else {?>
			<div id='show-login'>Панель обменистратора</div>
		<?}?>
		</div>
		<div class='login_forms'>
			<form style='display:none' id='login'>
				<input type='password' id='admin-pass' placeholder='Введите пароль'>
				<input type='submit' onclick='validate_pwd()' value='OK'>
			</form>
		</div>
		<div class='login_forms' id='response'></div>
	</div>
</div>
<div class="mainblock" id="mainblock-client" ng-controller="clientInfo">
	<div class="container">
		<div class="header">
			<p>О клиенте</p>
		</div>
		<div id="info" style="float: left">
			<div class="name">{{client_name}}</div>
			<div class="contacts">
				<p id="tel">+79126543210</p>
				<a href="foo@bar.dot" id="email">foo@bar.dot</a>
			</div>
		</div>
		<img style="max-width: 120px; width:20%" src="images\logo.png">
	</div>
</div>

<div class="mainblock" id="mainblock-payment" ng-controller="captions">
	<div class="container" ng-switch="form_switcher" ng-controller="formViewer">
		<div class="header">
			<p>Платежи</p>
		</div>
		<div class="tabs">
			<span class="tab-link" id="pay-tab" ng-click="just_pay()">Заплатить</span>
			<span class="tab-link" id="payment-request-tab" ng-click="payment_request()">Запросить платёж</span>
		</div>
		<div class="tabs" id="payment-tabs" ng-class="tabs_visibility">
			<span class="tab-link as-button" id="any-bank-tab" ng-class='{"active-tab": form_switcher == "any-bank"}' ng-click="form_switcher='any-bank'">С карты любого банка</span>
			<span class="tab-link as-button" id="your-bank-tab" ng-class='{"active-tab": form_switcher == "your-bank"}' ng-click="form_switcher='your-bank'">Из интернет-банка</span>
		</div>
		<form name="any_bank_frm" class="bank-form" id="any-bank" ng-submit="submit_form($event)" ng-switch-when="any-bank" novalidate>
			<div id="card">
				<img style="max-width: 150px; float:right; margin:2px;" src="images\visa-mastercard.png">
				<input type="text" id="card-number" class="input-field card-input" required ng-model="formAB.cardN" placeholder={{formAB_cap.cardN}} ng-pattern="/^\d{16}$/">
				<input type="text" id="date-expired" class="input-field card-input" required ng-model="formAB.expired" placeholder="ММ/ГГ" ng-pattern="/^(0[1-9]|1[0-2])/(1[7-9]|2[0-9]|3[0-7])$/">
				<input type="text" id="cvc" class="input-field card-input" required ng-model="formAB.cvc" placeholder={{formAB_cap.cvc}} ng-pattern="/^\d{3}$/">
			</div>
			<div id="pay-data">
				<div class="labeled-field">
					<p>{{formAB_cap.sum}}</p>
					<input type="text" class="input-field" required ng-model="formAB.sum" placeholder="От 1000 до 75000 р." ng-pattern="/^([1-9][0-9]{3}|[1-6][0-9]{4}|7[0-4][0-9]{3}|75000)$/">
				</div>
				<div class="labeled-field">
					<p>{{formAB_cap.email}}</p>
					<input type="email" class="input-field" required ng-model="formAB.email" placeholder="Для квитанций об оплате">
				</div>
				<div class="labeled-field" id="comments">
					<p>{{formAB_cap.comment}}</p>
					<textarea rows="4" form="any_bank_frm" class="input-field" ng-model="formAB.comment" placeholder="До 150 символов" ng-maxlength="150"></textarea>
				</div>
			</div>
			<br>
			<input type="submit" value="Заплатить" ng-disabled="any_bank_frm.$invalid" ng-click="any_bank_frm.$setPristine()">
		</form>

		<form name="your_bank_frm" class="bank-form" id="your-bank" ng-submit="submit_form($event)" ng-switch-when="your-bank">
			<h3>Сформируйте платёжку и загрузите её в свой банк для подписи</h3>
			<div class="labeled-field yr_bank">
				<div class="wide-label"><span>{{formYB_cap.INN}}</span></div>
				<input type="text" class="input-field" placeholder="10 или 12 цифр" required ng-model="formYB.INN" ng-pattern="/^([0-9]{10}|[0-9]{12})$/">
			</div>
			<div class="labeled-field yr_bank">
				<div class="wide-label"><span>{{formYB_cap.BIK}}</span></div>
				<input type="text" class="input-field" placeholder="9 цифр" required ng-model="formYB.BIK" ng-pattern="/^[0-9]{9}$/">
			</div>
			<div class="labeled-field yr_bank">
				<div class="wide-label"><span>{{formYB_cap.accNumber}}</span></div>
				<input type="text" class="input-field" placeholder="20 цифр" required ng-model="formYB.accNumber" ng-pattern='/^[0-9]{20}$/'>
			</div>
			<div class="labeled-field yr_bank">
				<div class="wide-label"><span>{{formYB_cap.purpose}}</span></div>
				<input type="text" class="input-field" placeholder="" ng-model="formYB.purpose">
			</div>
			<div class="labeled-field yr_bank">
				<div class="wide-label"><span>{{formYB_cap.sum}}</span></div>
				<input type="text" class="input-field" placeholder="От 1000 до 75000 р." required ng-model="formYB.sum" ng-pattern="/^([1-9][0-9]{3}|[1-6][0-9]{4}|7[0-4][0-9]{3}|75000)$/">
			</div>
			<input type="submit" ng-disabled="your_bank_frm.$invalid" value="Получить файл для интернет-банка" ng-click="your_bank_frm.$setPristine()">
		</form>

		<form name="pay_req_frm" class="bank-form" id="pay-req" ng-submit="submit_form($event)" ng-switch-when="pay-req" ng-controller="clientInfo">
			<h3>Создайте платёжку, а {{client_name}} подпишет её у себя в интернет-банке</h3>
			<div class="labeled-field yr_bank">
				<div class="wide-label"><span>{{formPR_cap.INN}}</span></div>
				<input type="text" class="input-field" placeholder="10 или 12 цифр" required ng-model="formPR.INN" ng-pattern="/^([0-9]{10}|[0-9]{12})$/">
			</div>
			<div class="labeled-field yr_bank">
				<div class="wide-label"><span>{{formPR_cap.BIK}}</span></div>
				<input type="text" class="input-field" placeholder="9 цифр" required ng-model="formPR.BIK" ng-pattern="/^[0-9]{9}$/">
			</div>
			<div class="labeled-field yr_bank">
				<div class="wide-label"><span>{{formPR_cap.accNumber}}</span></div>			
				<input type="text" class="input-field" placeholder="20 цифр" required ng-model="formPR.accNumber" ng-pattern='/^[0-9]{20}$/'>
			</div>
			<div class="labeled-field yr_bank">
				<div class="wide-label"><span>{{formPR_cap.purpose}}</span></div>
				<input type="text" class="input-field" placeholder="Назначение платежа" required ng-model="formPR.purpose">
			</div>
			<div class="labeled-field yr_bank">
				<div class="wide-label"><span>{{formPR_cap.sum}}</span></div>
				<input type="text" class="input-field" placeholder="От 1000 до 75000 р." required ng-model="formPR.sum">
			</div>
			<div class="labeled-field yr_bank">
				<div class="wide-label"><span>{{formPR_cap.tel}}</span></div>
				<input type="text" class="input-field" placeholder="" required ng-model="formPR.tel" ng-pattern='/^[0-9]{11}$/'>
			</div>
			<div class="labeled-field yr_bank">
				<div class="wide-label"><span>{{formPR_cap.email}}</span></div>
				<input type="email" class="input-field" placeholder="Для уведомлений об оплате" required ng-model="formPR.email">
			</div>
			<input type="submit" ng-disabled="pay_req_frm.$invalid" value="Создать платёж" ng-click="pay_req_frm.$setPristine()">
		</form>
		<div id='resp' style='font-size: 18px;'>{{response}}</div>
	</div>
</div>

<div class="mainblock" id="mainblock-about">
	<div class="container">
		<div class="header">
			<p>О компании</p>
		</div>
		<span id="client-info">ИП Иванов Владимир Анатольевич с 2015 года
		ничего не производит, но получает деньги буквально из воздуха.
		Всё просто: он продаёт воздух. Альпийский,
		арктический или тропический - всё, что вашему носу будет желанно, будет
		бережно собрано из прямых источников и доставлено в ближайшие сроки.
		</span>
		<div class="product-placement" ng-controller="product-placement">
			<div class="product" ng-repeat="product in ppdata">
				<h2 class="product-caption">{{product.name}}</h2>
				<p class="product-price">{{product.cost}} руб/м<sup>3</sup></p>
				<img src={{product.img}} style="max-width: 500px; width: 100%; height: 250px">
			</div>
		</div>
	</div>
</div>

<footer>
	<ul id="footer-content">
		<li>Сидоренко Артём 2017-2018 ©</li>
		<li><a href="https://vk.com/gigaoctet"><img src="images/vk.png" width="15" height="15"></a></li>
	</ul>
</footer>
</body>