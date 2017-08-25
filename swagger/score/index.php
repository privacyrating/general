<!DOCTYPE html>
<html>

<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

function secure($str) {
    $str = trim($str);
    $str = stripslashes($str);
    $str = htmlspecialchars($str);
    return $str;
}

function secure_array($array) {
    if ($array === null) return [];
    if (!is_array($array)) return [];

    for ($i = 0; $i < sizeof($array); $i++) {
        $array[$i] = secure($array[$i]);
    }
    return $array;
}

function get_value($name) {
    return (empty($_POST[$name]))? "" : secure($_POST[$name]);
}

function get_array($name) {
    return (empty($_POST[$name]))? [] : secure_array($_POST[$name]);
}

function print_array($arr) {
    for ($i = 0; $i<sizeof($arr); $i++) {
        echo $arr[$i] . "<br>";
    }
}

function handle_form_data() {

    $app = $cluster_id = $clustering_id = $id_group = $chk_group = $predicted = "";
    $app = get_value("app");
    $cluster_id = (int)get_value("cluster_id");
    $clustering_id = (int)get_value("clustering_id");
    $id_group = get_array("id_group");
    $chk_group = get_array("chk_group");
    $predicted = get_array("predicted");

    if (sizeof($id_group) !== sizeof($predicted)) {
        exit("An error occurred ¯\_(ツ)_/¯");
    }

    $mysqli = new mysqli("localhost", "putter", "total_safety", "privacy_ranking");
    if ($mysqli->connect_errno) {
        echo "Failed to connect to database";
    }
    $mysqli->set_charset('utf8');

    for ($i = 0; $i < sizeof($id_group); $i++) {
        $estimate = (in_array($id_group[$i], $chk_group, TRUE))? 1 : 0;

        $stmt = $mysqli->prepare("INSERT INTO Score (cluster_id, clustering_id, app_id, matching_app, predicted, estimate) VALUES (?,?,?,?,?,?);");

        $stmt->bind_param("iissii", $cluster_id, $clustering_id, $id_group[$i], $app, $predicted[$i], $estimate);

        $stmt->execute();

    }

    $mysqli->close();

}

if (!empty($_POST["commit"])) {
    handle_form_data();
}



$mysqli = new mysqli("localhost", "getter", "total_safety", "privacy_ranking");
if ($mysqli->connect_errno) {
    echo "Failed to connect to database";
}
$mysqli->set_charset('utf8');

function get_app_info($app_id) {
    global $mysqli;

    //$res = $mysqli->query("SELECT title, title_en, short_description, icon FROM Apps where App_id = 'com.tinder'");

    $stmt = $mysqli->prepare("SELECT title, title_en, short_description, icon FROM Apps where App_id = ?;");

    $stmt->bind_param("s", $app_id);
    $stmt->execute();
    $res = $stmt->get_result();

    if ($row = $res->fetch_assoc()) {
        return $row;
    }

}


function create_app_view($app_id, $app_id_fit, $match) {
    $app = get_app_info($app_id);

    echo '<div class="app_box">';
        echo '<div class="top_box">';
            echo '<div class="icon_box">';
                echo '<img class="img_icon" src="' . $app["icon"] . '">';
            echo '</div>';
            echo '<div class="title_box">';
                echo '<h3>' . $app["title"] . '</h3>';
                echo '<h4> [ENG] ' . $app["title_en"] . '</h4>';
            echo '</div>';
        echo '</div>';
        echo '<div class="desc_box">';
            echo $app["short_description"];
        echo '</div>';
        echo '<div class="bottom_box">';
            echo '<span class="span_link">';
                echo '<a href="https://play.google.com/store/apps/details?id='.$app_id.'" target="_blank">View on Google Play</a>';
            echo '</span>';

        if ($app_id_fit != null) {
            echo '<span class="span_toggle">';
                echo '<label class="switch">';
                    echo '<input type="hidden" name="id_group[]" value="'.$app_id.'">';
                    echo '<input type="hidden" name="predicted[]" value="'.(int)$match.'">';
                    echo '<input type="checkbox" name="chk_group[]" value="'.$app_id.'">';
                    echo '<div class="slider round"></div>';
                echo '</label>';
            echo '</span>';
        }

        echo '</div>';
    echo '</div>';


}

function get_random_app_from_cluster($cluster) {
    global $mysqli;

    $stmt = $mysqli->prepare("SELECT App_id FROM App_in_cluster WHERE cluster_id = ? AND Clustering_id = ? ORDER BY RAND() LIMIT 0,1");
    $stmt->bind_param("ii", $cluster["Cluster_id"], $cluster["Clustering_id"]);
    $stmt->execute();
    $res = $stmt->get_result();
    if ($row = $res->fetch_assoc()) {
        return $row["App_id"];
    }   

}

function get_apps_for_app($cluster, $app) {
    global $mysqli;

    // Get matching apps
    $stmt = $mysqli->prepare("SELECT App_id, 1 as `match` FROM App_in_cluster WHERE cluster_id = ? AND Clustering_id = ? AND App_id <> ? ORDER BY RAND() LIMIT 0,3");
    $stmt->bind_param("iis", $cluster["Cluster_id"], $cluster["Clustering_id"], $app);
    $stmt->execute();
    $res = $stmt->get_result();
    $rows1 = $res->fetch_all();

    // Get not matching apps
    $stmt = $mysqli->prepare("SELECT App_id, 0 as `match` FROM App_in_cluster WHERE cluster_id <> ? AND Clustering_id = ? ORDER BY RAND() LiMIT 0,3");
    $stmt->bind_param("ii", $cluster["Cluster_id"], $cluster["Clustering_id"]);
    $stmt->execute();
    $res = $stmt->get_result();
    $rows2 = $res->fetch_all();


    $rows = array_merge($rows1, $rows2);
    shuffle($rows);

    return $rows;

}

function get_random_cluster() {
    global $mysqli;

    $stmt = $mysqli->prepare("SELECT Cluster_id, Clustering_id FROM Clusters ORDER BY RAND() LIMIT 0,1");
    $stmt->execute();
    $res = $stmt->get_result();
    if ($row = $res->fetch_assoc()) {
        return $row;
    }
}

?>

<head>
    <title>Score quality of clustering</title>
    <link rel="stylesheet" type="text/css" href="style.css" />
    <meta name="viewport" content="width=device-width, height=device-height, initial-scale=1.0, user-scalable=yes, minimum-scale=1.0">
    <meta charset="utf-8"/>
</head>

<body>

<form action='index.php' method='POST'>

<?php

$cluster = get_random_cluster();
$app = get_random_app_from_cluster($cluster);

//$cluster["Cluster_id"] = 21;
//$cluster["Clustering_id"] = 2;
//$app = "com.live.happy.birthday.wallpaper.pretty.and.cute.wallpapers";

$apps = get_apps_for_app($cluster, $app);

echo '<input type="hidden" name="app" value="'.$app.'">';
echo '<input type="hidden" name="cluster_id" value="'.$cluster["Cluster_id"].'">';
echo '<input type="hidden" name="clustering_id" value="'.$cluster["Clustering_id"].'">';

create_app_view($app, null, false);

echo "<h2>Does this Apps match to the App above?</h2>";

for ($i = 0; $i < sizeof($apps); $i++) {
    create_app_view($apps[$i][0], $app, ($apps[$i][1]==1));
}


?>

<span class="gt">All translations where made with <a href="https://translate.google.com" target="_blank">Google Translator</a>.</span>

<button type="submit" name="commit" value="1">Commit</button>

</form>

</body>

<?php
    $mysqli->close();
?>

</html>
