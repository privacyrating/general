####
# Author: Robert Eichler
####

import mysql.connector as mariadb

clustering_id = 0

"""
Sets clustering id for future cluster insertions

Parameters
----------

cid :: int

"""
def set_clustering_id(cid):
    global clustering_id
    clustering_id = cid
    print(clustering_id)

"""
Connects to database with user putter

Returns
-------
connection

"""
def connect_putter():
    return mariadb.connect(user='putter', password='total_safety', database='privacy_ranking')

"""
Connects to database with user getter

Returns
-------
connection

"""
def connect_getter():
    return mariadb.connect(user='getter', password='total_safety', database='privacy_ranking')

"""
Removes all clusters with previous setted clustering id
"""
def remove_clusters():
    print("removing %d" % clustering_id)
    mariadb_connection = connect_putter()
    dbcursor = mariadb_connection.cursor()
    dbcursor.execute("DELETE FROM App_in_cluster where Clustering_id = %s;", (clustering_id,))
    #mariadb_connection.commit()
    dbcursor.execute("DELETE FROM Clusters where Clustering_id = %s;", (clustering_id,))
    mariadb_connection.commit()
    mariadb_connection.close()

"""
Inserts given clusters with previous setted clustering id into database

Parameters
----------

cluster_ids :: array

"""
def add_clusters(cluster_ids):
    remove_clusters()
    mariadb_connection = connect_putter()
    dbcursor = mariadb_connection.cursor()

    for cid in cluster_ids:
        dbcursor.execute("INSERT INTO Clusters (Cluster_id, Clustering_id, name)\
                            VALUES (%s, %s, %s);",
                            (int(cid), clustering_id, "Cat " + unicode(cid)));

    mariadb_connection.commit()
    mariadb_connection.close()

"""
Inserts apps into cluster with previous setted clustering id into database

Parameters
----------

app_list :: array
    List of all apps to insert

cluster_list :: array
    List of assigned clusters

"""
def add_app_to_cluster(app_list, cluster_list):
    mariadb_connection = connect_putter()
    dbcursor = mariadb_connection.cursor()

    for app, cid in zip(app_list, cluster_list):
        dbcursor.execute("INSERT INTO App_in_cluster (App_id, Clustering_id, cluster_id, similarity)\
                            VALUES (%s, %s, %s, %s)",
                            (str(app), clustering_id, int(cid), 1))

    mariadb_connection.commit()
    mariadb_connection.close()
