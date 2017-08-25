<?php
$servername = "localhost";
$username = "getter";
$password = "total_safety";
$dbname = "privacy_ranking";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}


$sql = "SELECT name FROM Clusters WHERE Clustering_id=0";

$result = $conn->query($sql);

$outp = array();


while($row=$result->fetch_assoc()){
	$outp[] = $row;
	}
echo json_encode($outp);

$conn->close();
?>
