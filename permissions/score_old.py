####
# Author: Robert Eichler
####

# Used to calculate the badness for each app (old algorithm)

import mysql.connector as mariadb

"""
Get all permissions from given cluster

Parameters
----------

dbcursor :: cursor

cid :: int
    Cluster ID

cing_id :: int
    Cluster ID

Returns
-------
permissions :: array

"""
def get_perm_in_cluster(dbcursor, cid, cing_id):
    dbcursor.execute("SELECT DISTINCT App_permissions.Permission_id \
                    FROM App_in_cluster NATURAL JOIN App_permissions \
                    WHERE App_in_cluster.Clustering_id = %s AND App_in_cluster.cluster_id = %s \
                    ORDER BY App_permissions.Permission_id;", (cing_id, cid))

    return map(lambda x: x[0],dbcursor.fetchall())

"""
Get the average permissions (those which are needed by more than the halve of apps) from given cluster

Parameters
----------

dbcursor :: cursor

cid :: int
    Cluster ID

cing_id :: int
    Clustering ID

Returns
-------
permissions :: array

"""
def get_avg_in_cluster(dbcursor, cid, cing_id):
    dbcursor.execute("SELECT clustering_id, cluster_id, permission_id, cnt \
                        FROM Count_permissions_View \
                        WHERE cnt >= (countAppsInCluster(cluster_id, clustering_id)/2) \
                        AND clustering_id = %s AND cluster_id = %s;", (cing_id, cid))

    return map(lambda x: x[2],dbcursor.fetchall())

"""
Updates the badness of given apps in database

Parameters
----------

apps :: Dict{app ID => value}
    Dict of apps and values to update

cid :: int
    Cluster ID

cing_id :: int
    Clustering ID

"""
def updating_apps(apps, cid, cing_id):
    mariadb_connection = mariadb.connect(user='putter', password='total_safety', database='privacy_ranking')
    dbcursor = mariadb_connection.cursor()

    for app in apps:
        dbcursor.execute("UPDATE App_in_cluster set similarity = %s WHERE App_id = %s \
                            AND Clustering_id = %s AND cluster_id = %s", (apps[app], app, cing_id, cid))

    mariadb_connection.commit()
    mariadb_connection.close()

"""
Calculates the badness for all apps of given cluster

Parameters
----------

dbcursor :: cursor

cid :: int
    Cluster ID

cing_id :: int
    Clustering ID

"""
def run(dbcursor, cid, cing_id):
    # 1 Collecting all Permission within cluster
    perm_in_c = get_perm_in_cluster(dbcursor, cid, cing_id)

    # 2 Collecting the average Permissions
    avg_in_c = get_avg_in_cluster(dbcursor, cid, cing_id)

    # 3 Collecting apps and their permissions
    dbcursor.execute("SELECT App_in_cluster.App_id, App_permissions.Permission_id \
                        FROM App_in_cluster LEFT JOIN App_permissions \
                        ON App_in_cluster.App_id = App_permissions.App_id \
                        WHERE App_in_cluster.Clustering_id = %s AND App_in_cluster.cluster_id = %s;", (cing_id,cid))

    apps = {};

    for app, permission in dbcursor:
        perms = apps.get(app, [])
        if (permission == None):
            perms.append(0)
        else:
            # 4 Reducing the badness of the average permissions
            perms.append(0.5 if (permission in avg_in_c) else 1.0)

        apps[app] = perms


    max_value = len(perm_in_c) * 1.0

    min_value = max_value

    # 5 Calculate the summary of the badness
    for app in apps:
        value = sum(apps[app])
        min_value = min(value, min_value)
        apps[app] = value

    min_value *= 1.0

    # 6 Calculating the percantage of badness
    for app in apps:
        value = 100 - ((apps[app] - min_value) * 100.0) / (max_value - min_value)
        apps[app] = value

    updating_apps(apps, cid, cing_id)


mariadb_connection = mariadb.connect(user='getter', password='total_safety', database='privacy_ranking')
dbcursor = mariadb_connection.cursor()

dbcursor.execute("SELECT Cluster_id, Clustering_id from Clusters;")

clusters = dbcursor.fetchall()

for cluster in clusters:
    print(cluster)
    run(dbcursor, cluster[0], cluster[1])

mariadb_connection.close()



'''
SELECT App_in_cluster.App_id, App_permissions.Permission_id
FROM App_in_cluster LEFT JOIN App_permissions
ON App_in_cluster.App_id = App_permissions.App_id
WHERE App_in_cluster.Clustering_id = 0 AND App_in_cluster.cluster_id = 24
AND App_in_cluster.App_id = "com.lge.wsdeveloper.retrodark";
'''
