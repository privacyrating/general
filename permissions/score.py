####
# Author: Robert Eichler
####

# Used to calculate the badness for each app

import mysql.connector as mariadb
from sklearn.cluster import KMeans
import numpy as np

"""
red 0 degree - 29 degree
yellow 30 degree - 79 degree
green 80 degree - 120 degree
"""
# color ranges in percent
colors = {"green": [66.6, 100.0],
            "yellow": [25.0, 65.83],
            "red": [0.0, 24.16]}

"""
Get all permissions from given cluster and the calculated wheight

Parameters
----------

dbcursor :: cursor

cid :: int
    Cluster ID

cing_id :: int
    Cluster ID

Returns
-------
permissions :: Dict{permission ID => weight}

"""
def get_perm_in_cluster(dbcursor, cid, cing_id):
    # Get permissions with weight
    dbcursor.execute("SELECT DISTINCT App_permissions.Permission_id, \
                        Permissions.weight \
                        FROM App_in_cluster NATURAL JOIN App_permissions \
                        NATURAL JOIN Permissions \
                        WHERE App_in_cluster.Clustering_id = %s AND \
                        App_in_cluster.cluster_id = %s \
                        ORDER BY App_permissions.Permission_id;", (cing_id, cid))

    perms = dbcursor.fetchall()

    # Get frequenzy of permission
    dbcursor.execute("select permission_id, \
                        (cnt / countAppsInCluster(cluster_id,clustering_id)) as p \
                        from Count_permissions_View \
                        where clustering_id = %s and cluster_id = %s \
                        order by permission_id;", (cing_id, cid))

    perms_p = dbcursor.fetchall()

    values = dict()

    # Calculate weight
    for i in range(len(perms)):
        values[perms[i][0]] = float(perms[i][1]) * (1.0 - float(perms_p[i][1]))

    return values

"""
Calculate the percentage distribution for all apps in a group

Parameters
----------

app_values :: array
    App values

labels :: array
    List of assigned labels

label :: int
    Group label

color_range :: [int, int]
    The range for coloring the group [min, max]

Returns
-------
values :: array

"""
def calc_percentages(app_values, labels, label, color_range):
    f = lambda x: x == label
    tmp = map(f, labels)
    indices = np.where(tmp)[0]

    filtered_apps = np.array(app_values)[indices]

    min_value = min(filtered_apps)
    max_value = max(filtered_apps)

    for i in range(len(app_values)):
        if labels[i] != label:
            continue
        if min_value == max_value:
            app_values[i] = color_range[1]
            continue

        # 0 - 100
        value = 100 - ((app_values[i] - min_value) * 100.0) / (max_value - min_value)

        # min_range - max_range
        value = (value * (color_range[1] - color_range[0]) / 100) + color_range[0]

        app_values[i] = value

    return app_values

"""
Updates the badness of given apps in database

Parameters
----------

app_ids :: array
    List of apps to update

app_values :: array
    List of values

cid :: int
    Cluster ID

cing_id :: int
    Clustering ID

"""
def updating_apps(app_ids, app_values, cid, cing_id):
    mariadb_connection = mariadb.connect(user='putter', password='total_safety', database='privacy_ranking')
    dbcursor = mariadb_connection.cursor()

    for i in range(len(app_ids)):
        dbcursor.execute("UPDATE App_in_cluster set similarity = %s WHERE App_id = %s \
                            AND Clustering_id = %s AND cluster_id = %s",
                            (float(app_values[i]), app_ids[i], cing_id, cid))

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
    # 1 Collecting all permission within a cluster
    # 2 Calculation of permission weight
    perm_in_c = get_perm_in_cluster(dbcursor, cid, cing_id)

    # 3 Filling the matrix
    dbcursor.execute("SELECT App_in_cluster.App_id, App_permissions.Permission_id \
                        FROM App_in_cluster LEFT JOIN App_permissions \
                        ON App_in_cluster.App_id = App_permissions.App_id \
                        WHERE App_in_cluster.Clustering_id = %s \
                        AND App_in_cluster.cluster_id = %s;", (cing_id, cid))

    apps = {}

    for app, permission in dbcursor:
        perms = apps.get(app, [])
        if (permission == None):
            perms.append(0)
        else:
            perms.append(perm_in_c[permission])

        apps[app] = perms

    # 4 Calculating the summary of the badness
    for app in apps:
        value = sum(apps[app])
        apps[app] = value

    # 5 Grouping the apps
    app_ids = []
    app_values = []
    for app in apps:
        app_ids.append(app)
        app_values.append(apps[app])

    X = map(lambda x: [x], app_values)

    km = KMeans(n_clusters=3)
    km.fit(X)

    labels = km.labels_
    centroids = km.cluster_centers_

    nlabels = len(np.unique(labels))
    ncentroids = len(centroids)

    min_c = min(centroids)
    max_c = max(centroids)

    for label in np.unique(labels):
        color = "green" if (centroids[label] == min_c) else "red" if (centroids[label] == max_c and nlabels == ncentroids) else "yellow"
        app_values = calc_percentages(app_values, labels, label, colors[color])


    updating_apps(app_ids, app_values, cid, cing_id)

mariadb_connection = mariadb.connect(user='getter', password='total_safety',
                                        database='privacy_ranking')
dbcursor = mariadb_connection.cursor()

dbcursor.execute("SELECT Cluster_id, Clustering_id from Clusters where Clustering_id = 0;")

clusters = dbcursor.fetchall()

for cluster in clusters:
    print(cluster)
    run(dbcursor, cluster[0], cluster[1])

mariadb_connection.close()
