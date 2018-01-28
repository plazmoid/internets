<?
require_once('api.php');

try {
	$api = new API();
	$api->processing();
} catch (Exception $e) {
	echo $e;
}

if($api->getAdmin()) {
	
$captions = array(
	'any_bank' => array('formAB_cap', 'Платежи с карт любых банков'),
	'your_bank' => array('formYB_cap', 'Платежи со своего банка'),
	'payment_requests' => array('formPR_cap', 'Запросы платежей')
);

$currform = $captions[$_SESSION['form']];
header('Content-type:text/html; charset=utf-8');
?>
<html>
<head>
	<title>Админ-панель</title>
	<link rel="stylesheet" type="text/css" href="css/payments.css">
	<link rel="stylesheet" type="text/css" href="css/observer.css">
	<script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.6.4/angular.min.js"></script>
	<script type="text/javascript" src="js/angular_content.js"></script>
	<meta name="viewport" content="width=device-width, initial-scale=1">
</head>

<body ng-app="mainModule" ng-controller="captions">
	<div id="head_panel">
		<div id='head_container'>
			<div class='login_forms' style="padding-top:7px;">
				<a href="/">Главная</a>
			</div>
		</div>
	</div>
	<div class="breadcrumb">
		<ul>
		  <li><a href="observer.php?form=any_bank">Платежи с карт любых банков</a></li>
		  <li><a href="observer.php?form=your_bank">Платежи со своего банка</a></li>
		  <li><a href="observer.php?form=payment_requests">Запросы платежей</a></li>
		</ul>
	</div>
	<div class="mainblock">
		<div class="container">
			<div class="header">
			<? echo	"<p>{$currform[1]}</p>";?>
			</div>
			<table>
			<? echo "<th ng-repeat='cap in {$currform[0]}'>{{cap}}</th>";
				while ($row = mysqli_fetch_assoc($api->form)) {
					echo '<tr>';
					foreach ($row as $key => $val) {
						echo '<td>'.$val.'</td>';
					}
					echo "<td><input type='checkbox' form='notSafeFrm' name='nsf-{$row['id']}'></td>";
					echo '</tr>';
				}
			?>
			</table>
			<form id='notSafeFrm' style="float:right;" action="observer.php" method='post'>
				<input type='radio' value='ns' name='notSafe' id='ns' checked>
				<label for='ns'>Небезопасный</label>
				<input type='radio' value='safe' name='notSafe' id='s'>
				<label for='s'>Безопасный</label>
				<input type='submit' value='Пометить'>
			</form>
			<form id='sort' action='observer.php'>
				<select name='sort' form='sort'>
				<? echo "<option value='{{key}}' ng-repeat='(key, val) in {$currform[0]}'>{{val}}</option>";?>
				</select>
				<br>
				<input type='radio' value='asc' name='sortdir' id='asc' checked>
				<label for='asc'>По возрастанию</label>
				<input type='radio' value='desc' name='sortdir' id='desc'>
				<label for='desc'>По убыванию</label>
				<br><br>
				<input type='submit' value='Сортировать'>
			</form>
		</div>
	</div>
</body>
</html>
<?}?>
