----
-- Author: Robert Eichler
----

-- Creating the database
CREATE DATABASE IF NOT EXISTS privacy_ranking
    DEFAULT CHARACTER SET utf8
    DEFAULT COLLATE utf8_general_ci;

-- Creating users
DROP USER 'putter'@'localhost';
CREATE USER 'putter'@'localhost'
    IDENTIFIED BY 'total_safety';
GRANT INSERT ON privacy_ranking.* TO 'putter'@'localhost';
GRANT UPDATE ON privacy_ranking.* TO 'putter'@'localhost';
GRANT DELETE ON privacy_ranking.* TO 'putter'@'localhost';
GRANT SELECT (App_id, Clustering_id, cluster_id) ON App_in_cluster TO putter@localhost;
GRANT EXECUTE ON FUNCTION countAppsInCluster TO getter@localhost;


DROP USER 'getter'@'localhost';
CREATE USER 'getter'@'localhost'
    IDENTIFIED BY 'total_safety';
GRANT SELECT ON privacy_ranking.* TO 'getter'@'localhost';

-- Passwod change: SET PASSWORD = PASSWORD('mypass');

USE privacy_ranking;

-- Creating the tables
CREATE TABLE IF NOT EXISTS Developers (
    Developer_id varchar(255) NOT NULL,
    name varchar(255) NOT NULL,
    PRIMARY KEY (Developer_id)
);

CREATE TABLE IF NOT EXISTS Categories (
    Category_id varchar(255) NOT NULL,
    name varchar(20) NOT NULL,
    PRIMARY KEY (Category_id)
);

CREATE TABLE IF NOT EXISTS Apps (
    App_id varchar(255) NOT NULL,
    title varchar(255) NOT NULL,
    title_en varchar(255) NOT NULL,
    developer_id varchar(255) NOT NULL,
    description text NOT NULL,
    short_description tinytext NOT NULL,
    rating float NOT NULL,
    min_downloads int NOT NULL,
    max_downloads int NOT NULL,
    reviews int NOT NULL,
    cost int NOT NULL,
    currency varchar(5) NOT NULL,
    icon varchar(400),
    app_category varchar(255) NOT NULL,
    version varchar(20),
    min_android varchar(5),
    changelog text NOT NULL,
    PRIMARY KEY (App_id),
    FOREIGN KEY (developer_id) REFERENCES Developers(Developer_id),
    FOREIGN KEY (app_category) REFERENCES Categories(Category_id)
);

CREATE TABLE IF NOT EXISTS Permissions (
    Permission_id INT NOT NULL,
    `name` VARCHAR(100),
    PRIMARY KEY (Permission_id)
);

-- alter table Permissions add weight float default 1.0;

CREATE TABLE IF NOT EXISTS App_permissions (
    App_id VARCHAR(255) NOT NULL,
    Permission_id INT NOT NULL,
    PRIMARY KEY (App_id, Permission_id),
    FOREIGN KEY (App_id) REFERENCES Apps(App_id),
    FOREIGN KEY (Permission_id) REFERENCES Permissions(Permission_id)
);

CREATE TABLE IF NOT EXISTS Images (
    Image_id INT NOT NULL AUTO_INCREMENT,
    app_id VARCHAR(255) NOT NULL,
    url VARCHAR(400) NOT NULL,
    PRIMARY KEY (Image_id),
    FOREIGN KEY (app_id) REFERENCES Apps(App_id)
);

CREATE TABLE IF NOT EXISTS Clusters (
    Cluster_id INT NOT NULL,
    Clustering_id INT NOT NULL,
    `name` VARCHAR(100),
    PRIMARY KEY (Cluster_id, Clustering_id)
);

CREATE TABLE IF NOT EXISTS App_in_cluster (
    App_id VARCHAR(255) NOT NULL,
    Clustering_id INT NOT NULL,
    cluster_id INT NOT NULL,
    similarity FLOAT NOT NULL,
    PRIMARY KEY (App_id, Clustering_id),
    FOREIGN KEY (cluster_id, Clustering_id) REFERENCES Clusters(Cluster_id, Clustering_id)
);


CREATE TABLE IF NOT EXISTS Score (
    Score_id INT NOT NULL AUTO_INCREMENT,
    cluster_id INT NOT NULL,
    clustering_id INT NOT NULL,
    app_id VARCHAR(255) NOT NULL,
    matching_app VARCHAR(255) NOT NULL,
    predicted INT(1) NOT NULL,
    estimate INT(1) NOT NULL,
    PRIMARY KEY (Score_id),
    FOREIGN KEY (cluster_id, clustering_id) REFERENCES Clusters(Cluster_id, Clustering_id),
    FOREIGN KEY (app_id) REFERENCES Apps(App_id),
    FOREIGN KEY (matching_app) REFERENCES Apps(App_id)
);


SOURCE permissions.sql
SOURCE other_permissions.sql


DELIMITER $$
DROP FUNCTION IF EXISTS countAppsInCluster$$
CREATE FUNCTION countAppsInCluster( c_id INT, cing_id INT )
RETURNS INT DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE cnt INT;
    SELECT count(App_id) INTO cnt FROM App_in_cluster WHERE cluster_id = c_id AND Clustering_id = cing_id;
    RETURN cnt;
END$$
DELIMITER ;


DROP VIEW IF EXISTS Count_permissions_View;
CREATE VIEW Count_permissions_View AS
SELECT App_in_cluster.Clustering_id as clustering_id, App_in_cluster.cluster_id,
App_permissions.Permission_id as permission_id, count(Apps.App_id) as cnt
FROM App_permissions NATURAL JOIN Apps
NATURAL JOIN App_in_cluster
GROUP BY App_in_cluster.Clustering_id, App_in_cluster.cluster_id, App_permissions.Permission_id
ORDER BY App_in_cluster.Clustering_id, App_in_cluster.cluster_id, App_permissions.Permission_id;


--SELECT clustering_id, cluster_id, permission_id, cnt
--FROM Count_permissions_View
--WHERE cnt = (countAppsInCluster(cluster_id, clustering_id))
--AND clustering_id = 0;

--SELECT clustering_id, cluster_id, permission_id, cnt
--FROM Count_permissions_View
--WHERE cnt = (countAppsInCluster(cluster_id, clustering_id)/2)
--AND clustering_id = 0;

