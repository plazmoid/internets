<?
require_once('db.php');

class API {
	public $db;
	private $form;
	private $method;
	private $isAdmin = false;
	
	public $captions = array(
		'any_bank' => array('formAB_cap', 'Платежи с карт любых банков'),
		'your_bank' => array('formYB_cap', 'Платежи со своего банка'),
		'payment_requests' => array('formPR_cap', 'Запросы платежей')
	);
	
	public function __construct() {
		session_start();
		$this->db = new DataBase();
		$this->method = $_SERVER['REQUEST_METHOD'];
		$this->isAdmin = isset($_SESSION['admin']);
	}
	
	public function goAway() {
		header('Location: /');//. $_SERVER['HTTP_ORIGIN']);
	}
	
	public function getAdmin() {
		return $this->isAdmin;
	}
	
	public function getForm() {
		return $this->form;
	}
	
	public function fetchFormSorted($sfield, $sdir) {
		$this->fetchForm($_SESSION['form'], "ORDER BY ".$sfield.' '.$sdir);
	}

	public function fetchForm($form, $q='') {
		if (!in_array($form, array_keys($this->captions))) {
			$form = $_SESSION['form'];
		}
		if(!$this->form = $this->db->query("SELECT * FROM ".implode(' ', array($form, $q))))
			$this->defaultForm();
		else
			$_SESSION['form'] = $form;
	}

	private function setAdmin($b) {
		$this->isAdmin = $b;
		if($b) {
			$_SESSION['admin'] = 1;
			echo '1';
		} else {
			session_destroy();
			$this->goAway();
		}
	}

	private function passchecking() {
		$this->passhash = md5($this->GET_param('h').'a_bit_of_salt');
		#$this->check = $this->db->query("SELECT * FROM users WHERE username='admin' AND password='{$this->passhash}'");
		#if($this->db->qcount($this->check))
		if ($this->passhash === '427cbfae21985190d3bbb58a15837594') #пароль: 'не угадаешь'
			$this->setAdmin(true);
	}
	
	public function updateNotSafe() {
		if (!$notSafe = $_POST['notSafe'] === 'ns' ? 'TRUE':'FALSE')
			return;
		foreach ($_POST as $key => $val) {
			if ($key !== 'notSafe') {
				$key = explode("-", $key);
				$this->db->query("UPDATE {$_SESSION['form']} SET notSafe={$notSafe} WHERE id={$key[1]}");
			}
		}
		$this->fetchForm($_SESSION['form']);
	}

	public function GET_param($key) {
		if(!isset($_GET[$key]))
			return false;
		else
			return htmlspecialchars($_GET[$key]);
	}
	
	public function defaultForm() {
		if (isset($_SESSION['form']))
			$this->fetchForm($_SESSION['form']);
		else
			$this->fetchForm('any_bank');
	}

	public function processing() {
		switch($this->method) {
			case 'POST':
				if(count($_POST) !== 0) {
					$this->updateNotSafe();
				} else {
					if ($json = file_get_contents('php://input')) {
						$this->storePayment($json);
						exit();
					} else
						$this->defaultForm();
				}
				break;
			case 'GET':
				if($this->isAdmin) {
					if (!count($_GET)) {
						$this->defaultForm();
					} else {
						if ($this->GET_param('q') === 'exit') {
							$this->setAdmin(false);
						} elseif ($this->GET_param('form')) {
							$this->fetchForm($this->GET_param('form'));
						} elseif ($this->GET_param('sort'))
							$this->fetchFormSorted($this->GET_param('sort'), $this->GET_param('sortdir'));
					}
				} else {
					if ($this->GET_param('h')) {
						$this->passchecking();
					} else
						$this->goAway();
					exit();
				}
				break;
		}
	}

	public function storePayment($data) {
		$this->data = json_decode($data, true);
		$this->table = array_shift($this->data);
		$this->str_keys = implode(',', array_keys($this->data));
		$this->str_vals = '';
		foreach (array_values($this->data) as $val) {
			$this->str_vals .= "'".stripslashes(htmlspecialchars(str_replace("'",'', $val)))."',";
		}
		$this->str_vals = substr($this->str_vals, 0, -1);
		if($this->db->query("INSERT INTO {$this->table} ({$this->str_keys}) VALUES ({$this->str_vals})"))
			echo 'store: success';
		else
			echo 'store: fail';
	}
}
?>