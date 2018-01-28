<?
class DataBase {
	public $connection;
	
	public function __construct() {
		$this->connection = mysqli_connect('localhost', 'root', '', 'payments');
		if (!$this->connection) {
			die("Connection failed: " . mysqli_connect_error());
		}
	}
	
	public function query($q) {
		$this->query_result = mysqli_query($this->connection, $q);
		if (!$this->query_result) {
			echo('Query failed: ' . mysqli_error($this->connection));
		}
		return $this->query_result;
	}
	
	public function qcount($q) {
		return mysqli_num_rows($q);
	}

	public function __destruct() {
		mysqli_close($this->connection);
	}
}
?>