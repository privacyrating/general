<?php
/*
Author : Simon Senn
*/

use \Psr\Http\Message\ServerRequestInterface as Request;
use \Psr\Http\Message\ResponseInterface as Response;

require 'vendor/autoload.php';
/*
config für slim
*/


$config['displayErrorDetails'] = true;
$config['addContentLengthHeader'] = false;

/*
database login data
*/

$config['db']['host']   = "localhost";
$config['db']['user']   = "getter";
$config['db']['pass']   = "total_safety";
$config['db']['dbname'] = "privacy_ranking";

$app = new \Slim\App(["settings" => $config]);

/*
connect to  database
*/
$container = $app->getContainer();

$container['db'] = function ($c) {
    $db = $c['settings']['db'];
    $pdo = new PDO("mysql:host=" . $db['host'] . ";dbname=" . $db['dbname'].";charset=utf8",
        $db['user'], $db['pass']);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
    return $pdo;
};


/*
returns name and id off all clusters
*/

$app->get('/cat', function ($response) {

    try
    {

         $sth = $this->db->prepare("SELECT name, Cluster_id FROM Clusters WHERE Clustering_id=0");

        $sth->execute();

        $category = $sth->fetchAll(PDO::FETCH_OBJ);

        if($category) {
            return $this->response->withJson($category, 200);

        } else {
            throw new PDOException('No records found.');
        }

    } catch(PDOException $e) {
          echo '{"error":{"text":'. $e->getMessage() .'}}';
    }
});


/*
returns all cluster id's used for internal testing
*/

$app->get('/cat_helper', function ($response) {

    try
    {

        $sth = $this->db->prepare("SELECT Cluster_id FROM Clusters WHERE Clustering_id=0");

        $sth->execute();

        $category = $sth->fetchAll(PDO::FETCH_OBJ);

        if($category) {
            return $this->response->withJson($category, 200);

        } else {
            throw new PDOException('No records found.');
        }

    } catch(PDOException $e) {
          echo '{"error":{"text":'. $e->getMessage() .'}}';
    }
});




/*
returns all apps in a given cluster sorted by their rating
*/

$app->get('/cat/[{id}]', function ($request, $response, $args) {

    try
    {

        $sth = $this->db->prepare("SELECT title, Apps.App_id, similarity, icon, count(Permission_id) FROM (((Apps NATURAL JOIN App_in_cluster) NATURAL JOIN Clusters) LEFT JOIN App_permissions ON Apps.App_id=App_permissions.App_id) WHERE Clusters.Cluster_id=:id AND Clustering_id=0 GROUP BY Apps.App_id ORDER BY similarity DESC");

	$sth->bindParam("id",$args['id']);

        $sth->execute();

        $category = $sth->fetchAll();

        if($category) {

            return $this->response->withJson($category, 200);

        } else {
            throw new PDOException('No records found.');
        }

    } catch(PDOException $e) {
          echo '{"error":{"text":'. $e->getMessage() .'}}';
    }
});


/*
returns all app_id's used for internal testing
*/
$app->get('/app_helper', function ($response) {

    try
    {

        $sth = $this->db->prepare("SELECT App_id FROM Apps");

        $sth->execute();

        $category = $sth->fetchAll(PDO::FETCH_OBJ);

        if($category) {
            return $this->response->withJson($category, 200);

        } else {
            throw new PDOException('No records found.');
        }

    } catch(PDOException $e) {
          echo '{"error":{"text":'. $e->getMessage() .'}}';
    }
});


/*
returns all information on an given application
*/
$app->get('/app/[{id}]', function ($request, $response, $args) {

    try
    {

        $sth = $this->db->prepare("SELECT *, Count(Permission_id) FROM (Apps LEFT JOIN App_permissions ON Apps.App_id=App_permissions.App_id LEFT JOIN App_in_cluster On Apps.App_id=App_in_cluster.App_id ) WHERE Apps.App_id=:id");

        $sth->bindParam("id",$args['id']);

        $sth->execute();

        $category = $sth->fetch();

        if($category) {

            return $this->response->withJson($category, 200);
        } else {
            throw new PDOException('No records found.');
        }

    } catch(PDOException $e) {
          echo '{"error":{"text":'. $e->getMessage() .'}}';
    }
});

/*
returns all apps matching the search string
*/
$app->get('/search/[{id}]', function ($request, $response, $args) {

    try
    {

        $sth = $this->db->prepare("SELECT title, Apps.App_id, icon, count(Permission_id) FROM (Apps LEFT JOIN App_permissions ON Apps.App_id=App_permissions.App_id) WHERE title like CONCAT('%',:id,'%') GROUP BY Apps.App_id ");

        $sth->bindParam("id",$args['id']);

        $sth->execute();

        $category = $sth->fetchAll();

        if($category) {

            return $this->response->withJson($category, 200);
        } else {
            throw new PDOException('No records found.');
        }

    } catch(PDOException $e) {
          echo '{"error":{"text":'. $e->getMessage() .'}}';
    }
});

/*
returns all permissions a given app uses
*/
$app->get('/perm/[{id}]', function ($request, $response, $args) {

    try
    {

        $sth = $this->db->prepare("SELECT name, Permission_id, weight  FROM Apps NATURAL JOIN App_permissions NATURAL JOIN Permissions  WHERE App_id=:id");

        $sth->bindParam("id",$args['id']);

        $sth->execute();

        $category = $sth->fetchAll();


        if($category) {
            return $this->response->withJson($category, 200);

        } else {
            throw new PDOException('"No Permissions needed."');
        }

    } catch(PDOException $e) {
	  echo '[{"name":'. $e->getMessage() .'}]';
    }
});
/*
returns the number of permissions a given app uses
*/
$app->get('/perm_count/[{id}]', function ($request, $response, $args) {

    try
    {

        $sth = $this->db->prepare("SELECT Count(*)  FROM Apps NATURAL JOIN App_permissions  WHERE App_id=:id");

        $sth->bindParam("id",$args['id']);

        $sth->execute();

        $category = $sth->fetchAll();

        if($category) {
            return $this->response->withJson($category, 200);

        } else {
            throw new PDOException('0');
        }

    } catch(PDOException $e) {
          echo '[{"Count(*)":'. $e->getMessage() .'}]';
    }

});



$app->run();


?>
